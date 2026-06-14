# Agent Workbench

Linux desktop workbench for Codex, Claude Code, and Gemini CLI sessions. It
keeps the conversation readable while putting commands, file changes, tools,
plans, and progress in a separate work log.

Selected Codex and Claude terminal sessions are mirrored live. Conversation
messages keep readable headings, lists, checklists, emphasis, and inline code
while implementation output stays in Work Log. User messages appear in a
right-side chat lane, with agent responses kept on the left. Substantial web
research appears as a collapsed, scrollable report card inside Conversation;
raw tool payloads remain in Work Log.

Workspace tabs can run multiple independent agent sessions at the same time,
including several Claude sessions or a mix of Claude, Codex, Gemini, and custom
CLI agents. Background tabs continue working and display an activity marker.
Open tabs, selected sessions, agents, projects, models, and effort settings are
restored after restart. Use `Ctrl+T` for a new tab, `Ctrl+W` to close one, and
`Ctrl+Tab` to switch.

Messages sent while an agent is working are queued on that tab and submitted in
order when the current turn finishes. Claude-backed Workbench sessions reload
their full Claude transcript after restart. A down-arrow in Conversation jumps
directly to the newest message in long discussions. When new output arrives
while you are reading earlier messages, Workbench preserves your scroll position
and changes the arrow to **New** instead of interrupting your review.

Closing Agent Workbench while a turn is running queues the close until all
active turns finish. Installing an update uses the same safe point, then
restarts the newly installed build automatically. If the process is forcibly
terminated or crashes, the next launch identifies sessions whose last turn was
interrupted so unfinished work is not silently forgotten.

Codex and Claude sessions show their active context usage in the top bar. The
conversation scrollbar is green below 40%, yellow from 40-60%, orange from
60-80%, and red above 80%. Claude's meter follows automatic compaction and
labels compacted sessions, so transcript length is not mistaken for active
context usage. **Hand Off** stays visible in the top bar and becomes available
at 70% active context or after the first compaction, when older details already
depend on a generated summary.

The separate **Limits** badge reports account rate-limit usage rather than
conversation context. Click it to refresh and show reset times. Codex reads the
five-hour and weekly windows from its native session telemetry; Claude queries
the same five-hour, weekly, and Sonnet-only usage data exposed by Claude Code.

The sidebar provides per-agent model and effort controls. Claude choices
include Fable, Opus, Sonnet, and Haiku. Defaults follow the installed clients:
Codex uses the model configured by the local Codex CLI at medium effort, Claude
uses the installed client's default model at medium effort, and Gemini uses Auto. Resumed Claude
terminal sessions retain their detected Fable, Opus, Sonnet, or Haiku model family.
Preferences are remembered separately for each agent.

Newly named sessions appear immediately. Only the newest untouched session is
shown, preventing abandoned empty sessions from filling the sidebar. Claude session
names are passed into Claude Code so they also appear in its `/resume` picker.
Sessions can be renamed, moved up or down with persistent ordering, or deleted
from the sidebar. Workbench presents the connected client's native history as
one session list; it does not label sessions as imported or create a separate
visible transcript type. Continuing a listed session resumes that same native
Codex, Claude, or Gemini session ID. After confirmation, deleting a connected
session also removes it from that client's history.
Codex uses its native archive operation; Claude and Gemini use their native
session deletion storage/commands.

The Artifacts tab stores screenshots, images, text files, and other documents in
a local folder dedicated to the selected session. Drop a file directly into
Conversation to store it and attach it to the next message, use **Attach**, or
press `Ctrl+V` in the composer to attach an image from the Wayland clipboard.
Images and text files have built-in previews. Adding a file from the Artifacts
tab stores it without sending it; secondary actions are available by
right-clicking the file. A queued attachment can be sent without typing a
separate message; Workbench asks the agent to inspect it.

Conversation text supports click-drag selection, `Ctrl+C`, right-click copy,
clickable web links, and clickable existing local paths. Right-clicking selected
text opens a compact **Copy** menu. New sessions ask for an optional title and
automatically derive one from the first prompt when the title is left blank.
Once Claude creates the real session, Workbench keeps its title synchronized
with Claude Code's `/resume` history. Workbench also normalizes print-mode
Claude transcripts into Claude's standard CLI history shape, so sessions
created in Workbench appear in the terminal picker and resume by their title.

The built-in Terminal tab provides a persistent PTY shell in the selected
project. It loads the user's normal interactive shell configuration and
supports command history, interactive line input, `Ctrl+C`, and shell restart.

Claude orchestration is non-modal. With **Options → Claude orchestration →
Smart routing**, Claude announces a concise routing plan only for substantial
actionable work, then uses its native subagents inside the current session:
Haiku for bounded read-only research, Sonnet at low/medium/high effort for
implementation based on complexity, and Opus at high effort for architecture,
high-risk decisions, and final review. Haiku does not expose an effort setting.
It does not ask after every prompt or create a separate Workbench worker unless
you explicitly use the Workers controls.

The **Workers** dialog is reserved for explicitly started manual worker
sessions. It shows active workers by default; completed and interrupted history
is optional and can be cleared. Native Claude subagents remain part of the
current Claude conversation rather than creating duplicate Workbench tabs.

![Agent Workbench icon](assets/agent-workbench.png)

## Requirements

- Linux with Python 3 and Tkinter
- At least one supported CLI installed and authenticated:
  - `codex`
  - `claude`
  - `gemini`
- Optional `python3-pillow` for image previews
- Optional `tkdnd` for desktop drag and drop

## Run

```bash
./agent-workbench
```

Send prompts with `Ctrl+Enter`.

The installer also places managed `claude`, `codex`, and `gemini` launchers in
`~/.local/share/agent-workbench/cli` and adds that directory to interactive
Bash sessions. These launchers use the same no-approval modes as Agent
Workbench. Set `AGENT_WORKBENCH_SAFE_PERMISSIONS=1` for a single command when
you intentionally want the client to use its normal approval prompts.

## Context handoff

Agent Workbench tracks each client's active context window separately from
account usage limits. At 70% it displays a context-quality warning; at 85% the
warning becomes critical.

Use **Hand Off** to create a fresh client session without copying text or
managing a handoff file. The new session:

- receives a local `HANDOFF.md` artifact covering user goals, decisions,
  upgrades, failures, technical details, and unresolved follow-ups
- starts with a fresh backend session and context window
- continues automatically with the same client, project, model, and effort
- receives the next numbered title, such as `Project`, `Project 2`, `Project 3`

Once the warning threshold is reached, Workbench updates `HANDOFF.md` only when
the saved conversation state changes. The staged file remains available in
Artifacts even if the client later stops responding.

Failed client turns remain visibly failed and include the client's diagnostic
message when available instead of immediately returning the status badge to
Ready.

## Recovery and refresh

Use **Refresh** or press `F5` to reconcile Workbench with the clients and local
session files. Refresh preserves an active turn, rescans session history,
reloads transcript and context data, and restarts an idle Codex service if its
local app server stopped.

A watchdog verifies client-process health every two seconds. It does not cancel
long-running work. After two minutes without an event it changes the status to
**Still working** and explains that Refresh is safe. A turn is failed
automatically only when its underlying client process is confirmed gone.

## Install

Download the latest Linux archive from this repository's **Releases** page.

Extract it, then run:

```bash
./install.sh
```

The installer adds the launcher, executable, and taskbar icon under the user's
local XDG directories.

Use **Add client** in the sidebar to connect Codex, Claude Code, or Gemini CLI.
Installed clients open their own vendor-managed sign-in flow. Missing clients
link only to the vendor's official installation guide.

Other local command-line agents can be registered with **Add custom CLI**. Enter
a command template such as `aider --message {prompt}`. If `{prompt}` is omitted,
Agent Workbench sends the prompt through standard input. Custom definitions are
stored only in the current user's local configuration and never include or copy
the client's credentials.

## API keys and MCP servers

Open **Options → API Keys & MCP…** to connect optional providers (such as
OpenRouter or Groq) and MCP servers. Paste a key and Agent Workbench
auto-detects the provider from its prefix, or pick one from the list and add it
manually.

Keys are stored locally in `~/.config/agent-workbench/secrets.json` (mode
`0600`), never logged, and never leave your machine. They are injected as
environment variables when agents launch. The `claude`, `codex`, and `gemini`
clients use their own account sign-in, so their provider keys stay **off by
default** — enable one only if you intentionally want to use API billing.

MCP servers added here are registered with Claude Code at user scope.

## Security

This prototype starts agent CLIs in their unrestricted automation modes:

- Codex: `approvalPolicy: never` and `sandbox: danger-full-access`
- Claude Code: `--dangerously-skip-permissions`
- Gemini CLI: `--yolo --skip-trust`

Agents can execute commands and modify files without confirmation. Run the app
only in directories and environments where that level of access is acceptable.

The Terminal tab has the same operating-system access as the user running Agent
Workbench. Full-screen terminal interfaces are not yet emulated; line-oriented
interactive commands and agent CLI subcommands are supported.

## Privacy

Session data remains local under `~/.config/agent-workbench/sessions`. Existing
data under `~/.config/codex-conversation-viewer` is copied automatically on the
first launch after upgrading. The app also reads local session metadata from
supported agent tools to populate its session list. It does not include
analytics or telemetry of its own.

Artifacts remain local under `~/.config/agent-workbench/artifacts`. They are
never added to the application repository or release archive.

Release downloads contain only the tracked application source, launcher,
installer, icon, license, and documentation. They do not contain developer or
user sessions, credentials, tokens, local configuration, or account data.

## License

MIT
