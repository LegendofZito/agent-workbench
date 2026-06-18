# Agent Workbench — Changelog

Running log of every change, newest first. Source: `agent-workbench` (single Python/Tkinter file).
Deploy: `bash install.sh` (copies source → `~/.local/bin/agent-workbench`, app self-restarts after the
current turn). A change is only LIVE after a deploy + the app reloading.

---

## 2026-06-18

### Renaming a chat no longer wipes the window (esp. mid-turn)
- Renaming a session called `open_session()`, which clears the views and re-renders the conversation from
  the **saved** copy. If a turn was still streaming, that live content wasn't saved yet → "everything in the
  window disappeared." Rename now updates the label in place (title bar, session list, workspace tab) and
  **never reloads the conversation**, so it's safe to rename a chat while it's processing. (`rename_selected_session`.)

### Client update watcher (claude / codex / gemini)
- New **Options → "Check for client updates…"**. On launch the app checks each wrapped CLI's installed
  version against the latest available (codex/gemini via `npm view`, claude via its native `claude update`),
  and the **Options** button turns yellow when an update is available. The dialog lists each client
  (current → latest) with a one-click **Update** button (`npm install -g …@latest`, or `claude update`),
  streams the output, and re-checks afterward — so updating from a terminal also clears the alert.

### "Ultracode" is now selectable directly in the Effort dropdown
- It was only reachable from the Claude-orchestration dialog before. Now **Ultracode** appears as the top
  tier in the **Effort** picker (low · medium · high · xhigh · max · **Ultracode**). It's a synthetic tier:
  at launch it maps to `--effort max` **+ ultra multi-agent orchestration**, so picking it enables ultracode
  for the run regardless of the orchestration dialog. (`_effort_options_for` appends it; the command builder
  maps `effort == "Ultracode"` → `orchestration_mode="ultra"`, `effort="max"`.) The orchestration dialog's
  Ultracode radio still works too.

### Hand Off + Active% moved up to the Skills bar (bar 1)
- Decluttered the lower status bar. The **Active context %** badge now sits at the **far right of the Skills
  bar** (directly above the Send button), and **Hand Off** sits at the **far left** of the Skills bar (just
  right of the ✦ Skills button). Skill chips fill the middle. The lower bar now carries only Sub-agents ·
  activity · status · Stop/Attach/Send/queue. (Reverses last entry's "move Hand Off + Active% next to
  status"; widgets kept their attribute names so context recolor + Hand Off enable/disable still work.)

### Spawned tab now shows real sub-agents (running + finished history)
- **The complaint:** the "Spawned" tab was always empty and nothing showed "which agents are up and
  running," even when Claude fanned work out to sub-agents. Root cause: the Spawned tab only listed
  workbench-launched *worker sessions* (`worker_parent_session_id`) — never in-turn Agent/Task sub-agents —
  and the in-turn ones only flickered in the "Sub-agents N" counter, getting deleted the instant they
  finished (no history).
- **Fix:** the backend now parses Claude Code's explicit sub-agent lifecycle events
  (`system/task_started`, `task_updated`, `task_notification`) — far richer than inferring from tool
  blocks: they carry `subagent_type`, description, status, summary, token usage, and duration. Each
  workspace keeps a **durable registry** of every sub-agent spawned this session, upserted idempotently by
  `tool_use_id` (so the older tool_use/tool_result fallback and the new task events don't double-count).
- The **Spawned tab** (relabeled "Agents & sessions spawned from this session") now renders two groups:
  **Sub-agents (this session)** — live ● running (yellow), ✓ completed (green) with duration + tokens +
  summary, ✗ failed (red), newest first — and **Worker sessions** below. It refreshes live on every
  sub-agent event. The "Sub-agents N" counter and popover still show **running only** (unchanged).
- Finished sub-agents now **persist across turns** (turn-end only clears stale still-"running" entries,
  not history). "✓ Sub-agent finished" logs exactly once, on the running→done transition.
- **Latent bug fixed:** a non-matching `tool_result` used to pop the last running sub-agent (any normal
  tool result could erase a live background agent). Stops now act only on an exact id match.
- Verified: `py_compile` clean + a logic simulation driven by real captured stream events
  (idempotency, count semantics, finish-once, history persistence, no-erase). Touches the stream parser,
  the `subagent_*` event handlers, `_live_subagents`/`_session_subagents`, and `_refresh_spawned_tab`.

### Footer consolidated from three bars to two
- The bottom area had three rows (Sub-agents/Ready · Skills · Active%/status/Send). Merged the two
  status rows into ONE: now it's just **Skills bar** + a single **status/controls bar** carrying —
  Sub-agents · activity · **Active context %** · **Hand Off** · ready/working status · Stop/Attach/Send.
  The **Hand Off** button moved down from the top bar to sit next to the status, and **Active %** sits
  there too. (Removed the separate `composer_state` row.)

### Ultracode orchestration mode (the tier above max effort)
- New **Ultracode** option in the Claude-orchestration dialog (alongside Smart / Direct). A single
  max-effort run is still one agent; Ultracode tells Claude to fan substantial work out to **many parallel
  sub-agents / multi-agent workflows** and adversarially verify results before reporting — the most
  thorough, most token-hungry tier. Reuses the Smart routing + cost-discipline + local-model rules.
  (`CLAUDE_ULTRACODE_ORCHESTRATION_PROMPT`; mode `ultra`.) Note: the model `--effort` scale itself still
  tops out at `max` (the CLI's ceiling) — Ultracode is "more than max" via orchestration, not effort.

### Active-context % moved to the bottom status bar
- The active-context percentage badge moved from the top bar down to the bottom bar, just left of the
  "working…"/status text, so context usage and activity sit together. Still recolors as context fills.

### Skill popover no longer shifts the background
- Opening a skill nudged the whole composer because the skill's chip border was *thickened* 1px→2px
  (resizing the chip, reflowing the row). Now opening a skill only **recolors** the chip's existing 1px
  border (no size change → no shift); the popover still anchors to its chip.

### Typing always goes to the composer / conversation
- On any non-terminal tab (Conversation, Work Log, Artifacts, Spawned) the composer is auto-focused, and a
  printable key pressed while a read-only view (Work Log/Artifacts) has focus is redirected into the
  composer — so everything you type reaches the conversation, nowhere else. Copy/find/scroll still work in
  those views; the Terminal tab keeps its own input. (`_route_key_to_composer`.)

### Ctrl+A selects all in the prompt box
- Bound Ctrl+A (and Ctrl+Shift+A) to select-all in the composer (Tk's default Ctrl+A was "go to line
  start"). (`_input_select_all`.)

### Ctrl+Z undoes only PASTES, never typed text
- Ctrl+Z in the composer removes the most recent **pasted** block and leaves everything you **typed**
  intact (Ctrl+Y / Ctrl+Shift+Z re-inserts it). Implemented with our own paste tracking instead of Tk's
  linear undo: each paste (Ctrl+V, middle-click, or the right-click menu) is bracketed with marks
  (start "right" gravity, end "left" gravity) so text typed at either boundary stays outside the block;
  Ctrl+Z deletes that marked range. Typing is never tracked, so it's never undone. Paste tracking resets
  on draft-restore and on send. (`_paste_text_marked`, `_on_paste_event`, `_input_undo`/`_input_redo`.)

### New-session dialog lists your local models (one-click Start)
- Pulling an Ollama model didn't make it appear anywhere to start — you had to go through Add-client →
  Search → Connect. The **New session** dialog now auto-lists installed Ollama models under "Local models
  (Ollama)", each with a **Start** button that connects it and opens a new tab. Also fixed the dialog's
  "installed" check so a connected local model shows **Ready** instead of "Not installed" (it was running
  the same wrong `shutil.which` gate that affected sends). `connect_ollama_model` is now idempotent and
  returns its key; new `_start_local_model`.

### Tab status colors (yellow = working, green = done)
- Each agent tab's whole box now turns **yellow while a turn is running** and **green when it finishes**
  (dark text for contrast; the selected tab keeps a bright outline) —
  visible even for background tabs, so you can tell at a glance which agents are working or done without
  switching. The green clears when you view that tab (or when a new turn starts there). (`_tab_status` +
  a per-workspace `tab_done` flag set on `turn_done`, cleared on turn-start and on `switch_workspace`;
  tab render signature now includes status so the color updates live.)

### Copy button on every message
- Each message in the Conversation — yours and the agent's — now has a small inline **⧉ Copy** button at
  its end that copies that message's full text to the clipboard. Added on every rendered message
  (`append_chat`) and on live-streamed replies when they finish (`assistant_done`, pulling the full text
  from the turn's stored message). Embedded as real Tk buttons so they work on the read-only transcript.
  (`_insert_copy_button`, `_copy_message`.)

### Workers dialog now shows which agents are actually running
- The "Workers" dialog only listed manual worker *sessions* (usually none), so it never answered "which
  agents are up and running." Added an **Active agents** list at the top: every open agent tab in this
  window with a ●working / ○idle dot, agent label, live model, status, current session title, and
  in-turn sub-agent count — the current tab is marked, and double-clicking a row jumps to it. Refreshes
  live (~1.2s) without disturbing the worker-list selection. (`render_agents`, `_focus_agent_tab`.)

## 2026-06-17

### "Active agents" view — finally shows which agents are up and running
- The Workers/Manage-sub-agents dialog only listed *manual worker sessions*, so it never answered "which
  agents are running." It now leads with a live **Active agents (this window)** list: every open agent tab
  with ● working / ○ idle state, model, live status text, current session, and any in-turn sub-agent count
  — the current tab is marked, and **double-click a row to jump to that tab**. Auto-refreshes ~1.2s so
  busy/idle stays live (refreshes only the agents section, so it never disturbs the worker-list selection).
  Manual worker sessions moved below. (`render_agents` in `open_workers_dialog`.)

### Terminal is now interactive (type directly) + audit cleanup
- **Terminal:** the main terminal area was read-only — you could only type in a small box below it, which
  felt broken. It's now a real interactive terminal: keystrokes forward straight to the pty (bash echoes
  them), so you type anywhere in it. Full key handling — printable chars, Enter, Backspace, Tab, arrows,
  Home/End/Delete/PgUp/PgDn, Esc, Ctrl-A..Z (incl. Ctrl-C interrupt, Ctrl-L clear), Ctrl+Shift+C copy,
  Ctrl(+Shift)+V / middle-click paste. Selection still works for copy. Auto-focuses on tab open. The
  bottom input box stays as a secondary option. (Verified the pty shell itself works end-to-end and the
  key→byte mapping with a unit test; `_terminal_key`, `_terminal_send`, `_terminal_paste`.)
- **Audit:** scanned for PII — **none** in shipping code (all paths use `$HOME`/`expanduser`; the only
  absolute-path strings are in non-shipped build-spec docs). Verified all of today's features are present
  AND wired (13/13). Removed 6 confirmed-dead items (~62 lines): `clone_for_continuation`,
  `_defer_chat_update`, `_register_custom_client`, `_filter_deleted_sessions`, the legacy
  `WORK_LOG_MAX_LINES` constant, and the unused `GEMINI_THOUGHT_MARKER` regex. Confirmed no orphans left.

### Ctrl + scroll wheel zooms text (like a terminal)
- Hold Ctrl and scroll to zoom the Conversation, Work Log, prompt box, and embedded terminal. The handler
  reads each font (base + every tag) and nudges its size by ±1, so the whole view scales uniformly while
  preserving relative sizes, bold/italic, and monospace families; clamped to 6–72pt. Binds
  `<Control-MouseWheel>` + `<Control-Button-4/5>` (X11 wheel) and returns "break" so it zooms instead of
  scrolling. (`_scale_font_spec`, `_zoom_text_widget`, `_on_ctrl_wheel_zoom`, `_enable_text_zoom`.) Resets
  to defaults on app restart (session-local, terminal-style).

### Local-LLM delegation: Claude can offload cheap subtasks to a free local model (token savings)
- New dependency-free stdio MCP server `local_delegate_server.py` (deployed to `~/.config/agent-workbench/`,
  installed by `install.sh`) exposes a `delegate_local(prompt, model?)` tool. It runs the subtask on a local
  Ollama model with a real tool-use loop (run_shell/read_file/write_file/list_dir/web_fetch, incl. the
  text-format tool-call parser) and returns a concise result.
- The Claude backend now passes `--mcp-config` (in smart mode, non-strict so other MCP servers still load;
  skipped gracefully if the server file is missing). Default delegate model `qwen3:8b`; the tool accepts a
  `model` arg (e.g. `granite4:tiny-h` for trivial/fast).
- The orchestration policy already directs Claude to prefer this free tool for bounded/mechanical/verifiable
  subtasks and keep complex/high-stakes work on Sonnet/Opus.
- Verified end-to-end with a live headless `claude` call: Claude discovered the tool, called it, granite4:tiny-h
  ran `uname -r` via run_shell and returned `7.0.12-201.fc44.x86_64`, and Claude relayed it. (Also unit-tested
  the MCP server over stdio: initialize / tools/list / tools/call.)

### Queue items are editable; sub-agents are visible; routing is cost-disciplined
- **Editable queue:** in the Queued-prompts dialog, the detail pane is now an editable box with a **Save
  edit** button — fix a not-yet-sent prompt in place instead of deleting and re-queuing. (`save_edit`)
- **Sub-agent visibility:** in-turn sub-agents finish fast, so the live popover was usually empty and
  nothing landed in the Work Log. The Claude backend now writes **`🤖 Delegated → <type>: <description>`**
  to the Work Log when it spawns a sub-agent, and **`✓ Sub-agent finished: <type>`** when it completes
  (only on an exact tool-id match, so normal tool results don't misfire). The Work Log is now the durable
  record of what sub-agents did. (Note: the *Spawned* tab is for manual worker *sessions* — a different
  thing from in-turn Task/Agent sub-agents, which is why it's empty.)
- **Cost-disciplined routing:** the orchestration policy now mandates the **cheapest capable tier** (never
  Opus for Sonnet's work, never Sonnet for Haiku's) and adds a **local-model rung** — when a
  `delegate_local` MCP tool is available, prefer free local Ollama for bounded/mechanical/verifiable
  subtasks, keeping complex/high-stakes work on Sonnet/Opus. (The MCP bridge itself is the next build.)

### One request → one response bubble (conversation no longer splits a reply into many)
- A single turn was rendering as several "CLAUDE" bubbles. Root cause: the agent narrates in blocks
  between tool calls; the store writes a **new** `agentMessage` item whenever the previous item isn't an
  agentMessage (tool/work items land between narration), and `_render_turn` rendered each item as its own
  `append_chat` bubble. So one reply with 5 narration blocks = 5 timestamped bubbles on reload.
- Fix: `_render_turn` now merges all of a turn's assistant text into a single conversation bubble (shown at
  the first block's timestamp). Non-chat items (commands, file changes, system output) still render in
  order to the Work Log. Verified against this session's real transcript: a 5-message turn and an 8-message
  turn each collapse to 1 bubble, with 124 / 232 items still routed to the Work Log.

### Local models can now actually RUN tools (qwen-coder text-format tool calls recovered)
- The Ollama tool-use loop only honored Ollama's **structured** `tool_calls` field. Tested live: `llama3.1`
  emits that and worked, but the qwen-coder family does **not** — `qwen3-coder:30b` emits an XML form
  (`<function=run_shell><parameter=command>date</parameter></function>`) and `qwen2.5-coder` emits bare
  JSON, both in the message **content**. The loop saw "no tool call," printed the raw blob, and stopped —
  so the user's main local model never executed anything.
- Added `OllamaBackend._parse_text_tool_calls`, a fallback that recovers tool calls from text in three
  formats (qwen3-coder XML, Hermes/`<tool_call>` JSON, bare/fenced JSON), normalizes them to the
  structured shape, and strips the markup so the user sees prose, not a blob. Gated on real tool names so
  ordinary JSON in an answer isn't misread as a call. The loop now runs recovered calls. Unit-tested
  against the real captured outputs of all the installed models (7 cases incl. negative cases).
- Local-models dialog fixes: the hardcoded **"Local · offline"** label (it lied — Ollama was up) now reads
  **"Local · ready"**; the **"added"** marker checks the client `model` field (Ollama clients have no
  `command`, so it never showed before); removed the bogus **"needs aider"** gate that hid Connect when
  aider wasn't installed — one-click Ollama clients use the HTTP API, not aider.

### Sending to a local (Ollama) model no longer pops the "Connect an agent client" dialog
- Bug: every message sent to a local-model client (e.g. `qwen3-coder:30b`) opened the Add-client dialog
  and never sent. `send()` runs an "is the executable installed?" gate (`shutil.which`) that only makes
  sense for CLI agents. One-click Ollama clients are stored with just `key`/`label`/`model`
  (`ollama_chat/…`) and **no `command`**, because they talk to a local HTTP API via `OllamaBackend` — so
  `_agent_executable` returned `""`, the gate failed, and `open_add_client_dialog()` fired.
- Fix: `send()` now skips the executable gate when the active agent is HTTP-backed (its backend is an
  `OllamaBackend`, or its client `model` is an `ollama_chat/…` id). CLI agents (codex/claude/gemini) and
  manual custom-CLI clients still get the install check. Confirmed the dialog has no other auto-trigger —
  switching agents/sessions never pops it.

### Added Claude's "ultrareview" to Skills
- The installed Claude CLI exposes an `ultrareview` command (cloud-hosted multi-agent code review), but it
  was missing from the Skills list. Added it to `BUILTIN_SKILLS` + `SKILL_BLURBS`, so it shows in the
  Skills menu and can be favorited; running it sends `/ultrareview` (alias for `/code-review ultra`).
  Note: it's cloud-hosted/billed and needs a git repo, so run it from a session whose working dir is a repo.

### Sessions hold their place + new Organize button
- The picker no longer re-sorts by `updated_at` on every render, so opening/touching a session no longer
  makes it "jump to the top." Each session keeps its slot; a **brand-new** session lands at the top and
  pushes the rest down. New `_apply_stable_session_order` reads/writes the per-`agent|cwd` `session_order`
  (which the render path previously ignored — this also makes the ↑/↓ move buttons actually stick).
- Added an **Organize ▾** button on the SESSIONS header row. It drops down a menu to sort the list **by
  date (newest first)** or **by title (A–Z)**; the chosen order is written into `session_order` and then
  stays stable until the next Organize / new session / manual move. (`_open_organize_menu`,
  `organize_sessions`.)

### Session selector now highlights instantly on click
- Clicking a session title in the left picker felt laggy: the highlight only appeared *after* the session
  finished opening. `<<ListboxSelect>>` → `select_session()` → `open_session_in_new_tab()` runs all the
  heavy open work (create workspace, re-render list, load transcript, rebuild tabs) inside the same Tk
  event handler, so Tk deferred the selection-highlight redraw until that returned. `select_session` now
  calls `self.session_list.update_idletasks()` to flush the highlight paint *before* the open work blocks
  the event loop — the click highlights immediately, then the session loads.

### Account Limits popover no longer clipped
- The limits popover sized itself once on open, but usage data arrives asynchronously — when the extra
  window row (e.g. `sonnet`) landed, the body grew past the fixed height and clipped the Refresh/Close
  buttons. `_populate_limits_body` now re-fits the popover height each time it (re)populates.

### Work log is now paged (clickable Log column)
- The Work Log tab gained a **left column of "Log N" buttons** — work output rolls into a new page every
  ~300 lines (`WORK_LOG_PAGE_LINES`), so it's never one giant block and each page renders fast. The newest
  page is marked ● (live) and auto-follows new output; click any "Log N" to jump back to that chunk.
  (`append_work` now buffers into `work_pages`; `_show_work_page`/`_rebuild_work_page_buttons`/
  `_reset_work_pages`; `_clear_views` and `scroll_work_to_latest` updated.) Replaces the old line cap.

### Agent switching unblocked
- The agent dropdown had a busy-revert: if the current tab was running a turn (i.e. almost any time you
  reached for it), selecting another agent snapped right back — looked like "can't switch." Removed it.
  Switching now always works, shows the chosen agent's session list, gives status feedback, and never
  interrupts the running turn (backend keeps going; sending while busy still queues). Click a listed session
  to open it in a new tab on the fly. Also hardened the settings lookup (`.get`) so an odd agent key can't
  silently abort the switch.

### New-session picks the client first + per-attachment remove ✕
- **New session** now opens a client picker first (`_open_new_session_dialog` — lists Claude/Codex/Gemini/
  Ollama with Ready/Not-installed; custom clients always available) → then the name prompt → then creates
  the named session in its own tab (`_create_named_session`). No more guessing which agent you started.
- **Attachment bar is now per-file chips**, each with its own red **✕** (`remove_attachment`) so you can drop
  a single image; the existing button (renamed "Clear all") still removes everything.

### Skills menu: dividers under descriptions only + hover-reveal long titles
- Divider lines now sit **under the description column only** (inside a right-hand sub-frame); the title
  boxes float free with their own padding, no line cramming against them.
- **Long titles reveal on hover**: if a name is too long for its box (e.g. "Claude Automation Recomm…"),
  hovering it for 143ms (same delay as the session list) pops an overlay that extends the box rightward
  over the description to show the full name. Clears on leave / scroll / click / menu close.

### Skill popover connected to its chip + run-bare
- The prompt popover now **anchors directly above the chip you clicked** (was anchored to the skills-bar's
  left edge, so it floated far from the chip). Clamped on-screen so even a far-right chip's box stays visible.
- **Hard-connected look**: popover and the active chip share a blue accent border (popover overlaps the chip
  top by 2px so the borders merge) and the popover has a colored header with the skill name — clear which
  chip the box belongs to even with many chips. Chip un-highlights when the box closes.
- **Empty box is allowed** now: running a skill with no text sends just `/name`, so the skill uses its own
  prerequisites/defaults and asks you itself (in the conversation) instead of your text overriding them.
  Hint added to the box. (Skills don't have a native popup questionnaire — they ask conversationally; this
  lets that happen cleanly.)

### Skills menu redesign + scroll-wheel fix
- Rows are now two columns: the skill **name in its own color-coded box on the LEFT** (Title-Cased,
  width-aligned, ✓ when favorited), **description on the RIGHT** (muted, wraps). The name box alternates
  between two staggered colors only (`#26405c` regular / `#1e2c3d` faded) row-to-row.
- **Mouse wheel now scrolls the menu** — the canvas had no wheel binding (only scrollbar drag worked).
  Bound `<MouseWheel>` + `<Button-4>`/`<Button-5>` (Linux) to the canvas, rows frame, and every row.
- Clicking anywhere on a row toggles the favorite (rows are Frame+Labels now, not a single Button).
- Added a 1px `BORDER` divider after each row so descriptions read as separate rows, not one paragraph.
- **Readable descriptions**: raw `SKILL.md` text is model-facing ("This skill should be used when the user
  asks to…"). Added `SKILL_BLURBS` (clear one-line blurbs for all ~38 known skills) + `_humanize_skill_desc`
  (strips that boilerplate and keeps the first sentence) as a fallback for any unknown skill.

### Work log capped (fixes slowdown on long sessions)
- The Work Log `ScrolledText` grew unbounded — thousands of tool/system lines made Tk slow to
  insert/scroll/render. `append_work` now trims to the last `WORK_LOG_MAX_LINES` (2000) lines; old lines
  drop from VIEW only. The full record stays in the session file + `debug.jsonl`.
- CONFIRMED the work log is display-only and NOT part of the model's context window: `context_text` is sent
  to the Claude CLI only on a handoff's first turn (line ~3741); normal turns resume Claude's own session.
  So the "7%" context reading is accurate — the work log was never inflating it. The slowness was pure UI.

### Skills bar
- **`BUILTIN_SKILLS` constant** (14 entries) and **`discover_skills(cwd)`** added at module level, near
  `discover_external_sessions`. `discover_skills` scans `~/.claude/skills/*/SKILL.md` (personal),
  `<cwd>/.claude/skills/*/SKILL.md` (project), and plugin marketplace layouts; parses YAML frontmatter
  for `name:` / `description:`; built-ins win on name collision; result is sorted by name.
- **Skills bar** inserted between the composer_state row and the send bar. A `"✦ Skills"` button is
  pinned left; a chips wrapper expands to fill the remaining space with the chip frame centered in it
  (`pack(anchor="center")`), so 1–2 chips sit in the middle and the row grows outward as more are added.
- **Favorite chips** (`_render_skill_chips`): for each name in `self.skill_favorites` a small
  PANEL_ALT chip is rendered with a name button (opens prompt popover) and a `×` remove button.
- **`open_skills_menu`**: searchable `Toplevel` (transient, dark theme) lists all discovered skills.
  Favorited skills show a `✓` prefix and highlighted row. Clicking a row calls `_toggle_skill_favorite`
  and live-updates the list without closing the menu. Supports keyboard search via a `StringVar` trace.
  Positioned above the skills bar; toggling the button a second time closes the menu.
- **`_toggle_skill_favorite`**: adds or removes a name from `self.skill_favorites`, calls
  `_save_skill_favorites()` (writes `config["skill_favorites"]` to `CONFIG_FILE` non-durably), and
  re-renders chips.
- **`_open_skill_prompt`**: `overrideredirect` Toplevel anchored above the skills bar; shows
  `"✦ {name}"` title, a 3-line `Text` widget, and Run/Cancel buttons. Return key in the text box runs.
  Toggle behavior: clicking a chip while a popover is open closes it instead of stacking.
- **`_run_skill`**: validates text is non-empty; warns if the active agent is not Claude; appends
  `"✦ Skill: {name}"` system message; calls `self.send(prompt=f"/{name} {text.strip()}")` (explicit
  prompt skips reading/clearing the composer draft); logs `skill_run` via `_log_event`.
- **`_restore_workspace`** now calls `_render_skill_chips()` at the end so the chips bar is correct on
  tab switch (favorites are global, not per-tab).

### Qwen "beast mode" + Claude sub-agent fixes
- **Qwen was secretly still running aider** (the dumb-terminal code editor) — your only qwen agent was
  the `command: …aider…` client, NOT the agentic tool-loop. Added a startup migration: any custom client
  whose command contains `ollama_chat/<model>` is converted to a model-only client (drops the command),
  so it routes to the agentic `OllamaBackend`. Your `custom-qwen3-coder-30b` now runs the tool loop.
- **Expanded qwen's tools** from 3 → 5: `run_shell`, `read_file`, `write_file`, **`list_dir`**, **`web_fetch`**
  (HTTP GET any URL / REST API). Strengthened the system prompt: explicitly not sandboxed, can sudo dnf /
  systemctl / pactl / bluetoothctl / curl / git, must never claim it lacks access. Verified qwen tool-calls
  correctly with all 5. (Full MCP-client wiring is a larger future step; qwen reaches APIs now via
  web_fetch + curl in run_shell.)
- **Claude sub-agents — now you'll see more than 1.** Two fixes: (1) the orchestration policy said "use at
  most one worker by default" — loosened to fan out to 3–4 parallel workers for independent sub-tasks;
  (2) `subagent_stop` read `parent_tool_use_id` (always null in stream-json) so the live count never
  decremented — now reads the `tool_result.tool_use_id`, matching the Agent tool_use id, so the
  "Sub-agents N" count is accurate. The flow already worked; it just rarely fanned out and mis-counted.

### Tabs shrink-to-fit (not by age)
- Tabs now stay FULL-WIDTH and readable until they'd overflow the strip's right edge, then shrink
  uniformly to fit — instead of shrinking older tabs preemptively. New tabs still append on the right.
  Width-aware `maxlen` computed per render from `workspace_tabs_frame` width; reflows on window resize
  (`_on_win_configure`, width-gated so it can't loop). e.g. ~1–4 tabs full, ~10 tabs ≈11 chars each.

### Tab-open lag, click feedback, tab-limit popup
- **Opening a session is now instant.** Every tab-open / agent-switch / refresh was calling
  `discover_external_sessions`, which scanned ~132 Claude `.jsonl` files (plus Codex/Gemini) from disk —
  pure waste, since the picker is local-only. Removed from all 6 interactive paths (`external_sessions=[]`);
  only the unused def remains. (External "resume" can be re-added later as an on-demand action.)
- **Selected session title lights up** — added `selectforeground=white` + `exportselection=False` so the
  clicked row stays clearly highlighted (it was washed out / didn't read as selected).
- **10-tab limit now shows an on-screen popup** (`_notify_tab_limit` → `messagebox.showinfo`) in addition to
  the inline tab-strip label, wired into all three open paths (picker, New, ＋).

### Performance audit — fixed the stalling/hangups (CRITICAL)
Root causes found and fixed (all were blocking the UI thread with disk I/O):
- **`save_json` fsync'd on every write.** Added `durable=` param; high-frequency writes (config draft,
  session autosave) now skip fsync (still atomic via `os.replace`).
- **Every streamed token rewrote the whole session file + fsync** (`_append_assistant_chunk` → `store.save`),
  O(n²) per turn. Now updates the message in memory and autosaves at most every 2s (no fsync); the durable
  save happens at turn end. This was the big one.
- **`drain_events` re-saved config and rebuilt the tab bar after EVERY event** (hundreds/sec while
  streaming). Now batched: at most once per 50ms drain tick.
- **`config.json` write is now non-fsync** (`_persist_workspace_config` durable=False).
- A bad event can no longer stall the loop — `handle_event` is wrapped; errors are logged, not fatal.

### Queues run across tabs (the "30-minute" stall)
- A queued prompt in a BACKGROUND tab used to sit until you switched back (only the active tab drained on
  turn-done). New `_drain_workspace_queue` advances a background tab's queue automatically when its turn
  finishes, using that tab's own session/backend (never touches the active UI). Active tab unchanged.

### Accurate activity log
- New append-only `~/.config/agent-workbench/debug.jsonl` (timestamped JSON lines): `turn_start`,
  `turn_done` (with `elapsed_ms`), `queue_add`, `queue_drain` (active + background), `handler_error`.
  Cheap (no fsync), self-rotates at ~5MB. Tail it to see exactly what's slow or stuck.

### Dead code removed (~93 lines, 8 symbols)
- Deleted verified-unused: `title_from_claude_jsonl`, `SessionStore.list_for`, `_format_context_load`,
  `_current_session_context`, `_should_defer_chat_update`, `copy_latest_response`, `add_custom_client`,
  `launch_client_setup`. All confirmed zero-reference before deletion.

### Tabs: New = new tab, older tabs shrink, 10-tab cap
- The **New session** button now opens a NEW tab instead of swapping/replacing the current session.
  It never interrupts a running turn. (New sessions still come only from this button or a handoff.)
- **Max 10 tabs.** New/＋/cross-agent-open are blocked at the cap with a status message, and the tab strip
  shows an italic **"(10 tab limit reached)"** label in place of the ＋ button.
- **Older tabs shrink** — newest/active tab full-size; non-active tabs get progressively shorter labels and
  tighter padding the older they are, so new tabs always have room. (`_render_workspace_tabs_now`,
  `MAX_WORKSPACE_TABS=10`, `_at_tab_limit`.)
- NOTE: not deployed automatically — run `bash install.sh` when ready (deploy/restart is now user-initiated).

### Draft never lost (composer persistence) — CRITICAL
- **Queued messages no longer wipe what you're typing.** `_send_next_queued_prompt` used to delete the
  composer and stuff the queued text in before sending. If you'd started typing a new message after
  queuing one, that new text was destroyed when the turn finished. `send()` now takes an optional
  `prompt`/`attachments`; the queue sends DIRECTLY to the backend and never reads or clears the composer.
  Every `self.input.delete(...)` / `clear_attachments()` in `send()` is now guarded by `from_composer`.
- Composer draft is autosaved to config on a 150ms debounce and on close (`finalize_close` →
  `_persist_workspace_config`), and restored per-tab on restart via `_restore_workspace`.

### Local model is now a real tool-using agent
- `OllamaBackend` rewritten from chat-only into an agent loop with tools: `run_shell`, `read_file`,
  `write_file`. It runs commands on the machine, feeds results back, and iterates (180s/cmd timeout,
  25-step cap, Stop honored). Verified: qwen3-coder:30b ran `pactl list sinks short` and found the Echo Dot.
- Fixed: model id was sent as `ollama_chat/<name>` to `/api/chat` (now stripped to the bare name).
- Fixed: connected local models vanished after restart — startup only registered custom clients that had a
  `command`; now registers `command OR model`, so one-click-connected Ollama agents persist.
- To use: one-click "Connect local model" → green `<model>` agent (routes to OllamaBackend). The old
  `qwen-aider` custom client is a code-editor only; use the agent for system tasks.

### Session picker: per-agent + no surprise sessions
- Switching the agent dropdown now ONLY switches the agent and shows that agent's sessions. It does NOT
  open or create a session, and leaves the current conversation intact. New sessions come only from the
  New button or a handoff (`on_agent_changed` no longer calls `refresh_sessions`).
- Picker lists are filtered by agent (all working dirs), newest-first. `list_all_local(agent_key)`.
- Busy tab: switching agents is blocked with a message instead of spawning a tab/session.

### Open multiple sessions at once + no duplicate tabs
- EVERY picker click opens the session in its own tab; the current tab is never swapped/replaced.
- A session is matched **by id, not title** — so three different sessions that share a title each
  get their own tab, but the SAME session never opens twice. Re-selecting an already-open session focuses
  its existing tab (`open_session_in_new_tab` dedup loop). `select_session` now always delegates there;
  removed the old swap-in-place path and the `_session_in_other_tab` helper. Spawned-tab opens dedup too.

### Per-message timestamps
- Every message shows a local-time stamp (`H:MM:SS AM/PM`) next to the speaker, stored per item
  (`add_item` stamps `created_at`), on both stored and live-streaming paths.

### Store cleanup
- Picker shows only real created/new/handoff sessions (`_is_picker_session`): origin `local`, no
  `worker_job_id`/`worker_parent_session_id`, never `*-terminal` imports.
- Purged 178 empty imported `*-terminal` stub files from the store (backup tarball:
  `~/.config/agent-workbench/terminal-sessions-backup-20260616-225925.tar.gz`). Root sessions untouched.

---

## 2026-06-13 (deployed 2026-06-17)
- Status bar: workers moved left, model+state moved right; shows the REAL model from Claude's stream
  ("Opus Working…" / "Sonnet Working…").
- Terminal tab: startup banner + error surfacing + clear-on-restart.
- "Workers" badge → "Sub-agents"; counts Workbench workers + Claude in-turn Task sub-agents; click opens a
  popover above the badge.
- `CustomCliBackend` runs under a PTY + TERM (aider no longer "dumb terminal").
