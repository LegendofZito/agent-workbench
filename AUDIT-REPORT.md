# Agent Workbench — Audit Report (2026-06-20)

Automated audit: 24 chunked Sonnet readers + per-finding adversarial verifiers (102 agents). 74 findings survived verification. This report lists what was applied and what remains.

## ✅ Auto-applied (13) — see commits a2341e8, bd0e0c5

- **_handle_notification** (L4347, high/bug): When item['content'] is a non-empty list, it is assigned directly to 'text', bypassing the fallback loop that extracts text from structured content blocks.
- **update_project_state** (L10959, high/bug): _project_state_update_running is never reset when win.after() raises TclError, permanently blocking future calls.
- **_bulk_delete_sessions** (L13228, high/bug): Bulk delete does not tombstone deleted sessions and does not remove client-side files, so deleted external sessions reappear in the picker on next refresh.
- **_queue_prompt** (L17192, high/bug): Unconditionally wipes the composer and attachments even when the send was programmatic (not from the composer), destroying any draft the user has typed.
- **codex_sessions_for_cwd** (L2252, medium/bug): SQLite3 connection is never closed, leaking a file descriptor on every call.
- **ensure_project_registry** (L3226, medium/bug): When a dict entry in related_roots has neither 'root' nor 'path' key, clean_text(None) produces '' and os.path.abspath('') resolves to the process CWD, which is a valid existing directory, so it gets spuriously appended to related_roots.
- **refresh_prompt_state** (L9864, medium/bug): model variable is computed but never used in the text string, wasting a call to _working_model_effort_label on every 1-second tick.
- **show_edit_menu** (L10591, medium/bug): Select-all in the edit context menu selects the trailing implicit newline ("end") unlike every other select-all in the file ("end-1c").
- **move_selected_session** (L13363, medium/bug): Wrong status message shown when no session is selected and no filter is active.
- **format_token_usage** (L894, low/dead_code): The branch `if not parts and limit and total_tokens` at line 894 is unreachable dead code.
- **infer_project_root** (L3098, low/dead_code): The `if title_root: return title_root` branch at line 3098 is unreachable dead code.
- **row_bg** (L8883, low/dead_code): `row_bg` is assigned but never read inside `_open_subagents_popover`.
- **refresh_sessions** (L12777, low/dead_code): The else branch in refresh_sessions is unreachable because self.sessions is always non-empty at that point.

## ⛔ Rejected (1) — would introduce a bug, NOT applied

- **_handoff_context_text** (L14999): The else-branch of _handoff_context_text ('Continue from the attached handoff context.') is unreachable because every caller guards the call with `if handoff_artifact else packet`.  
  Reason kept: removing the else makes `intro` unbound (UnboundLocalError) if any caller passes a falsy artifact — it's a defensive default, not truly dead.

## 🐛 Bugs not yet applied — medium (17)

- **gemini_session_index** (L1926): `@lru_cache(maxsize=1)` on a disk-scanning function means new Gemini session files created after app start are permanently invisible until process restart.
  - fix: 
- **codex_usage_limits** (L3796): codex_usage_limits passes the raw resets_at value (likely an ISO 8601 string) directly to format_reset_time, which calls float(timestamp) and silently returns '' on ValueError, so Codex reset times are always blank.
  - fix: 
- **_read_stdout** (L4295): self.pending.pop() is called without holding self.lock, creating inconsistent synchronization with the locked writes in request() and the unlocked clear() in restart().
  - fix: 
- **_handle_notification** (L4438): When thread/created or thread/resumed notifications arrive, active_threads is not updated, causing ensure_session to create a duplicate thread on the next call.
  - fix: 
- **OllamaBackend.start_turn** (L4988): turn_done event is emitted outside the try-finally block, so a raise in the preceding emit() leaves the session permanently stuck in 'running' state.
  - fix: 
- **GeminiBackend.start_turn** (L5627): GeminiBackend emits turn_done status='completed' even when the turn was stopped early via stop_flag, incorrectly marking aborted turns as successful.
  - fix: 
- **_working_workspace_labels** (L6807): Busy marker ' •' is silently dropped from window-title labels when the session title is long, because shorten() truncates it before endswith(' •') can match.
  - fix: 
- **_build_ui** (L7579): work_pages_scroll scrollbar is created and wired but never packed, so the work-log page-button list has no visible scrollbar even when pages overflow.
  - fix: 
- **_open_skill_prompt** (L8452): Clicking any skill chip while a popover is open always closes and returns, so clicking a different chip never opens its popover.
  - fix: 
- **_display_session_title** (L12470): Alias set for claude-terminal sessions is never displayed because the function returns before the alias check.
  - fix: 
- **_linkify_chat_range** (L14376): Tkinter `link_N` tags and their `tag_bind` callbacks are never deleted when the chat is cleared, leaking memory and event bindings on every session switch.
  - fix: 
- **_open_new_session_dialog** (L14788): Ollama always appears as 'Not installed' in the New Session dialog because the ollama-reachability check present in the agent picker is absent here.
  - fix: 
- **spawn_worker_job** (L15398): Worker sessions never store handoff_base_title or handoff_sequence, breaking the title-chaining sequence for downstream handoffs from a worker.
  - fix: 
- **_do_add_mcp** (L16230): MCP entry is appended to secrets and saved before subprocess registration succeeds, so a `shlex.split` ValueError (malformed command with unclosed quote) persists a broken entry and shows a confusing 'Saved; register error' message instead of blocking the save.
  - fix: 
- **open_handoff_options_dialog** (L17126): Missing WM_DELETE_WINDOW protocol binding leaves an orphaned StringVar trace when the dialog is closed with the title-bar X button.
  - fix: 
- **handle_event** (L18186): Active-workspace turn_done handler does not reset live_subagents or live_token_count on the workspace dict, leaving stale values visible after a turn ends.
  - fix: 
- **request_close** (L18416): request_close uses close_when_idle without excluding restart_after_close, so pressing close while a restart is queued shows a misleading 'will close automatically' info dialog instead of letting the user override or cancel the restart.
  - fix: 

## 🐛 Bugs not yet applied — low (13)

- **sanitize_session_context_stream** (L655): Dead branch 'if not chunk' is unreachable because 'raw' is already guaranteed non-empty before 'chunk = buffer + raw' is computed.
  - fix: 
- **codex_thread_metadata** (L1441): The `finally` block references `con` which may be unbound if `sqlite3.connect()` raises before assignment, causing a silent `NameError` swallowed by the inner `except Exception: pass`.
  - fix: 
- **_paths_from_command** (L2741): When a command starts with `cd`, the target path is appended to `paths` twice.
  - fix: 
- **codex_usage_limits** (L3791): Falsy-zero bug: when window_minutes is absent or null, `minutes` is 0 and the condition `minutes and minutes <= 360` is False, so a missing-minutes primary 5h window is mislabeled 'week'.
  - fix: 
- **_ollama_model_options** (L8672): `models or []` collapses `None` (Ollama unreachable) and `[]` (no models installed) into the same cached value, masking the error state for 8 seconds.
  - fix: 
- **save_edit** (L9637): After saving, _loaded_text[0] is set to the raw widget content (possibly with leading/trailing whitespace) while the persisted prompt was clean_text-stripped, so the displayed text and the stored value silently diverge.
  - fix: 
- **_open_limits_popover** (L10181): Toggle-close path clears _limits_popover but leaves _limits_popover_populate and _limits_popover_body pointing at stale closures from the destroyed popover.
  - fix: 
- **submit_terminal_command** (L11682): Calling clear_terminal() before sending 'clear'/'reset' to the shell causes a visible double-clear because the shell's ANSI response also triggers clear_terminal().
  - fix: 
- **_terminal_send** (L11625): Second send() after restart_terminal() silently swallows failure if the new shell also fails to start.
  - fix: 
- **_deploy_handoff_to_existing** (L15317): Bare source.get('id') at line 15317 will raise AttributeError if source is None, despite the method's own earlier defensive `(source or {}).get(...)` pattern at lines 15244-15245.
  - fix: 
- **open_handoff_dialog** (L16742): The 'New tab title' row is always visible even when 'Existing session' mode is selected, where the title field is meaningless.
  - fix: 
- **handle_event** (L18058): subagent_stop marks an agent complete only if its status is exactly 'running', missing 'in_progress' and 'pending' states that the rest of the codebase treats as active.
  - fix: 
- **drain_events** (L18393): processed=True is set unconditionally after a handle_event exception, so a corrupted/unhandled event still triggers a workspace config save and tab re-render on the same tick.
  - fix: 

## ♻️ Redundant (14)

- **_infer_expected_root** (L3023, low): `_infer_expected_root` is a one-line wrapper for `infer_project_root` with a false docstring, called only once.
- **ensure_project_registry** (L3187, low): The `if path else {}` ternary has a dead else-branch: path is guaranteed truthy by the early-return guard three lines above.
- **OllamaBackend.TOOL_NAMES** (L4691, low): TOOL_NAMES manually duplicates the five tool names already declared in the TOOLS class attribute, creating a synchronization hazard.
- **CustomCliBackend.start_turn** (L5032, low): The cwd variable is computed inside the aider hint block (line 5032) and then unconditionally recomputed with the identical expression three lines later (line 5051).
- **_evict_subagent_workspace_tabs** (L6223, low): `keep` is computed at line 6223 but never used; `self.workspace_order` is reassigned by recomputing the equivalent filter at line 6234.
- **_apply_secrets_env** (L6025, low): `_apply_secrets_env` redundantly guards `_injected_env` initialization that `_load_secrets` already guarantees.
- **_build_ui** (L7864, low): spawned_list binds both <<ListboxSelect>> and <Double-Button-1> to the same _open_selected_spawned() method, causing it to fire twice on every double-click.
- **open_add_client_dialog** (L12067, low): action_text variable is assigned the constant string 'Connect' and used only once, making it needless.
- **_artifact_items_for_session** (L12619, low): Manual fileChange path extraction (lines 12619-12623) is a strict subset of what _collect_artifact_paths already does on the same item at line 12624.
- **rename_selected_session** (L13503, low): For local sessions where source_updated is True, session['title'] = alias and session_aliases.pop() are executed twice.
- **open_session** (L13732, low): Empty `if loading_transcript: pass` branch immediately followed by a duplicate `if not loading_transcript:` block, producing two separate checks for the same condition where the first does nothing.
- **_render_item** (L14127, low): `self.latest_agent_text = visible_text` is set before calling `append_chat`, which unconditionally overwrites it with the same value.
- **_make_turn** (L17179, low): Double `.get("title")` call: the second `.get("title", "")` is redundant because its result is only evaluated when the first `.get("title")` already returned a truthy value.
- **handle_event** (L18222, low): refresh_usage(manual=False) is called twice in the same turn_done handler path, separated by ~35 lines.

## ♻️ Simplify (5)

- **ensure_local_delegate_mcp_config** (L96, low): Intermediate variable 'model' is assigned the module-level constant LOCAL_DELEGATE_DEFAULT_MODEL and used exactly once, adding no clarity.
- **project_scope_conflict** (L3052, low): The `expected_hits and` guard before `expected_hits >= max(3, ...)` is redundant.
- **_update_worker_indicator** (L8839, low): `_active_worker_jobs()` is called twice unnecessarily in the same function.
- **_on_provider_change** (L16082, low): The 'Custom env var' row is always visible in the layout; hiding it by setting fg=PANEL (background color) is a color-hack that leaves the row occupying space and the label text invisible but still present in the layout.
- **handle_event** (L18065, low): elif kind == 'assistant_begin': pass is an explicit no-op branch that adds noise without value.

## 📋 Report-only — flagged by verifier as risky/behavioral (11)

- **delete_selected_session** (L13398, high/bug, CONFIRMED): Busy guard only checks the active workspace, allowing deletion of a session that is mid-turn in a background workspace tab.
  - The bug is real and provable from the code. Lines 13398-13404 check only `self.busy` and `self.current_session`, which reflect the active (foreground) workspace. Background workspaces track their own 
- **split_gemini_visible_text** (L502, medium/bug, CONFIRMED): Function returns the entire raw text as 'thought' and empty string as 'visible' when a [thought:] marker is present, so any Gemini message containing a thought block produces no visible assistant output.
  - The function at lines 502-508 is provably wrong. When `[thought:` IS present in the text, line 508 executes `return raw, ""` — returning the entire unmodified text as `thought_text` and an empty strin
- **ClaudeBackend.start_turn** (L5323, medium/bug, CONFIRMED): context_text is silently dropped on all non-first turns; the condition guards injection only when first_turn is True, so any context supplied by the caller on a resumed session is discarded without warning.
  - The code at lines 5322-5324 of agent-workbench is exactly as described: `payload = prompt; if context_text and first_turn: payload = context_text.strip() + "\n\n" + prompt.strip()`. The `first_turn` g
- **render_queue** (L9498, medium/bug, CONFIRMED): render_queue always resets the listbox selection to item 0, so any external _refresh_queue_dialog call while the user is editing a non-zero item jumps them back to item 0 and silently discards the dirty edit context.
  - The bug is provably real from the code. `render_queue()` (line 9486) unconditionally calls `queue_list.selection_set(0)` (line 9499) and `show_selected()` (line 9502) with no guard for a preexisting s
- **render_local_models** (L12139, medium/bug, CONFIRMED): Network call to Ollama blocks the main Tkinter UI thread for up to 1.5 seconds on every Search click.
  - The code at line 12139 directly calls `self._list_ollama_models()` inside `render_local_models()`, which is bound as `command=render_local_models` to the "Search for local models" button at line 12244
- **remove_custom_client** (L12365, medium/bug, CONFIRMED): Busy guard only checks the active workspace; a custom backend running in a background workspace is closed mid-turn without warning.
  - The bug is real and provable from the code. At line 12365, the guard is `if self.busy and self.active_agent.get() == key`. `self.busy` is loaded exclusively from the active workspace at line 6408 (`se
- **switch_workspace** (L6513, low/bug, PLAUSIBLE): _schedule_workspace_config_save(immediate=False) is called before active_workspace_id is updated, so its deferred callback (350 ms later) saves the wrong (new) workspace instead of the old one.
  - The code at lines 6509-6519 does match the described sequence: line 6512 calls _save_active_workspace() synchronously (saving the old workspace into the in-memory dict), line 6513 schedules a deferred
- **_render_workspace_tabs_now** (L7107, low/redundant, CONFIRMED): The three .configure() calls for frame, button, and close are duplicated verbatim in both branches of the if is_new or needs_reorder block.
  - The code at lines 7102-7147 confirms the finding verbatim. In the `if is_new or needs_reorder:` branch (lines 7107-7124), the three `.configure()` calls for `tab["frame"]`, `tab["button"]`, and `tab["
- **show_selected** (L9612, low/bug, CONFIRMED): show_selected sets _loaded_text[0] = prompt (clean_text-stripped) before calling _mark_saved, but if render_queue fires while the user has unsaved edits in a different item it overwrites the dirty context without warning.
  - The bug is provably real. The code path is: `_refresh_queue_dialog()` (lines 17200, 17220 - triggered by external queue-add and queue-drain events while the dialog is open) → `render_queue()` (line 88
- **_known_source_ids** (L13844, low/dead_code, CONFIRMED): `_known_source_ids` is only called from `poll_live_sessions` after the feature-disabled early-return guard, making it unreachable at runtime.
  - `_known_source_ids` is defined at line 13844 and has exactly one call site at line 13891 inside `poll_live_sessions`. That call is unreachable because `poll_live_sessions` has an unconditional early-r
- **_auto_open_live_session** (L13864, low/dead_code, CONFIRMED): `_auto_open_live_session` is only called from within `poll_live_sessions` after the feature-disabled early-return guard, making it unreachable at runtime.
  - `_AUTO_OPEN_LIVE_SESSIONS = False` at line 13862. `poll_live_sessions` (line 13884) returns immediately at lines 13887-13888 (`if not self._AUTO_OPEN_LIVE_SESSIONS: return`) before reaching any of the