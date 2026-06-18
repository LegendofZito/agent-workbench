#!/usr/bin/env python3
"""Minimal dependency-free stdio MCP server for Agent Workbench.

Exposes ONE tool — `delegate_local` — that runs a bounded subtask on a local
Ollama model with a real tool-use loop (run_shell / read_file / write_file /
list_dir / web_fetch). The driving cloud agent (Opus/Sonnet) calls this to
offload cheap, mechanical, easily-verified work to a FREE local LLM instead of
spending tokens on a paid sub-agent.

Protocol: JSON-RPC 2.0 over stdio, newline-delimited (MCP stdio transport).
stdout is the JSON-RPC channel ONLY; all logging goes to stderr.
"""
import sys, os, json, re, subprocess, urllib.request, urllib.error

OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
DEFAULT_MODEL = os.environ.get("DELEGATE_MODEL", "qwen3:8b")
PROTO_DEFAULT = "2024-11-05"
MAX_STEPS = 12
TOOL_NAMES = {"run_shell", "read_file", "write_file", "list_dir", "web_fetch"}

LOCAL_TOOLS = [
    {"type": "function", "function": {"name": "run_shell",
     "description": "Run a bash command on the local Fedora machine; returns combined stdout+stderr.",
     "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "read_file",
     "description": "Read and return a file's contents.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file",
     "description": "Create or overwrite a file with text content.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "list_dir",
     "description": "List entries in a directory.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}}},
    {"type": "function", "function": {"name": "web_fetch",
     "description": "HTTP GET a URL and return up to ~8000 chars of the body.",
     "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
]

SYSTEM = (
    "You are a fast local helper model executing a single delegated subtask on the "
    "user's Fedora Linux machine, on behalf of a larger agent. You are NOT sandboxed "
    "and have REAL tools: run_shell, read_file, write_file, list_dir, web_fetch. Use "
    "them to actually do the task — never claim you lack access. Work one step at a "
    "time, then finish with a SHORT plain-text result the calling agent can use. When "
    "done, reply with the result and NO tool call."
)


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def ollama_chat(model, messages):
    body = json.dumps({"model": model, "messages": messages, "tools": LOCAL_TOOLS, "stream": False}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/chat", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read().decode("utf-8")).get("message") or {}


def run_tool(name, args):
    if not isinstance(args, dict):
        args = {}
    try:
        if name == "run_shell":
            cmd = str(args.get("command") or "").strip()
            if not cmd:
                return "error: no command"
            p = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True, timeout=180)
            out = ((p.stdout or "") + (p.stderr or "")).strip() or "(no output)"
            return (f"[exit {p.returncode}]\n" if p.returncode else "") + out[:6000]
        if name == "read_file":
            with open(os.path.expanduser(str(args.get("path") or "")), "r", errors="replace") as f:
                return f.read()[:8000]
        if name == "write_file":
            path = os.path.expanduser(str(args.get("path") or ""))
            with open(path, "w") as f:
                f.write(str(args.get("content") or ""))
            return f"wrote {path}"
        if name == "list_dir":
            path = os.path.expanduser(str(args.get("path") or "."))
            return "\n".join(sorted(os.listdir(path)))[:6000]
        if name == "web_fetch":
            url = str(args.get("url") or "")
            r = urllib.request.Request(url, headers={"User-Agent": "AgentWorkbench-delegate"})
            with urllib.request.urlopen(r, timeout=30) as resp:
                return resp.read(200000).decode("utf-8", errors="replace")[:8000]
        return f"error: unknown tool '{name}'"
    except Exception as exc:
        return f"error: {exc}"


def parse_text_tool_calls(content):
    """Recover tool calls emitted as text (qwen3-coder XML / Hermes / bare JSON)."""
    if not content or not content.strip():
        return [], content
    calls, cleaned = [], content
    for fm in re.finditer(r"<function=([A-Za-z0-9_]+)\s*>(.*?)</function>", content, re.DOTALL):
        if fm.group(1) not in TOOL_NAMES:
            continue
        args = {}
        for pm in re.finditer(r"<parameter=([A-Za-z0-9_]+)\s*>(.*?)</parameter>", fm.group(2), re.DOTALL):
            args[pm.group(1)] = pm.group(2).strip("\n")
        calls.append({"function": {"name": fm.group(1), "arguments": args}})
    if calls:
        cleaned = re.sub(r"<function=.*?</function>", "", cleaned, flags=re.DOTALL)
        return calls, re.sub(r"</?tool_call>", "", cleaned).strip()
    cands = re.findall(r"<tool_call>\s*(\{.*?\}|\[.*?\])\s*</tool_call>", content, re.DOTALL)
    cands += re.findall(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", content, re.DOTALL)
    if not cands and content.strip()[:1] in "{[":
        cands.append(content.strip())
    for blob in cands:
        try:
            data = json.loads(blob)
        except (ValueError, TypeError):
            continue
        for obj in (data if isinstance(data, list) else [data]):
            if not isinstance(obj, dict):
                continue
            fn = obj.get("function") if isinstance(obj.get("function"), dict) else obj
            nm = (fn.get("name") or fn.get("tool") or "").strip()
            if nm not in TOOL_NAMES:
                continue
            ar = fn.get("arguments")
            if ar is None:
                ar = fn.get("parameters")
            calls.append({"function": {"name": nm, "arguments": ar if ar is not None else {}}})
    return calls, ("" if (calls and content.strip()[:1] in "{[") else cleaned.strip())


def delegate(prompt, model):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}]
    out_parts = []
    for _ in range(MAX_STEPS):
        msg = ollama_chat(model, messages)
        content = (msg.get("content") or "").strip()
        tool_calls = msg.get("tool_calls") or []
        if not tool_calls and content:
            recovered, content = parse_text_tool_calls(content)
            if recovered:
                tool_calls = recovered
        turn = {"role": "assistant", "content": msg.get("content") or ""}
        if tool_calls:
            turn["tool_calls"] = tool_calls
        messages.append(turn)
        if content:
            out_parts.append(content)
        if not tool_calls:
            break
        for call in tool_calls:
            fn = call.get("function") or {}
            nm = (fn.get("name") or "").strip()
            ar = fn.get("arguments")
            if isinstance(ar, str):
                try:
                    ar = json.loads(ar)
                except ValueError:
                    ar = {}
            result = run_tool(nm, ar or {})
            out_parts.append(f"[{nm}] {result[:800]}")
            messages.append({"role": "tool", "tool_name": nm, "content": result})
    return "\n\n".join(p for p in out_parts if p) or "(local model returned no output)"


DELEGATE_TOOL = {
    "name": "delegate_local",
    "description": (
        "Delegate a bounded, mechanical, easily-verified subtask to a FREE local LLM "
        "(Ollama) to save tokens. The local model has run_shell/read_file/write_file/"
        "list_dir/web_fetch on this machine and returns a concise result. Use for simple "
        "lookups, boilerplate, format conversion, grep-style searches, quick shell tasks. "
        "Do NOT use for complex, ambiguous, or high-stakes work — keep those yourself. "
        "Always verify the returned result before relying on it."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "Self-contained instructions for the local model. Include all context it needs."},
            "model": {"type": "string", "description": f"Ollama model (default {DEFAULT_MODEL}). Use granite4:tiny-h for trivial/fast, qwen3:8b for more reasoning."},
        },
        "required": ["prompt"],
    },
}


def handle(req):
    method = req.get("method")
    if method == "initialize":
        ver = (req.get("params") or {}).get("protocolVersion") or PROTO_DEFAULT
        return {"protocolVersion": ver, "capabilities": {"tools": {}},
                "serverInfo": {"name": "agent-workbench-local-delegate", "version": "1.0.0"}}
    if method == "tools/list":
        return {"tools": [DELEGATE_TOOL]}
    if method == "tools/call":
        p = req.get("params") or {}
        if p.get("name") != "delegate_local":
            return {"isError": True, "content": [{"type": "text", "text": f"unknown tool {p.get('name')}"}]}
        args = p.get("arguments") or {}
        prompt = str(args.get("prompt") or "").strip()
        model = str(args.get("model") or DEFAULT_MODEL).strip() or DEFAULT_MODEL
        if not prompt:
            return {"isError": True, "content": [{"type": "text", "text": "delegate_local: empty prompt"}]}
        try:
            out = delegate(prompt, model)
        except urllib.error.URLError as exc:
            return {"isError": True, "content": [{"type": "text", "text": f"Ollama unreachable at {OLLAMA}: {exc}"}]}
        except Exception as exc:
            return {"isError": True, "content": [{"type": "text", "text": f"local delegate error: {exc}"}]}
        return {"content": [{"type": "text", "text": f"[delegated to {model}]\n{out}"}]}
    if method == "ping":
        return {}
    if method == "resources/list":
        return {"resources": []}
    if method == "prompts/list":
        return {"prompts": []}
    return {}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except ValueError:
            continue
        method = req.get("method", "")
        if method.startswith("notifications/") or "id" not in req:
            continue  # notifications get no response
        rid = req.get("id")
        try:
            result = handle(req)
            resp = {"jsonrpc": "2.0", "id": rid, "result": result}
        except Exception as exc:
            log("handler error:", exc)
            resp = {"jsonrpc": "2.0", "id": rid, "error": {"code": -32603, "message": str(exc)}}
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
