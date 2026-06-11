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

Codex and Claude sessions show their active context usage in the top bar. The
conversation scrollbar is green below 40%, yellow from 40-60%, orange from
60-80%, and red above 80%. Claude's meter follows automatic compaction and
labels compacted sessions, so transcript length is not mistaken for active
context usage.

The sidebar provides per-agent model and effort controls. Defaults favor
responsive general use: Codex GPT-5.5 at medium effort, the installed Claude
client's default model at medium effort, and Gemini Auto. Resumed Claude
terminal sessions retain their detected Opus, Sonnet, or Haiku model family.
Preferences are remembered separately for each agent.

The Artifacts tab stores screenshots, images, text files, and other documents in
a local folder dedicated to the selected session. Files can be added with the
file picker or dragged into the tab when TkDND is installed. Images and text
files have built-in previews; every artifact can be opened or have its local
path copied. Use **Attach** in the composer or artifact preview to make files
available to the agent on the next turn. Adding a file from the Artifacts tab
stores it without sending it.

Conversation text supports normal selection, right-click copy, clickable web
links, and clickable existing local paths. **Copy latest** copies the latest
agent answer. New sessions ask for an optional title and automatically derive
one from the first prompt when the title is left blank.

The built-in Terminal tab provides a persistent PTY shell in the selected
project. It loads the user's normal interactive shell configuration and
supports command history, interactive line input, `Ctrl+C`, and shell restart.

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
