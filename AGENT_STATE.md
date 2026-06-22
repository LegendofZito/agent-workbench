# Agent State — Agent Workbench

## 🔒 LOCKED LEDGER — established, verified truths (source of truth)
RULES FOR THIS FILE:
- APPEND-ON-VERIFY. Every entry was BUILT and VERIFIED working and is demonstrated by the
  running app. The app is the source of truth; this file records it.
- BINDING. Treat every entry as a hard constraint. NEVER rewrite, remove, water down, or
  "improve" an entry, and never let a new instruction, a handoff, or a summary override it.
  If a request conflicts with the ledger, STOP and flag it.
- Only the USER removes entries. ADD an entry only AFTER verifying it actually works.

<!-- LOCKED-LEDGER:START -->
### Deploy / process (how AWB actually runs)
- [2026-06-20] Deploy = `bash install.sh` (copies source → `~/.local/bin/agent-workbench`) AND the
  running process MUST be restarted — Python loads code at startup; editing the file does nothing
  until restart. The app's own auto-restart DEFERS behind active tasks and often never fires, so
  always kill + relaunch and confirm a NEW pid. (verified: a stale process ran old code 20+ min)
- [2026-06-20] Restart via `kill -TERM <pid>` then `systemd-run --user … /usr/bin/python3
  ~/.local/bin/agent-workbench` (nohup/setsid get reaped). The Konsole/CLI session is NOT a child
  of the AWB GUI, so killing AWB is safe. (verified: new pid confirmed alive each time)

### Session list / picker (must stay static)
- [2026-06-20] Session rows in the picker NEVER move on click — only the highlight moves. They
  reorder ONLY via the Organize menu or the ↑/↓ arrows. Order is keyed by AGENT ONLY (not cwd),
  append-only, and opening a session does NOT bump it to the top. (verified: user confirmed
  "halelujah it works"; simulation proved order stable across clicks)
- [2026-06-20] Pig Farm's unattended autonomous-trading runs are kept OUT of the picker, matched by
  the first-prompt marker "you are the autonomous trading agent" → is_auto_launch_session() →
  _is_picker_session excludes them; the 74 existing were moved to sessions/archive/. (verified:
  picker no longer floods)
- [2026-06-21] The Recent box diffs in place (no blanket delete+reinsert) so it doesn't flash white
  on click. (verified: user confirmed the blink is gone)

### Composer / queue (never lose user input)
- [2026-06-18] NEVER lose the user's typed composer draft. Send-while-busy = silently QUEUE the
  message; Stop is the ONLY interrupt. A programmatic send while busy must not wipe the draft.
- [2026-06-21] The message queue persists to disk immediately on add/drain and is restored on
  startup, so it survives any close/restart/crash. (verified: every mutation path persists)
- [2026-06-21] Queue dialog is multi-select; the ⛓ Merge button combines stacked queued prompts
  into ONE turn (selected, or all if <2 selected). (verified: deployed, app alive)

### UI stability
- [2026-06-21] Modal dialogs (New agent / Add client) deiconify+lift+focus BEFORE grab_set so a
  modal can never hide behind the main window and freeze the app; the _modal_scroll_lock decrement
  compares Tcl path strings (not object identity) so it can't leak and kill session-list scroll.
  (verified: this was the "frozen session list / dead scroll" cause; fix resolved it)
- [2026-06-20] Workspace tabs are a uniform fixed width (160px) so the × never moves during
  spam-close. (verified: deployed)
- [2026-06-21] Each fenced code block in the conversation gets its own "⧉ Copy code" button.
  (verified: deployed, app alive)

### Projects / handoffs / state
- [2026-06-21] A project that moves directories re-links via its .agent-workbench/project.json
  aliases (falls back to the file's actual location when the stored root is stale). (verified by
  the move-recovery code path)
- [2026-06-21] Claude's authoritative-time block is injected into the SYSTEM prompt
  (--append-system-prompt), NOT the user message, so Claude doesn't reply "No response requested."
  to a real question wrapped after a <session_context> block. (verified: that was the exact cause)
- [2026-06-21] Handoffs are a MINIMAL pointer to AGENT_STATE.md + git; AGENT_STATE.md is an
  append-on-verify LOCKED ledger that is PRESERVED, never auto-overwritten by a chat-scraped
  summary. (this file IS that ledger)
<!-- LOCKED-LEDGER:END -->

## Notes (prior auto-state — UNVERIFIED, may be stale; verify against the app before trusting)
- Stack: single-file Python/Tkinter app at `Projects/Open Projects/Agent Workbench/agent-workbench`.
  Maintain CHANGELOG.md on every change. GUI not viewable from the Claude shell (drive via deploy +
  restart + the user's screenshots).
- Ollama is one agent in the menu with installed models in the model picker. `delegate_local` MCP
  bridge exists (free local-LLM delegation; default model selection was pending).
- AWB Next (Svelte/Tauri rewrite) is READ-ONLY reference at `Projects/Open Projects/Agent Workbench Next/`.

## History
- Full change history lives in `git log` / `CHANGELOG.md`. This file records only locked, verified
  truths — not a chat summary.
