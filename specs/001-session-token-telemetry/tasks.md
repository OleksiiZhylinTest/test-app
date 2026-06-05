# Tasks: Agentic SDLC Token Consumption Telemetry

**Input**: Design documents from `specs/001-session-token-telemetry/`

**Prerequisites**: plan.md ✓ | spec.md ✓ | research.md ✓ | data-model.md ✓ | contracts/ ✓

**Note**: This feature is implemented retroactively. Tasks reflect the actual implementation and serve as a verification checklist. All tasks marked ✅ are complete; tasks without ✅ require verification against quickstart.md scenarios.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared state)
- **[Story]**: User story this task belongs to (US1/US2/US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify the hook wiring and output directory configuration.

- [x] T001 Verify Stop hook wiring in `.claude/settings.local.json` (Stop event → `post_stop_notify.sh`)
- [x] T002 Verify `generated/debug/` is listed in `.gitignore` so reports are not committed

---

## Phase 2: Foundational (Core Parsing Infrastructure)

**Purpose**: Core transcript parsing that all three user stories depend on. Must be complete before any story can deliver its output.

**⚠️ CRITICAL**: No user story output is possible until this phase is complete.

- [x] T003 Implement `_load_transcript(path)` with UTF-8 encoding and UUID-based deduplication in `tools/claude_session_stats.py`
- [x] T004 [P] Implement `_usage_fp(usage)` usage fingerprint function (4-tuple of token fields) in `tools/claude_session_stats.py`
- [x] T005 [P] Implement `_is_tool_result(content)` transparent connector detection in `tools/claude_session_stats.py`
- [x] T006 Implement `_parse_turns(entries)` — main grouping loop that skips isMeta/isSidechain entries, treats tool-result user entries as transparent, and groups consecutive assistant entries by fingerprint into Steps in `tools/claude_session_stats.py`

**Checkpoint**: Parsing infrastructure complete — all three user stories can now be built on top of this foundation.

---

## Phase 3: User Story 1 — View Session Token Report After Agentic Run (Priority: P1) 🎯 MVP

**Goal**: Automatically generate a Markdown report with session totals and per-turn sections at the end of every agentic session.

**Independent Test**: After any Claude Code session ends, `generated/debug/claude_session_<id>.md` appears automatically; the file contains a Session Totals table and one `### Turn N` section per user prompt (quickstart.md Scenario 1 + Scenario 3).

### Implementation for User Story 1

- [x] T007 [US1] Implement `_prompt_excerpt(content, max_len=70)` helper in `tools/claude_session_stats.py`
- [x] T008 [US1] Implement `_turn_totals(turn)` and session-level aggregation in `tools/claude_session_stats.py`
- [x] T009 [US1] Implement `_fmt(n)` and `_render_markdown()` header block (session ID, project, branch, date, duration, model) in `tools/claude_session_stats.py`
- [x] T010 [US1] Add `## Session Totals` table to `_render_markdown()` in `tools/claude_session_stats.py`
- [x] T011 [US1] Add per-turn `### Turn N` sections with subtotal lines to `_render_markdown()` in `tools/claude_session_stats.py`
- [x] T012 [US1] Implement `main()` with argparse (positional `transcript` + `--output-dir`), output file writing, and stderr logging in `tools/claude_session_stats.py`
- [x] T013 [US1] Update `.claude/hooks/post_stop_notify.sh` to capture stdin and pipe to the Python script, with stderr suppressed

**Checkpoint**: User Story 1 is fully functional — report auto-generates after each session with session totals and turn breakdown.

---

## Phase 4: User Story 2 — Identify Expensive Steps Within a Turn (Priority: P2)

**Goal**: Each turn section shows a per-step table with one row per API call, including an operation label, timestamp, and per-category token counts.

**Independent Test**: A session report for a multi-step turn lists each step as a table row; delegated agent steps show subagent type; pure-response steps show `_(response)_` (quickstart.md Scenario 2 + Scenario 3).

### Implementation for User Story 2

- [x] T014 [US2] Implement `_op_label(tool, inp)` for all tool types: `Agent`, `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `TaskCreate`, `TaskUpdate`, `TaskGet`/`TaskList`, and fallback in `tools/claude_session_stats.py`
- [x] T015 [US2] Implement `_step_op_summary(step)` to join operation labels for a step (returns `_(response)_` for empty ops list) in `tools/claude_session_stats.py`
- [x] T016 [US2] Add per-step table (`| # | Time (UTC) | Operation | In | Cache-W | Cache-R | Out |`) to each turn section in `_render_markdown()` in `tools/claude_session_stats.py`

**Checkpoint**: User Stories 1 + 2 both work independently — step-level tables appear in each turn section with human-readable operation labels.

---

## Phase 5: User Story 3 — Find Optimization Targets via Hotspots (Priority: P3)

**Goal**: A Hotspots section at the end of the report lists the top 5 steps by cache-write volume, each cross-referenced to its turn and step.

**Independent Test**: A session with varied context-loading steps produces a `## Hotspots — Top Cache-Write Steps` section with ≤5 rows ranked by Cache-W descending; sessions with no cache writes produce no Hotspots section (quickstart.md Scenario 4).

### Implementation for User Story 3

- [x] T017 [US3] Implement Hotspots collection: gather all `(turn_num, step_num, step)` tuples across turns, sort by `cache_creation_input_tokens` descending, take top 5 in `tools/claude_session_stats.py`
- [x] T018 [US3] Add conditional `## Hotspots — Top Cache-Write Steps` section to `_render_markdown()` — omit entirely when top entry has `cache_creation_input_tokens == 0` in `tools/claude_session_stats.py`

**Checkpoint**: All three user stories are complete and independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge-case handling, manual invocation path, and end-to-end validation.

- [x] T019 Add graceful exit for empty transcript (no turns found): print diagnostic to stderr, exit code 0, no file written — in `main()` in `tools/claude_session_stats.py`
- [x] T020 [P] Add graceful exit for missing/unreadable transcript: print error to stderr, exit code 1, no file written — in `main()` in `tools/claude_session_stats.py`
- [x] T021 [P] Validate `--output-dir` flag writes report to the specified directory per quickstart.md Scenario 5
- [x] T022 Run quickstart.md Scenario 6 (empty session) and Scenario 7 (missing transcript) to confirm graceful exits
- [x] T023 Run full quickstart.md validation (Scenarios 1–7) to confirm all acceptance criteria are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — verify immediately
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS all user stories**
- **User Story Phases (3–5)**: All depend on Foundational (Phase 2) completion
  - US1 (Phase 3): No dependency on US2/US3
  - US2 (Phase 4): Depends on US1 rendering infrastructure (turn sections must exist)
  - US3 (Phase 5): Depends on US1 rendering infrastructure; independent of US2
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Independent — can start after Phase 2
- **US2 (P2)**: Depends on US1 turn sections existing (T011) before T016 can extend them
- **US3 (P3)**: Depends on US1 report structure (T009/T010) before Hotspots section can be appended; independent of US2

### Within Each Phase

- Foundation: T003 first; T004 and T005 in parallel; T006 last (depends on T004, T005)
- US1: T007 and T008 in parallel; T009–T012 sequentially; T013 after T012
- US2: T014 first; T015 depends on T014; T016 depends on T015
- US3: T017 first; T018 depends on T017

### Parallel Opportunities

- T004 and T005 can run in parallel (independent functions, same file — coordinate to avoid edit conflicts)
- T007 and T008 can run in parallel
- T019 and T020 can run in parallel
- T021 and T022 can run in parallel

---

## Parallel Example: Foundational Phase

```
# Run in parallel (different functions, same file — stagger edits):
Task T004: "Implement _usage_fp() fingerprint function in tools/claude_session_stats.py"
Task T005: "Implement _is_tool_result() connector detection in tools/claude_session_stats.py"
```

## Parallel Example: Polish Phase

```
Task T019: "Add graceful empty-transcript exit in tools/claude_session_stats.py"
Task T020: "Add graceful missing-transcript exit in tools/claude_session_stats.py"
Task T021: "Validate --output-dir flag per quickstart.md Scenario 5"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup verification
2. Complete Phase 2: Foundational parsing (T003–T006)
3. Complete Phase 3: US1 auto-report (T007–T013)
4. **STOP and VALIDATE**: Run quickstart.md Scenario 1 — confirm report appears after session end
5. Report is useful standalone at this point (session totals + turn breakdown)

### Incremental Delivery

1. Phase 1 + 2 → Parsing works
2. Phase 3 → Reports generate automatically (MVP)
3. Phase 4 → Step tables show operation labels (actionable detail)
4. Phase 5 → Hotspots section enables targeted optimization
5. Phase 6 → Edge cases handled; all scenarios validated

---

## Notes

- All tasks operate on `tools/claude_session_stats.py` and `.claude/hooks/post_stop_notify.sh` only — no `app/` changes needed
- `[P]` tasks in the same file require coordinated edits to avoid conflicts; prefer sequential execution unless pair-programming
- This feature has zero new external dependencies — stdlib only
- Commit after each phase checkpoint for clean git history
- Run quickstart.md Scenario 1 after T013 to confirm the happy path before proceeding to US2/US3
