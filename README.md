# Agent Workbench

Linux desktop workbench for Codex, Claude Code, and Gemini CLI sessions. It
keeps the conversation readable while putting commands, file changes, tools,
plans, and progress in a separate work log.

Selected Codex and Claude terminal sessions are mirrored live. Conversation
messages keep readable headings, lists, checklists, emphasis, and inline code
while implementation output stays in Work Log.

The sidebar provides per-agent model and effort controls. Defaults favor
responsive general use: Codex GPT-5.5 at medium effort, Claude Sonnet at medium
effort, and Gemini Auto. Preferences are remembered separately for each agent.

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

## Run

```bash
./agent-workbench
```

Send prompts with `Ctrl+Enter`.

## Install

```bash
./install.sh
```

The installer adds the launcher, executable, and taskbar icon under the user's
local XDG directories.

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

## License

MIT
