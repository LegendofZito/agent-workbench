# Agent State

## Project
- **Name:** Agent Workbench (OG — primary)
- **Directory:** /home/zito/Projects/Open Projects/Agent Workbench
- **State file (this file):** /home/zito/Projects/Open Projects/Agent Workbench/AGENT_STATE.md
- **Source:** /home/zito/Projects/Open Projects/Agent Workbench/agent-workbench (single Python/Tkinter file)
- **Installed binary:** ~/.local/bin/agent-workbench
- **Deploy:** `cd "/home/zito/Projects/Open Projects/Agent Workbench" && bash install.sh` (app self-restarts gracefully when idle via update-request.json — don't hard-kill a responsive app)
- **Related project (read-only reference):** /home/zito/Projects/Open Projects/Agent Workbench Next

## Current Objective
- AWBfixes1 all 4 items complete as of 2026-06-19 (deployed 7a58a84). No critical in-flight work.

## Durable Facts
- Single-file Python/Tkinter app. All edits go to the source file, then `bash install.sh`.
- Do NOT hard-kill a responsive app to deploy — install.sh signals a graceful self-restart. Only hard-kill if wedged.
- OG is the only writable project. Next is a Svelte/Tauri rewrite — read-only unless explicitly told otherwise.
- GPU risk: AMD DATA FABRIC SYNC FLOOD on RX 6800M — `_OLLAMA_INFERENCE_SEM` caps concurrent Ollama inference to 1.
- **OllamaBackend has full tool calling** (run_shell, read_file, write_file, list_dir, web_fetch) with text-format tool-call parsing (qwen3-coder XML + Hermes JSON).
- **Ollama is now ONE agent** in the menu; installed models are chosen in the model picker (not one client per model). Default model resolver prefers qwen3-coder:30b → qwen3:14b → first installed.
- **UI freeze = O(n²) work-log render** (per-line see()/yview()). Fixed via `_suspend_work_autoscroll` during bulk render. py-spy diagnoses; the persisted log re-freezes on restart unless the render fix is deployed first.

## Recent Changes (2026-06-19 evening) — full detail in CHANGELOG.md
- **`recent_session_list` modal scroll-lock** — missing wheel guard added; now respects `_modal_scroll_lock`
  like `session_list` does. Scroll bleed fully plugged for both modal dialogs. (AWBfixes1 #1 complete.)
- **Redundant model label removed from prompt_state** — busy bottom-bar showed "Opus · 2m 15s" right next
  to the "Working" badge; now shows just "2m 15s · streamed ~N tokens". Agent identified by tab + selector.
  (AWBfixes1 #2.)

## Recent Changes (2026-06-19 daytime) — full detail in CHANGELOG.md
- **Live-session auto-detect DISABLED** (`_AUTO_OPEN_LIVE_SESSIONS = False`): the feature
  (`poll_live_sessions`, built in the Pig Farm session) was spawning DUPLICATE tabs every 5s — its
  dedup via `_known_source_ids` didn't catch an already-open session before the next poll fired, so
  it re-opened the same sessions endlessly and flooded the UI. Hard-off until the dedup is reworked.
  Also added a load-time tab dedup (collapse workspace_tabs sharing a source_session_id) so the
  duplicates don't pile back up on restart.
- **Transcript mirror — machine-injection filter** (`strip_harness_injections`): user-role turns
  that are `<task-notification>`, `<system-reminder>`, post-compaction summaries, attachment
  wrappers/prompts, handoff/project-state prefixes, or bare `[Image: source:]` artifacts no longer
  render as "YOU" bubbles. Parser-level → also cleans stored turns + Hand Off packet.
- **Hand Off freshness**: `_sync_session_from_transcript` force-reads the transcript synchronously
  before staging the packet (no 2s blind spot).

## Recent Changes (2026-06-18 evening) — full detail in CHANGELOG.md
- **Ollama as a single agent + model picker** (`_model_options_for("ollama")` → live `/api/tags`, cached 8s; `start_turn` resolves live model from session backend settings).
- **Ollama "Not installed" fix** in the new-agent dialog (HTTP-backed → "Ready" when server reachable, not a CLI-exe check).
- **Work-log render freeze fix** (`_suspend_work_autoscroll`).
- **Mirrored session live-render**: a Claude session open in BOTH terminal + AWB now shows terminal turns LIVE (early-return for `origin=="local"` now gated on `self.busy`). Context % was ALREADY shared/accurate (reads transcript usage via `claude_session_metadata`); the gap was only display.
- **Queue editor fix**: white cursor, working Ctrl+C/X/V/A, accurate Save→Saved state.
- **Interrupt-on-send REVERTED** — send-while-busy queues silently; only Stop interrupts.
- **Per-client skills bar** (built by a parallel session): Claude/Codex/Gemini/Ollama each show their own skills.

## Local Models (Ollama) — installed ~65 GB total
- KEEP — qwen3:14b (best tool-calling, fits 12GB VRAM, 37 tok/s), qwen3-coder:30b (best coding, spills, 19 tok/s), gemma3:12b (Pig Farm Tell Extractor).
- CANDIDATES TO REMOVE (experiments pulled 6/17, ~21 GB): granite4:micro, granite4:tiny-h, qwen3:8b, llama3.1:8b, qwen2.5-coder:7b. deepseek-r1:14b (9 GB, reasoning, can't tool-call) borderline.

## Open Tasks
- Ollama multi-model **sub-agent distribution** (different local models for different sub-tasks) — NOT built. This is the "fleet" vision.
- Cosmetic: image attachment renders as a 2nd raw `[Image: source: /path]` YOU bubble — collapse into an inline chip.

## Verification Commands
- cd "/home/zito/Projects/Open Projects/Agent Workbench" && git log --oneline -10
- ollama list   # installed local models
- ~/.local/bin/py-spy dump --pid <gui-pid>   # diagnose a freeze

## Last Updated
- 2026-06-18T23:30:00-04:00
