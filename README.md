# Codex Workbench

Linux desktop workbench for Codex, Claude Code, and Gemini CLI sessions. It
keeps the conversation readable while putting commands, file changes, tools,
plans, and progress in a separate work log.

![Codex Workbench icon](assets/codex-workbench.png)

## Requirements

- Linux with Python 3 and Tkinter
- At least one supported CLI installed and authenticated:
  - `codex`
  - `claude`
  - `gemini`

## Run

```bash
./codex-conversation-viewer
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

## Privacy

Session data remains local under
`~/.config/codex-conversation-viewer/sessions`. The app also reads local session
metadata from supported agent tools to populate its session list. It does not
include analytics or telemetry of its own.

## License

MIT
