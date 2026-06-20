# Agent Workbench — Changelog

Running log of every change, newest first. Source: `agent-workbench` (single Python/Tkinter file).
Deploy: `bash install.sh` (copies source → `~/.local/bin/agent-workbench`, app self-restarts after the
current turn). A change is only LIVE after a deploy + the app reloading.

---

## 2026-06-19 (Attach button to attachment bar; copy button copies full message)

- **Attach button moved to attachment bar** — previously in the skills bar (below the text
  input), now permanently anchored at the left edge of the attachment bar that sits above
  the text input (where file/image chips appear). The bar is always visible so Attach is
  always reachable, not just when a file is pending.
- **Clear all** button only appears in the attachment bar when there are pending attachments;
  hidden otherwise.
- **Copy button now copies the entire response**, not just the last chunk. A long reply from
  Claude can span multiple `agentMessage` items between tool calls; the previous code did
  `break` on the first one found in reverse order, silently dropping all earlier content.
  Fixed by joining all `agentMessage` parts with `"\n\n"`, matching how `_render_turn`
  already merges them for display.

## 2026-06-19 (Organize: bulk-delete sessions older than 30 days / delete all)

- **"Delete sessions older than 30 days…"** and **"Delete ALL sessions (keep current)…"**
  added to the Organize ▾ drop-down. Both skip any sessions currently open in a workspace
  tab. Deletes are permanent and preceded by a confirmation dialog. (`_bulk_delete_sessions`,
  wired into `_open_organize_menu`.)

## 2026-06-19 (Hard rule: sub-agent sessions never in tab bar; fix session scroll)

- **Sub-agent/workflow sessions are now banned from the workspace tab bar** (hard rule).
  Three-part guard: (1) `open_session_in_new_tab` silently returns if the session has
  `worker_job_id` or `worker_parent_session_id`; (2) `_open_selected_spawned` no longer
  calls open-in-tab — clicking a Spawned entry just echoes its title in the status bar;
  (3) `_evict_subagent_workspace_tabs` runs at startup to close any sub-agent tabs that
  were persisted in the saved workspace config (cleaning up ones already open).
- **Session list scroll wheel fixed** — both `_session_wheel` (main session list) and
  `_recent_wheel` (recent-sessions pane) now call `yview_scroll` explicitly and return
  `"break"`, instead of returning `None` and relying on class-level propagation which
  stopped working after the modal-lock bindings were added.

## 2026-06-19 (AWBfixes1 remainder: scroll bleed + redundant working label)

- **`recent_session_list` scroll bleed** — the "Open new agent" and "Add client" modal dialogs blocked
  `session_list` scrolling via `_modal_scroll_lock`, but `recent_session_list` had no such guard. Added
  the same `<MouseWheel>/<Button-4>/<Button-5>` → `return "break"` bindings so the recent-sessions pane
  is also frozen while a modal is open. (AWBfixes1 #1 — fully complete now.)
- **Removed model name from active-turn status badge** — the prompt-state label at bottom-right showed
  `"Opus · 2m 15s"` right next to the "Working" activity badge, making it redundant (two things saying
  "the agent is working"). It now shows only `"2m 15s · streamed ~N tokens"` while busy; the agent/model
  is already visible in the tab + selector. (AWBfixes1 #2.)

## 2026-06-19 (Add-agent-client dialog: scrollbar + black buffer)

The earlier scroll fix landed on `open_new_agent_dialog`, but the user's actual dialog was the
"+ Clients" → **`open_add_client_dialog`** ("Connect an agent client"), which still looked unchanged.
Fixed it there too:
- **Scrollbar thumb never moved** — the canvas had `command→yview` but was MISSING
  `yscrollcommand=results_scrollbar.set` (the return path). Added it; the thumb now tracks position.
- **Black buffer below the list** — `results_outer` was packed `fill="x"` (no vertical expand), so a
  taller window dumped the extra height into black space. Changed to `fill="both", expand=True` so the
  canvas grows with the window, and added the same `scrollregion=bbox("all")` + `dialog.maxsize`
  content cap as the new-agent dialog: dragging the bottom reveals more models, then stops.

(Deploy crash from the prior entry: user confirmed **Deploy now works**.)

---

## 2026-06-19 (Hand Off Deploy CRASH fixed + button sizing + new-agent scroll)

### Hand Off "Deploy" crash — ROOT CAUSE found and fixed
- Captured the real traceback (added a `handoff-error.log` writer to the deploy error handler):
  `_validate_handoff_plan` → `ensure_project_registry(root='/home/zito')` → `save_json('')` →
  `os.makedirs('')` → `FileNotFoundError: [Errno 2] ''`.
- Cause: `ensure_project_registry` checked `os.path.isdir(root)` (home passes) but then called
  `project_registry_path(root)`, which returns `''` for the home dir (home is guarded), and
  proceeded to `save_json('')`. Any session whose cwd is the home directory (e.g. the mirrored
  "Pig Farm 8") crashed Deploy here.
- Fix: `ensure_project_registry` now returns `""` immediately when `project_registry_path` is empty,
  BEFORE save_json. Validation only *warns* on a missing registry (not an error), so Deploy now
  proceeds and succeeds for home-cwd sessions instead of crashing.

### Footer buttons uniform size
- Send / Attach / Stop / Hand Off / State were different widths (looked sloppy). All now use a fixed
  `width=8` (chars) so they match.

### New-agent dialog scroll
- Scrollbar thumb didn't reflect the scroll position: after all rows are built, the scrollregion is
  now set to span the full content (`bbox("all")`), so the thumb sizes and moves correctly.
- Resizing the dialog taller showed a black buffer below the list: the window max-height is now
  capped to the content height (`dialog.maxsize`), so dragging the bottom reveals more agent rows
  and then stops — no empty black area.

---

## 2026-06-19 (footer reorder, usage %-hard-lock, modal scroll fixes)

From the UIchange-footer1.webm / glitching2.webm batch:

1. **Footer right-group reordered** to `[Context Limit] [Hand Off] [State]`. State is packed first
   (far right, above Send), Context Limit packed last (leftmost of the group) so when its text widens
   on compaction it grows LEFT into the chip area instead of shoving Hand Off / State leftward — the
   thing the user disliked. (`skills_bar` build.)
   - **State button** = `open_project_state` → opens AGENT_STATE.md (project shared state) in the
     editor. Documented here for reference.
2. **Removed the duplicate top compaction banner.** `update_context_indicator`: the
   "This session has compacted N×…" banner (shown when compacted at low context) is suppressed
   (`show_banner=False`) — the footer "Context Limit … compacted N×" badge already conveys it. The
   genuinely-useful high-context (≥warning/critical) and rate-limit banners still show.
3. **Usage badge HARD-LOCKED to percentages.** Removed the `local_stats` "N req/24h" fallback from
   both `claude_usage_limits()` (no longer returns request counts at all) and `_display_usage()`
   (deleted the local-stats branch). Source is the OAuth endpoint (5h/week utilization %, verified
   reachable: 7%/4%). On a transient OAuth failure the badge keeps the last-good % or shows "--" —
   it will NEVER show request counts again.
4. **Connect-client dialog scroll fixed (Linux).** `_scroll_results` used `event.delta` + only bound
   `<MouseWheel>` — dead on X11. Now handles `<Button-4>/<Button-5>` (event.num) too, bound via an
   Enter/Leave-scoped `bind_all`. Dialog is now modal+topmost.
5. **Background session list can't scroll under a modal dialog.** Added `self._modal_scroll_lock`
   (incremented while the new-agent or connect-client dialog is open). The session Listbox's wheel
   handler returns `"break"` at the widget level while the lock is held, so it can't scroll
   underneath. Both dialogs are now grab+topmost+focus_force.

---

## 2026-06-19 (skills bar: stop blink + position jump on tab switch)

- `_render_skill_chips` destroyed and recreated every chip on EVERY tab switch, so the skills bar
  visibly blinked. Added a signature `(active_agent, tuple(favorites))`; the rebuild is skipped when
  nothing changed, so switching between same-agent tabs no longer flashes. Toggling a favorite still
  rebuilds (signature changes).
- The chip frame was `anchor="center"`, so a different agent's favorites (different total width)
  shifted the chips horizontally on switch. Changed to `anchor="w"` (left-aligned) for a stable
  position. (From ~/Videos/Screencasts/Glitching.webm.)

---

## 2026-06-19 (AWBfixes1: new-agent modal, status text, Hand Off deploy + title)

Batch from ~/AWBfixes1:
1. **New-agent dialog is now properly modal.** Added `-topmost` + `focus_force` (can't be lost
   behind other windows) on top of the existing `grab_set`. Fixed the scroll bleed: the mouse-wheel
   handler used `bind_all` (global), so scrolling the session list behind the dialog also scrolled
   the agent list. Now it only scrolls when the pointer is actually over the dialog
   (`winfo_containing(...).winfo_toplevel() is dialog`).
2. **Removed redundant "is working" text.** The activity line next to the status badge said
   "{model} is working · {elapsed}"; the badge already shows Working/Ready, so it's now
   "{model} · {elapsed}". The model name beside the badge identifies which agent is working.
3. **Hand Off "Deploy" hang fixed.** The dialog holds a modal `grab_set`; `_deploy_handoff` can pop
   its own modal (project-scope-conflict warning), which deadlocked against the dialog's grab — the
   classic "nothing happens" hang. `deploy()` now releases the grab before deploying (re-grabs only
   if aborted) and wraps the call in try/except that surfaces a real error dialog + traceback instead
   of silently hanging.
4. **Hand Off shows the title transition.** New "New tab title" row renders `old → [editable new]`
   with a ✏ hint. The new title defaults to the computed next title (e.g. "OG Agent Workbench 4 →
   OG Agent Workbench 5"), updates with the target agent's numbering, and is user-editable;
   `_deploy_handoff` gained a `title_override` param so the edited title is used.

---

## 2026-06-19 (DISABLE runaway live-session auto-open + tab dedup)

### Live-session auto-open hard-disabled (was spawning duplicate tabs every 5s)
- `poll_live_sessions` auto-opened a tab for any session whose transcript changed in the last 90s.
  Its dedup (`_known_source_ids`) didn't register an already-open session before the next 5s poll,
  so it re-opened the same sessions over and over — the UI filled with duplicate "OG Agent Workbench"
  tabs. Added `_AUTO_OPEN_LIVE_SESSIONS = False`: `_auto_open_live_session` and `poll_live_sessions`
  both early-return, so no tabs spawn and the 5s scan loop stops. Re-enable only after the dedup is
  reworked to reliably track auto-opened source ids.
- Added a **load-time tab dedup** in workspace restore: workspace_tabs sharing a
  `source_session_id` (or session id) collapse to the first, so any duplicates that got persisted
  don't pile back up on restart. Blank tabs (no session) are always kept.

---

## 2026-06-19 (live-session auto-detect: Claude/Codex/Gemini)

### Externally-started sessions now auto-open as mirror tabs
- Added `poll_live_sessions()` — runs every 5 seconds, scans for Claude JSONL files, Codex
  SQLite threads, and Gemini session files modified in the last 90 seconds that are NOT already
  open in any AWB workspace tab.
- When a live external session is detected, it's instantly opened as a read-only mirror tab
  (same `open_session_in_new_tab` path used by the manual session picker).
- If at the 10-tab limit, shows a status-bar alert instead of silently dropping it.
- Covers all three clients: Claude Code (`~/.claude/projects/`), Codex (`~/.codex/state_5.sqlite`),
  Gemini (`~/.gemini/tmp/*/chats/session-*.jsonl`).
- Sessions started from Termius, plain terminal, or any other SSH connection appear in AWB
  within 5 seconds without any manual action.
- Opens in the **background** (`background=True`) — does NOT steal focus from the tab you're
  working in. Status bar shows "Live session detected → new tab: …" as the only signal.
- Added `_known_source_ids()` helper — checks all workspaces so AWB-managed sessions are
  never double-opened.
- `open_session_in_new_tab` gains `background=False` parameter; when True, restores the
  previously-active workspace after building the new tab.

---

## 2026-06-18 (filter harness-injected turns from the mirror)

### Machine-injected turns no longer render as "YOU" bubbles
- Claude Code stores several machine messages as USER-role transcript turns (so the model sees
  them). AWB's `claude_jsonl_turns` rendered every user-role text turn as a YOU bubble, so these
  showed up as giant chunks "from the user" — not what was typed in the terminal. Culprits found on
  the live transcript: `<task-notification>` background-agent completion notices (4×, 5–9 KB),
  `<system-reminder>` blocks, the AWB attachment wrapper ("The user attached the following local
  files…"), and — the big one the user kept seeing — the **post-compaction continuation summary**
  ("This session is being continued from a previous conversation…", 3× at 13–17 KB each).
- Added `HARNESS_INJECTION_BLOCK` regex + `strip_harness_injections(text)`: removes the tagged
  blocks (`<task-notification>`, `<system-reminder>`, `<local-command-*>`, `<session_context>`),
  drops the "This session is being continued…" compaction summary, and runs the existing
  `_strip_attachment_injection` to keep only the real request after an attachment wrapper. In
  `claude_jsonl_turns`, if nothing user-authored remains the turn flushes the prior assistant text
  at the boundary but renders NO YOU bubble; the assistant's reply still renders as its own bubble.
- Filter lives at the PARSER, so it cleans the rendered chat, the stored `turns`, AND the Hand Off
  packet at once. Simulated on the real transcript: 7 machine turns skipped (4 task-notification +
  3 compaction summary), all 62 real user turns preserved (attachment turns cleaned to just the
  request). Existing tabs refresh on next open/switch (re-parse).

---

## 2026-06-18 (Hand Off freshness + sync audit)

### Hand Off now captures the conversation to the last word
- `handoff_session` built the packet from `session["turns"]` as of the last 2s external poll.
  Turns typed in the terminal in the ~2s before clicking Hand Off could be missing from the packet.
- Added `_sync_session_from_transcript(session)`: a SYNCHRONOUS re-read of the linked transcript
  (`claude_jsonl_turns` + `claude_session_metadata` for Claude; codex/gemini equivalents) that
  refreshes `session["turns"]` and `["context"]` (and the indicator) right before the packet stages.
  `handoff_session` calls it before `_refresh_handoff_stage`. Hand Off is now lossless w.r.t. terminal turns.

### Audit findings (no code change needed)
- **Scrollbar vs context % is NOT a bug.** The chat scrollbar thumb is auto-sized by Tk =
  viewport/total-rendered-height; `claude_jsonl_turns` renders the ENTIRE transcript (all
  pre-compaction history + long messages), so a long session = tiny thumb. The context badge is the
  LIVE window only (`used/limit` from the latest turn's usage). Independent measures; both correct.
- **Context sharing for a terminal-driven mirrored session works** (verified to the token: transcript
  247,714 = 24.8% → badge "25%/248K/1M"). AGENT_STATE.md is written fresh to disk before each handoff
  (`request_project_state_update(force=True)`); the packet references its path (intentional, keeps the
  packet small; continuation reads current state from disk).

---

## 2026-06-18 (New-agent dialog: scrollable model list)

### "Open a new agent" dialog now scrolls
- The dialog packed every agent + local-model row straight into `body` with no scroll
  container and `resizable(False, False)`. With 8+ local Ollama models the list ran off the
  bottom of the screen with no way to reach the lower entries (or the Escape/close affordance).
- Wrapped the rows in a capped-height (`460px`) `Canvas` + `Scrollbar` (`scroll_content`),
  with mouse-wheel support (`<MouseWheel>` / `<Button-4>` / `<Button-5>`, bound while the modal
  is open and unbound on `<Destroy>`). Dialog is now `resizable(False, True)` so it can grow.
- Deduped the second `_list_ollama_models()` probe (reuses the one from the install check).

---

## 2026-06-18 (mirrored session: context shared; live re-render REVERTED as freeze risk)

### Shared context — confirmed accurate
- A Claude session driven from the terminal is mirrored in AWB as `origin: "local"` with a
  `source_path` to the Claude transcript. `poll_external_session` re-reads the transcript every 2s
  and `update_context_indicator` shows the REAL shared context %. VERIFIED against the live
  transcript: latest turn used 247,714 tokens = 24.8%, compacted 3× → AWB displayed "25% · 248K/1M ·
  compacted 3×". Accurate to the token. `store.save` runs for any local sync so the record persists.
- The mirror path never triggers a send — pure display (reads turns, queues
  `external_session_loaded`, no turn creation).

### REVERTED: live re-render of terminal turns
- A prior attempt made idle `origin == "local"` sessions fall through to a FULL `_clear_views` +
  `_render_session` on every 2s poll, so terminal-driven turns would appear live. On a large active
  session that destroys+rebuilds 50+ chat bubbles (and their embedded Copy buttons) every 2 seconds —
  a real freeze/stutter risk, the opposite of what the user needs. Reverted: local sessions skip the
  re-render (early-return) as before. Context still updates every poll (it's computed before the
  early-return); new terminal turns are in `current_session["turns"]` and paint on tab open/switch.
  Showing them live would need an INCREMENTAL append (delta only), not a full re-render — deferred.
- STILL OPEN: image attachments render as a 2nd raw `[Image: source: /path]` YOU bubble.

---

## 2026-06-18 (Ollama "Not installed" fix + work-log freeze fix)

### New-agent dialog: Ollama no longer shows "Not installed"
- `open_new_agent_dialog` checked every base agent for a CLI executable in PATH. Ollama is
  HTTP-backed (no `ollama` binary needed), so it always failed the check and the "Open tab"
  button was disabled. Now `agent_key == "ollama"` is "Ready" when the local server is reachable
  (`_list_ollama_models() is not None`), reusing the same probe the Local-models list already does.

### Work-log render freeze (O(n²)) — fixed
- `_insert_work_entry` called `yview()` + `see("end")` after every line, forcing a full layout
  recompute per entry. Loading a session with a huge work log (runaway agent turn) ground the UI
  to a halt (main thread pegged for minutes). Added `_suspend_work_autoscroll`: `_render_session`
  sets it for the whole bulk render so entries insert with no per-line scroll; one `see("end")` at
  the end. The work log is persisted, so this had to land before restarting or the app re-freezes.

---

## 2026-06-18 (usage = real % again, per-client skills, interrupt REVERTED)

### Claude usage badge shows real 5h / weekly PERCENTAGES again (not request counts)
- **Root cause:** `claude -p /usage` on a Max subscription returns only local request
  counts ("Last 24h · N requests"), NOT the 5h/weekly utilization percentages. An earlier
  fix this day embraced the request-count format ("N req/24h · M req/7d"). The user wants
  the percentages back — the same ones claude.ai and the interactive `/usage` gauge show.
- **Fix:** New `_claude_oauth_usage()` calls the real source the TUI gauge uses —
  `GET https://api.anthropic.com/api/oauth/usage` with the OAuth token from
  `~/.claude/.credentials.json` (`anthropic-beta: oauth-2025-04-20`). Parses
  `five_hour.utilization` → "5h", `seven_day.utilization` → "week",
  `seven_day_sonnet.utilization` → "sonnet". `claude_usage_limits()` now returns these as
  normal `windows` (same shape as Codex), so the badge renders "Usage: 10% 5h · 45% week".
- `claude -p /usage` local request-count parsing is kept as a **fallback** if the endpoint
  is unreachable or the token is missing. Verified live against the account (matches claude.ai).

### Skills bar is now PER-CLIENT
- `discover_skills(cwd, agent_key)` is agent-aware: Claude → BUILTIN + `~/.claude/skills` + plugins;
  Codex → `~/.codex/skills/**`; Gemini → `~/.gemini/commands/**`; local/Ollama → none.
- `skill_favorites` are now per-agent (`skill_favorites_by_agent`), migrating the old flat list
  into the Claude bucket. The bar + menu re-render for the active tab's client; empty state for
  clients with no skills. (Verified: Claude 39, Codex 5, Gemini 0, Ollama 0.)

### Interrupt & Send — REVERTED (user rejected it)
- The "[ Queue ] [ ⚡ Interrupt & Send ]" banner added earlier today was fully removed.
  Send-while-busy now silently QUEUES (terminal-style) and the running turn finishes;
  **Stop is the only thing that interrupts a turn.** All banner UI, helpers, and dismiss
  hooks removed; `send()`'s busy branch is back to `self._queue_prompt(...)`.

---

## 2026-06-18 (Ollama as a single agent + queue editor fix)

### Ollama is now ONE agent in the menu with a model picker
- Added a base `{"key": "ollama", "label": "Ollama"}` agent spec alongside Codex/Claude/Gemini.
  Installed local models are now chosen in the **model picker** (`_model_options_for("ollama")` →
  `"Default"` + live `/api/tags` list, cached 8s) instead of every model being its own menu entry.
- `_create_backend_set` now always builds a base `"ollama"` OllamaBackend; per-model custom_clients
  with an `ollama_chat` model are **no longer registered as separate agent entries** (they cluttered
  the menu). Real CLI custom clients (those with a launch command) are unaffected.
- `OllamaBackend` constructed with no fixed model; `start_turn` resolves the live model from the
  session's backend settings each turn. `"Default"`/empty → `_resolve_ollama_model()` auto-picks an
  installed model (prefers qwen3-coder:30b, then qwen3:14b, else first available).
- Added `"ollama"` to EFFORT_OPTIONS / DEFAULT_AGENT_SETTINGS and the settings-validation loop.
- NOTE: this is the single-agent + model-picker layer. Multi-model **sub-agent distribution**
  (different Ollama models for different sub-tasks) is the next layer, not yet built.

### Queue editor: white cursor, reliable copy/paste/cut, accurate Saved state
- Insertion cursor changed to solid white (`insertbackground="#ffffff"`).
- Dirty/Saved is now computed by comparing the editor content to the loaded baseline
  (`_loaded_text`) on `<KeyRelease>` — arrow keys, Ctrl+C, and modifier presses no longer produce a
  false "unsaved" state; undoing an edit back to the original flips the button back to **Saved**.
- Explicit clipboard handlers (`_detail_copy/_cut/_paste/_select_all`) bound to Ctrl+C/X/V/A (upper
  and lower case) and the `<<Copy/Cut/Paste>>` virtual events, driving CLIPBOARD directly so Linux
  PRIMARY-vs-CLIPBOARD inconsistency is gone. Each returns `"break"` to stop double-handling.

### Reverted: Queue-vs-Interrupt "Interrupt & Send" banner
- Removed entirely. Sending while a session is busy **queues silently** again (previous behavior).
  Only the **Stop** button interrupts a running turn — sending a message never does.
  (The earlier "interrupt-and-send" entry below is superseded by this revert.)

---

## 2026-06-18 (per-client skills bar)

### Client-aware Skills bar
- `discover_skills(cwd)` is now `discover_skills(cwd, agent_key="claude")` and branches on the active agent:
  - **Claude** — unchanged (BUILTIN_SKILLS + `~/.claude/skills` + project `.claude/skills` + plugins).
  - **Codex** — recursive scan of `~/.codex/skills/**/SKILL.md`; parses the same YAML frontmatter (name/description). Includes `.system/` skills (imagegen, skill-creator, etc.).
  - **Gemini** — recursive scan of `~/.gemini/commands/**/*.toml`; name = file stem (or `subdir:stem`), description from `description = "..."` line if present. Currently empty on this machine but wired.
  - **Ollama/local/custom** — returns `[]` immediately (no skills concept).
  - Shared frontmatter parsing extracted into `_parse_skill_md_frontmatter()` to eliminate duplication.
- `skill_favorites` is now **per-agent**: stored in config under `skill_favorites_by_agent = {"claude": [...], "codex": [...], ...}`.
  - **Migration:** if `skill_favorites_by_agent` is absent but old flat `skill_favorites` list exists, it is seeded into the `"claude"` bucket automatically.
  - New `_agent_favorites(agent_key)` helper returns the mutable list for a given agent, creating an empty entry on first access.
  - `_save_skill_favorites` now writes `skill_favorites_by_agent` to config.
- `_render_skill_chips` reads `_agent_favorites(active_agent)` so chips update when switching tabs.
- `open_skills_menu` passes the active agent key to `discover_skills`, shows a "Skills for: Claude/Codex/Gemini" header strip, and shows "No skills available for this client." when the list is empty (Ollama/local).
- `_toggle_skill_favorite` resolves the active agent and mutates only that agent's favorites list.
- `_restore_workspace` comment updated: favorites are now per-agent, not global.

---

## 2026-06-18 (interrupt-and-send)

### Queue vs Interrupt & Send choice banner
- When `send()` is called while the session is busy, instead of silently queueing,
  an inline orange-bordered banner now appears above the controls bar with two buttons:
  **Queue** (existing behavior) and **⚡ Interrupt & Send** (queues the message AND
  calls `backend.interrupt()` so the queued message fires immediately after the interrupted turn ends).
- Banner auto-dismisses on: choice made, workspace tab switch, or turn_done.
- Composer text is cleared after the banner appears (same as before), so the draft is
  not lost inside the banner's pending choice.
- No modal dialog; fully inline between the Skills bar and the status/controls bar.

---

## 2026-06-18 (state injection rendering fix)

### SB-010 — project_state_context: wrap output in session_context tags
- **Root cause:** PROJECT SHARED STATE injection was prepended to user messages as raw text,
  not wrapped in `<session_context>` tags. `visible_user_prompt_text` detected the prefix
  (`has_hidden_prefix = True`) but the fallback branch only stripped single-line "Also read..."
  patterns — leaving the entire multi-paragraph AGENT_STATE block visible as a YOU bubble.
- **Fix:** `project_state_context()` now wraps its output in `<session_context>…</session_context>`.
  The existing `strip_session_context` path in `visible_user_prompt_text` (line 572) already
  handles this tag correctly and was already the right machinery — it just wasn't being reached
  because the injection wasn't tagged. No changes to stripping logic needed.

---

## 2026-06-18 (Ollama write-guard)

### SB-009 (v2) — request_project_state_update: require direct title match; removed scored fallback
- **Root cause of v1 failure:** `session_candidate_root_scores` (the `scored` check) was truthy for the
  "Next Agent Workbench" Codex session against OG AWB's root because that session's JSONL contained
  OG AWB file paths — they were injected into context from the shared source file reference. This made
  `alias_only = False` and bypassed the guard.
- **Fix:** Removed `scored` entirely from the write guard. Auto-writes now require `_project_root_from_title`
  to return the same root as `infer_project_root`. If the title doesn't directly name a known project
  directory, no background AGENT_STATE write occurs, regardless of path-score evidence.

### SB-009 (v1) — request_project_state_update: alias-only inference no longer auto-writes AGENT_STATE
- **Root cause:** Ollama's `local_project_state_summary` was overwriting OG AWB's `AGENT_STATE.md`
  with stale "Agent Workbench Next" Codex session content. A Codex tab titled "Next Agent Workbench"
  resolved (correctly, for read/injection) to OG AWB via the registry alias lookup, but then
  `request_project_state_update` auto-wrote that Codex session's content to OG AWB's state file.
- **Fix:** Added an alias-only guard in `request_project_state_update`. If the root was resolved
  only by alias (i.e. `_project_root_from_title` returns no direct match AND
  `session_candidate_root_scores` returns no path-score evidence), the auto-write is skipped.
  The project-state indicator is still updated (read is still valid); only the write is blocked.
  Explicit user-triggered updates (`update_project_state()`, `force=True`) bypass the guard.

---

## 2026-06-18 (usage display + status bar)

### Usage panel takes over half the screen — fixed
- **Root cause:** `claude -p /usage` on Claude Code Max subscription returns a multi-paragraph
  local-stats block ("What's contributing to your limits usage? Last 24h · 3330 requests…") instead
  of the API-rate-limit format. The entire block was stored as `error` and then set via
  `self.status.set(...)` which expanded the status bar label to fill vertical space.
- **Fix 1 (source):** error path in `usage_updated` handler now only writes the first line of the
  error to the status bar (`full_error.split("\n")[0]`).
- **Fix 2 (systemic):** Added a `trace_add("write", …)` guard on `self.status` StringVar that
  clamps any multi-line text to its first line immediately after any `.set()` call. This protects
  the status bar against future multi-line content from any code path.
- **Fix 3 (badge):** `claude_usage_limits` now parses the local-stats format
  ("Last 24h · N requests · M sessions") and synthesises a `label_text` field. `_display_usage`
  shows "Usage: N req/24h · M req/7d" in the badge instead of "--" for Max subscribers.

## 2026-06-18 (lower-severity cleanup batch)

### DEAD-001 — codex_history_prompts: deleted dead function
- `codex_history_prompts()` had zero call sites. Removed entirely.

### DEAD-005 — _stream_stderr: deduplicated from ClaudeBackend and GeminiBackend
- Identical `_stream_stderr` methods in both backends moved to `StreamCliBackend` parent. Both call sites
  resolve through MRO automatically.

### DEAD-008 — migrate_legacy_config: removed permanently-dead migration
- `migrate_legacy_config()` and its `App.__init__` call removed. The `CONFIG_DIR` exists on any machine
  that has run the app; the early-return guard fired every startup. Migration window from
  codex-conversation-viewer → agent-workbench has long closed.

### DEAD-002 — _working_status_text: deleted unused method
- `App._working_status_text()` had zero call sites. Removed.

### DEAD-003 — ClaudeBackend: deleted unused visible_chunks/emitted_visible
- `visible_chunks = []` and `emitted_visible = False` in `ClaudeBackend.start_turn` were never read;
  copy-paste leftovers from GeminiBackend. Removed.

### DEAD-004 — _restore_workspace: removed stale self-attribute assignments
- `self.session_context_active` and `self.session_context_buffer` were set from workspace dict but never
  read (all live code reads from the workspace dict directly). Removed.

### DEAD-009 — _block_vertical_tab_wheel: deleted unused method
- `App._block_vertical_tab_wheel()` was never bound or called. Removed.

### SB-005 — new_handoff_session: removed home-dir cwd fallback
- Changed `cwd=project_root or source.get('cwd') or os.path.expanduser('~')` to use `''` instead of
  home as the floor. Home is not a meaningful project directory and misled scope-conflict checks.

### SB-007 / HO-005 — structured_handoff_packet: removed dead home_state_path replacement
- `home_state_path = project_state_path(os.path.expanduser('~'))` always returns `''` (home guard).
  The `packet.replace(...)` call was permanently unreachable. Three lines removed.

### AWB-003 — check_client_updates: destroy guard + TclError protection
- Added `finalizing_close` guard before `self.win.after(0, ...)` and wrapped the call in
  `try/except Exception` to silently discard TclError if the window is destroyed while the
  background check runs (up to 25s per spec).

### AWB-004 — animate_activity: added finalizing_close guard
- Added `if self.finalizing_close: return` as first line of `animate_activity`, matching the pattern
  used by `refresh_prompt_state` and `poll_usage`. Prevents StringVar mutation and timer reschedule
  during teardown.

### AWB-004 (Gemini) — GeminiBackend: turn_done now reflects actual result status
- `turn_done` was always emitted with `status='completed'` regardless of Gemini result. Now emits
  `status='error'` when the result event's status is not 'success'. Fixes suppressed error indicators
  and blocked retry logic for failed Gemini turns.

### AWB-006 (image label) — preview_selected_artifact: fixed layout split on text preview
- `artifact_preview_image_label` was always packed from init and never hidden when text preview was
  shown. Now pack_forget'd before branching and re-packed in image/unavailable branches.
  `_clear_artifact_preview` also re-packs the label after clearing.

### AWB-006 (PTY) — CustomCliBackend: kill zombie PTY processes after wait() timeout
- After `running.wait(timeout=5)` in the `finally` block, if `poll()` is still None, now calls
  `os.killpg(SIGKILL)` (falling back to `running.kill()`) to prevent orphaned PTY children.

### AWB-007 — StringVar traces: explicit trace_remove on popup/dialog close
- `search_var` trace in skill popup and `mode_var` trace in handoff dialog are now removed in their
  respective close handlers via `trace_remove`, preventing Tcl-level callbacks firing against
  destroyed widget trees.

### AWB-008 (tab order) — _render_workspace_tabs_now: order_sig committed after loop
- `self._workspace_tabs_order_sig` is now assigned after the tab-packing loop completes rather than
  before it, so a TclError mid-loop doesn't permanently suppress re-renders.

### AWB-008 (rollout) — codex_rollout_turns: apply visible_user_prompt_text at parse time
- `userMessage` items are now stored with `visible_user_prompt_text(raw)` applied, so injected AWB
  preambles don't appear as visible user messages when old rollout files are displayed.

### HO-002 / HO-003 — handoff_summary_text: filter 'project registry:' and registry injection lines
- Added `"project registry:"` and `"also read the project registry before acting"` to the per-line
  skip filter. Added regex to strip `^Also read the project registry before acting:` from raw text.
  Added `"also read the project registry before acting"` to `visible_user_prompt_text` has_hidden_prefix
  tuple (belt-and-suspenders).

---

## 2026-06-18 (bug-fix batch)

### SB-001 — infer_project_root: deleted dead/dangerous fallback lines
- Removed lines that re-returned `/home/zito` as project root when `find_project_root(cwd)` resolved to
  the home directory but `cwd` itself was not home. The preceding guard (`root != home → return root`)
  already covers the valid case; the deleted lines were unreachable for valid roots and incorrectly
  returned home for invalid ones.

### SB-003 — project_registry_path, project_memory_dir: home-dir guard added
- Both functions now return `""` when `cwd` resolves to the bare home directory, matching the existing
  guard in `project_state_path`. Prevents structured handoff packets from emitting
  `~/.agent-workbench/project.json` for unresolved sessions and stops the receiving agent being directed
  to read a cross-project registry file.

### SB-004 — alias/slug normaliser: two-pass suffix strip for "Session N" / "Day N" patterns
- `_project_title_slugs` and `_project_root_from_registry_aliases` now strip counter-noun + digit suffixes
  (`Session 7`, `Day 3`, `Round 14`, etc.) before the existing bare-digit strip. Both passes run in order
  so "Pig Farm Session 7" → "Pig Farm" and "Pig Farm 7" → "Pig Farm" both resolve to the same alias.

### SB-008 — project_scope_conflict / infer_project_root: shared expected-root helper
- Extracted `_infer_expected_root(session, fallback_cwd)` (delegates to `infer_project_root`). Both
  `project_scope_conflict` and `infer_project_root` now derive the expected root from the same code path,
  eliminating the divergence where conflict detection used `self OR title OR alias` short-circuit while
  inference used a more complex stored-root reconciliation.

### AWB-002 — ClaudeBackend: session_id write guarded by self.lock
- Background reader thread that writes `session["backend"]["session_id"]` on `system/init` events now
  acquires `self.lock` (the same lock used to guard `self.running`) before the dict mutation, eliminating
  the race with main-thread readers of `session["backend"]`.

### AWB-003 — GeminiBackend: session_id write guarded by self.lock
- Identical race to AWB-002; same fix applied. GeminiBackend inherits `self.lock` from StreamCliBackend.

### AWB-005 — CodexBackend: thread_id / active_threads guarded by self.lock
- `_handle_notification` thread/created write, `ensure_session` early-return read, post-wait writes, and
  `restart` clear/reset are all now wrapped in `with self.lock`. `interrupt` snapshots `thread_id` and
  `turn_id` under the lock before issuing the request, preventing a race with `restart`.

### AWB-001 (tab render) — pack_forget TclError no longer skips pack
- Changed `continue` to `pass` in the `pack_forget` except-TclError handler inside
  `_render_workspace_tabs_now`. Previously a TclError on a brand-new (never-packed) frame would
  `continue` past the `pack()` call, leaving the tab invisible until a full re-render was triggered.

### AWB-002 (update dialog) — work thread guards against destroyed window/dialog
- `work()` closure in `open_client_updates_dialog` now wraps `self.win.after(0, done)` in
  `try/except TclError`, and `done()` returns early if `dialog.winfo_exists()` is False. Prevents
  TclError crashes when the update dialog or main window is closed while a 600-second update runs in
  the background.

### AWB-001 (Ollama semaphore) — OllamaBackend.start_turn acquires _OLLAMA_INFERENCE_SEM
- Interactive Ollama turns now acquire the module-level GPU semaphore (blocking) before the inference
  loop and release it in a `finally` block. This serialises concurrent Ollama sessions and simultaneous
  `local_project_state_summary` calls, preventing two HTTP inference requests from hitting the GPU at
  the same time.

### HO-001 — visible_user_prompt_text: fallback for payloads without </session_context>
- Added a fallback branch (mirrors `handoff_summary_text`) that strips known AWB prefix lines and stray
  `<session_context>` blocks when `has_hidden_prefix` is True but the `</session_context>` sentinel is
  absent. Previously such payloads silently returned `""`, losing the user's actual prompt. Only
  activates for old-format payloads that predate the time-context injection.

---

## 2026-06-18

### Session bleed fix — bidirectional cross-project state injection eliminated
- **Root cause:** `infer_project_root` failed to match "Next Agent Workbench" (session title) to the
  `Agent Workbench Next` directory because the title slug ("next-agent-workbench") didn't match the
  directory name ("Agent Workbench Next"). The fallback `session_candidate_root_scores` then found
  Pig Farm file paths in the stored Codex JSONL (from prior injected context) and returned the Pig
  Farm root — causing all subsequent Codex turns in that tab to receive Pig Farm AGENT_STATE.
- **Fix 1 — word-rotation slugs:** `_project_title_slugs` now also generates a first-word-rotated
  variant (e.g. "Next Agent Workbench" → slug "agent-workbench-next") so `_project_root_from_title`
  can directly find the correct directory without any additional lookup.
- **Fix 2 — registry alias lookup:** new `_project_root_from_registry_aliases` function scans all
  known project directories for `.agent-workbench/project.json` files and matches the session title
  against registered `aliases`. Called from `infer_project_root` before falling through to path
  scoring, so a registered alias always wins over content-derived paths. "Next Agent Workbench" is
  already in the OG AWB `project.json` aliases, so it resolves correctly.
- **Fix 3 — conflict detection:** `project_scope_conflict` now also uses the alias lookup when
  `_project_root_from_title` fails, so the conflict-guard UI works for alias-matched sessions too.
- **Root cause 2 (bidirectional bleed):** Every Codex session has `cwd = /home/zito` in the DB
  (Codex always uses home). Sessions whose titles fail all lookups fell through to returning
  `/home/zito` as the project root. A stale `/home/zito/AGENT_STATE.md` with AWB handoff content
  was then injected into Pig Farm sessions (and vice versa) as "PROJECT SHARED STATE."
- **Fix 4 — never treat home dir as project root:** `infer_project_root` final fallback now
  returns `""` when the resolved root is the home directory. `project_state_path` also guards
  against home dir so no state file is read/written there. This eliminates the AGENT_STATE
  cross-contamination for all unresolvable sessions. Stale `/home/zito/AGENT_STATE.md`
  archived to `AGENT_STATE.md.stale`.

### Attachment injection + AGENT_STATE no longer visible in conversation
- **Root cause:** `visible_user_prompt_text` stripped `PROJECT SHARED STATE` headers and
  `<session_context>` time blocks but NOT the AWB file-attachment injection wrapper
  (`"The user attached the following local files..."`) that follows them. Codex echoes the
  full request payload (context + time block + attachment injection + real message) as a
  `userMessage` stored in its JSONL; AWB was rendering that echo as a visible YOU bubble.
- **Fix:** added `_strip_attachment_injection()` which recognises the attachment wrapper prefix
  and extracts only the text after `"User request:\n"`. Applied at the end of
  `visible_user_prompt_text` (all paths) so every rendered user message in the conversation —
  both live and from stored/external transcripts — is clean.
- Applied the same strip in `handoff_summary_text` so attachment wrapper text can't leak
  into handoff packets as fake "user requests".

### GPU overload / freeze / tab-blink fixes
- **Ollama concurrency cap (fixes GPU overloading + system shutdowns):** `local_project_state_summary`
  now acquires a module-level `threading.Semaphore(1)` before calling Ollama. If another inference is
  already running it returns immediately and falls back to the deterministic state writer. This prevents
  multiple simultaneous `qwen3:8b` GPU inferences (triggered by many tabs completing turns at once) from
  stacking up and triggering the AMD DATA FABRIC SYNC FLOOD hard-shutdown.
- **`poll_external_session` no longer calls `_save_active_workspace` every 500ms (fixes UI freeze):**
  `_save_active_workspace` reads the entire composer text widget on the Tk main thread; doing that 2×/sec
  was a primary freeze source. The watchdog still saves every 2s. Poll interval also slowed 500ms → 2000ms.
- **Tab switch no longer blinks all tabs (fixes glitching):** `_render_workspace_tabs_now` now tracks an
  `order_sig` (just the tab sequence). Only when the sequence changes (new tab, closed tab, reorder) are
  frames `pack_forget`+`pack`ed. For color/selection-only changes (e.g. switching active tab), tabs are
  updated in-place with `configure()` only — no frames disappear and reappear.

### Project-local handoff filesystem + existing-session targets
- Handoff deployment can now target either a new continuation or an existing same-project session for the
  selected agent. Existing-session handoffs attach a one-turn pending handoff context, focus/open the target
  session, and send the continuation prompt without replaying the handoff on future turns.
- Project memory now has a stronger hard-drive contract: `AGENT_STATE.md` stays at the project root,
  `.agent-workbench/project.json` stores project identity/related roots/client metadata, and generated
  handoff packets are written into `.agent-workbench/handoffs/` with timestamped files plus `latest.md`.
- Hidden shared-state context now includes the absolute project root and registered related roots in addition
  to the canonical state file, registry file, and project id.
- The project-scope guard now respects registered related roots from `.agent-workbench/project.json`, so this
  Agent Workbench session can legitimately hand off work that includes the related Agent Workbench Next repo
  without being blocked as cross-project contamination.

### OGAWB fixes file follow-up
- Read the actual `/home/zito/OGAWBfixes.md` file (lowercase `f`), which listed five remaining issues:
  selector wheel behavior, arrow-key navigation, Work Log find, tab blink, and sub-tab white blink.
- The Work Log selector now scrolls without a visible scrollbar, matching the requested "scroll the whole set"
  behavior without selecting pages on wheel movement.
- Clicking a `Log N` button now focuses that selector item so arrow/page/home/end navigation works immediately.
- Work Log Find now supports exact matching and fallback all-word phrase matching, then jumps to and highlights
  the matching page.
- Workspace tab buttons and Workbench sub-tabs now suppress default focus/highlight borders and keep dark active,
  pressed, and focus colors to reduce white flashes when clicked.

### Work Log page selector is internally scrollable
- Fixed the overflow shown in the latest screenshot: when a session has many Work Log pages, the `Log N`
  selector now scrolls inside its own column instead of extending down into the composer/status area.
- Mouse wheel over the selector scrolls the selector list; arrow/page/home/end keys still change the
  selected Work Log page and keep the selected page visible.

### Work Log scroll no longer blinks through pages
- Fixed the blink shown in `/home/zito/Videos/Screencasts/Screencast_20260618_172958.webm`: mouse-wheel movement over the Work Log page selector no longer rapidly switches `Log N` pages.
- Work Log page buttons now update their selected/live styles in place instead of destroying and recreating every button on each page change.
- Re-selecting the already-visible Work Log page no longer clears and reinserts the text pane.

### OG responsiveness + work-log usability pass
- Added Work Log controls for exporting the full log, exporting the current log page, and finding the log page that contains a search term.
- Work Log now opens on the newest/live page; wheel over the selector scrolls the selector list, while arrow/page/home/end navigates pages.
- Workspace tabs now reuse existing tab widgets instead of destroying/recreating the whole tab strip on every selected/status change, reducing blink when switching tabs or streaming work.
- Composer draft persistence is debounced without snapshotting the active workspace on every keystroke, reducing typing latency.
- File drag/drop now accepts `file://` drops from desktop file managers and reports when a drop contains no readable files, so Markdown files such as `/home/zito/Documents/OGagentworkbenchfixes.md` can attach normally.
- Opening a saved session now restores that session's own agent and working directory before the next send, reducing the chance of an old tab launching work in the wrong project.
- Busy tabs restored from `Starting` now normalize to `Working` once a turn has actually started, including background tabs checked by the watchdog.

### Model selection no longer looks like it changed at send time
- Confirmed through `debug.jsonl` that some recent Codex turns really launched with `gpt-5.4` while other
  tabs launched with `gpt-5.5`; this was not just user perception.
- Turn launch now captures the visible dropdown model/effort into per-workspace `running_model` /
  `running_effort` before starting the backend, syncs the workspace/session immediately, and logs previous
  versus launch settings for future audits.
- The working badge now prefers the captured launch model/effort while a turn is running, so stale
  session/workspace settings cannot make the footer say the wrong model.
- Opening a session now shows `Ready. Next turn: <model - effort>.` so per-session model restores are
  visible before pressing Enter.

### Project registry + handoff validation
- Added per-project `.agent-workbench/project.json` metadata with a stable project id, root, state file,
  aliases, and per-client last-session/sequence data. This makes project identity explicit instead of
  relying only on title/cwd inference.
- Hidden shared-state context and handoff packets now include the project registry path when available, so
  new clients can read both human/model state (`AGENT_STATE.md`) and machine-readable project metadata.
- Handoff deploy now runs a validation pass before creating the continuation. It blocks unresolved project
  roots, unknown target clients, blank titles, and duplicate target-client titles for the same project; it
  logs successful validations and non-blocking warnings.

### Single active worker indicator
- Removed the duplicate routine `model - effort is working...` text from the left footer hint. The
  right-side working badge remains the single live worker/model indicator with model, effort, elapsed time,
  and token details; the left hint is reserved for warnings, errors, and other status messages.

### Per-client handoff title sequencing
- Handoff titles now sequence against the **target client's own sessions** for the inferred project, not the
  source client's open session list. Example: Claude `Pig Farm 6` handed to fresh Codex becomes `Pig Farm`,
  Codex `Pig Farm 3` handed back to Claude becomes `Pig Farm 7`, and Claude `Pig Farm 10` handed back to
  Codex becomes `Pig Farm 4`.
- Cross-client handoff tabs now initialize with the target agent's cwd/model/effort/session list before
  opening the continuation session, preventing the new tab from briefly inheriting the source client's
  picker state.

### Hidden project-state echo suppression
- Backend `userMessage` echoes from Codex/Gemini are now treated as request echoes, not new user-authored
  messages, so Workbench no longer creates surprise blue bubbles from the payload it sent internally.
- Saved transcript rendering now strips Workbench-only `PROJECT SHARED STATE` / handoff bootstrap context
  and shows only the real prompt after the authoritative time block. Existing native Codex transcripts that
  already persisted the hidden payload will render cleanly after reload.
- Handoff summaries and turn summaries now use the same visible-user-text sanitizer, preventing recursive
  project-state dumps from being inherited into future handoffs.
- Codex `userMessage` item-start notifications are hidden from the work log; they are backend lifecycle
  noise, not useful user activity.

### Usage-exhausted tabs + cross-project handoff guard
- Workspace tabs now turn **red** when that client/workspace reports usage at 100% or no remaining quota.
  Red takes precedence over working yellow, completed green, and normal ready tabs; matching-agent tabs also
  inherit the red state when one workspace has account-level telemetry for that agent.
- The lower running status now shows the actual model/effort instead of the client name, e.g.
  `gpt-5.4-mini - medium is working...`; the same formatter covers Codex, Claude, Gemini, and connected
  Ollama/local-model clients.
- Workspace tab switching is more responsive: config persistence is debounced, transcript redraw starts
  after the tab has visually switched, redraw batches are smaller, and artifact previews are deferred until
  selected instead of being read immediately during every tab restore.
- Project-state fallback updates no longer append the previous `AGENT_STATE.md` as a recursive
  `Prior State Snapshot`, and the local/Ollama summarizer receives old state with prior snapshots stripped.
  This stops stale cross-project state from poisoning future project memory.
- Vertical mouse-wheel events over tab controls are blocked from switching tabs. Horizontal wheel events
  (including MX Master-style Button-6/Button-7 and Shift+wheel) can still move through tabs, while normal
  pane scrolling and Ctrl-wheel text zoom remain unchanged.
- Stale broad roots such as `/home/zito` no longer override a specific project title/root such as
  `/home/zito/the-pig-farm`, and a handoff is no longer blocked by one old inherited path when the current
  session evidence overwhelmingly points at the titled project.
- Automatic handoffs are capped more tightly and ignore inherited `PROJECT SHARED STATE` / "read this
  previous handoff" bootstrap wrappers when choosing the next session's objective, preventing recursive
  context growth during model-to-model handoff chains.
- Generated handoffs rewrite stale `/home/zito/AGENT_STATE.md` references to the inferred project-local
  state file, so old bad packets do not keep poisoning new Pig Farm continuations.
- Added a project-scope conflict guard for handoffs and project-state updates. If a session title resolves
  to one project (for example Pig Farm) but the handoff/session evidence points at another project (for
  example Agent Workbench Next), Workbench now blocks update/handoff/copy/worker/send-first-handoff actions
  and shows a scope-mismatch warning instead of launching a contaminated continuation.

### Automatic project-state routing and visible state indicator
- `AGENT_STATE.md` is now automatic for normal use: completed/error turns, staged handoffs, copied
  handoffs, worker handoffs, and deployed handoffs refresh the inferred project state without requiring
  `Options -> Update project state`.
- Project-state routing now infers the real project root from touched files and commands first, then from
  session title/project directories, before falling back to the selected cwd. This prevents broad sessions
  like `/home/zito` from writing Pig Farm context into `/home/zito/AGENT_STATE.md`; Pig Farm resolves to
  `/home/zito/the-pig-farm/AGENT_STATE.md`.
- Added a front-row **State** button next to Hand Off/Context showing missing/updating/fresh state. It opens
  the active session's inferred `AGENT_STATE.md` directly, so evidence that state was written is visible
  during normal work.
- The main conversation header now includes the active client (`Codex: Pig Farm`, `Claude: Pig Farm 8`,
  etc.) so switching tabs makes the current agent obvious.

### Project-state update no longer freezes the UI
- Fixed **Options → Update project state** blocking the Tk event loop while local Ollama summarized a
  handoff. Manual project-state refreshes now run in a background thread and report completion in the
  status bar.
- Fast handoff/copy/open paths now create/update `AGENT_STATE.md` with the deterministic fallback instead
  of waiting on a local LLM, so usage-limit handoffs stay responsive even if Ollama is slow, cold-starting,
  or missing the configured model.

### Shared project state + immediate effort changes
- Added repo-local **`AGENT_STATE.md`** support for every project: Workbench can update a durable shared
  project memory file from the current session/handoff, and future turns inject the file path plus a bounded
  excerpt for Claude, Codex, Gemini, and local-model clients. Handoff packets now include the shared state
  path too.
- Project-state updates use **local Ollama** for the mechanical summarization step when available
  (`qwen3:8b` default), falling back to a deterministic Markdown state if Ollama is offline. This keeps
  cloud tokens out of routine "compress this handoff into project memory" work.
- **Effort/model dropdown changes now take immediate effect**: the active workspace, current session backend,
  saved agent defaults, and persisted workspace config all update in one path, so the next turn/queued turn
  uses the selected effort instead of a stale one.

### Artifact copy + usage-limit handoff
- Artifact previews are now true read-only text views instead of disabled text widgets, so selecting text
  no longer turns the preview unreadable/black. `Ctrl+C`, `Ctrl+A`, right-click Copy/Copy all, and the
  artifact-list **Copy contents** command now work for handoff files.
- Added **Copy packet** in the handoff dialog and **Options → Copy current handoff** for manual cross-client
  continuation without deploying a new tab.
- The **Hand Off** button now also wakes up when the active client's usage telemetry is near exhausted
  (90%+ in any reported window), not only when context is 70%+ or compacted. Usage-limit pressure also
  stages a durable `HANDOFF.md`, so a Claude limit can be handed to Codex/Gemini/Ollama cleanly.

### Codex sidebar shows full native session history again
- Restored Codex native history in the Workbench sidebar without bringing back the slow all-client scan:
  Codex sessions are read directly from `~/.codex/state_5.sqlite`, with no 100-row cap and no eager rollout
  transcript parsing. Opening a native Codex row loads the full rollout on demand.
- Fixed merge/dedupe so Workbench-local sessions linked to a Codex thread keep their friendly Workbench
  label (e.g. "Next Agent Workbench") while the matching native row is hidden. Worker/child sessions still
  stay out of the main picker.
- Named Workbench Codex sessions now sync their title back to Codex's native thread record and fill
  `source_session_id`/`source_path`, so the Codex terminal history uses the same label after restart.

### Per-session scope charter (push back on wrong-chat requests)
- New **Options → "Session scope / charter…"**: describe what a session is for (e.g. "Pig Farm trading
  only — do NOT edit Agent Workbench"). It's injected into that session's system prompt so the agent
  pushes back on clearly off-scope requests ("this isn't the right chat for that") and asks before
  proceeding — and **STOPS instead of acting when running unattended**, including when a handoff inherited
  an off-scope objective. Opt-in: blank = no effect (zero behavior change until set). The charter **carries
  forward through handoffs** so a whole lineage (Pig Farm 7→8→9) stays scoped. Applies to Claude sessions;
  works in every orchestration mode (smart/ultra/direct). (`session_charter_prompt`, `session["charter"]`,
  `open_session_charter_dialog`.) Soft guardrail / smoke detector, not a hard lock — pairs well with giving
  sessions their real project cwd.

### Usage popover no longer clipped; usage auto-shows on every tab
- **Cut-off fixed:** the limits popover opened with its left edge pinned to the badge's x; since the badge
  sits near the right of the window, it ran off the right screen edge and clipped the reset times. It's now
  **right-aligned under the badge and clamped on-screen** (helper `_place_popover`), applied both on open and
  on the async re-fit when usage arrives — so the reset timestamps are always fully visible.
- **Auto-display fixed:** `_restore_workspace` only showed *cached* usage on activation, so a freshly
  opened/switched tab sat on "Usage --" until the 90s poll or a manual click. Now activating a tab also
  **fetches usage in the background** (cached shows instantly, fresh replaces it) — combined with the
  persisted per-workspace cache, the badge never sits blank waiting for a click.

### Handoff cross-session audit + strict session-isolation guard
- **Audit result (a Pig Farm 7→8 handoff referenced Agent Workbench work):** the handoff machinery is NOT
  at fault — `structured_handoff_packet` and the whole stage/deploy path read only from the source
  session's own turns, every backend/app event stamps `workspace_id`, and no two sessions share a backend
  session-id. The Agent Workbench text was genuinely present in Pig Farm 7's stored turns (real
  `userMessage`s sent into that tab — all sessions share `cwd=/home/zito`, so nothing flagged it as
  off-project), and the handoff faithfully carried it forward.
- **Defense-in-depth guard:** `handle_event` could previously let an event with **no `workspace_id`** fall
  through and write into whatever session was in the foreground. Added `SESSION_MUTATING_KINDS`; any
  unattributed session-mutating event (assistant/work/user/turn_done/external_session_loaded/subagent/…)
  is now **dropped and logged** instead of applied to the active session — one session can no longer bleed
  into another even on a future regression. (No behavior change today; nothing currently emits
  unattributed mutating events.)

### Bottom bar: one status indicator, smaller input, corner buffer
- **No more two "Ready"s.** The green status badge moved from the far left to the **right** (just left of
  the token readout), and the white prompt-state no longer prints a redundant "Ready" — it now shows only
  the token/queue readout (blank when idle and no turn has run). One status indicator, on the right.
- **Smaller composer** — the prompt input dropped from 3 rows to 2.
- **Bottom buffer panel** added below the controls bar, plus left/right corner spacing on Sub-agents and
  Send, so those buttons aren't jammed into the window corners.

### Usage badge updates in real time; relabels; Hand Off beside Context Limit
- **Real-time 5h/weekly usage:** the badge refreshed only every 5 min (or on click). Now it also refreshes
  **immediately after every turn completes** (when usage actually changes) and the background poll dropped
  from 5 min → **90 s**. (`refresh_usage` on `turn_done`; `poll_usage` interval.)
- **Fixed stuck green "Starting":** when a **local** Claude session finished syncing it set the status to
  "synchronized" but never reset the activity badge, so it sat on the initial "Starting." It now goes to
  **Ready** (idle) when not busy — matching the non-local sync path.
- **Hand Off moved to the RIGHT of the Skills bar, beside Context Limit %** (they go hand in hand). Order is
  now `✦ Skills · …chips… · Hand Off · Context Limit %`.
- **Relabels:** the context badge "Active …" → **"Context Limit …"**, and the top usage badge "Limits" →
  **"Usage"** (popover header "Account Limits" → "Account Usage") to avoid confusing the two.

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
