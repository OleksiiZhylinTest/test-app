# Quickstart & Validation Guide: Agentic SDLC Token Consumption Telemetry

**Branch**: `001-session-token-telemetry` | **Date**: 2026-06-05

## Prerequisites

- Claude Code CLI installed and configured for this project
- `.claude/hooks/post_stop_notify.sh` wired in `.claude/settings.local.json` as a Stop hook (already configured)
- Python 3.x available on `PATH`
- `generated/debug/` directory writeable (created automatically if absent)

## Scenario 1 — Automatic Report Generation (Happy Path)

**Goal**: Verify a report is generated after a normal agentic session.

1. Start a Claude Code session in this project.
2. Send at least two user messages; perform at least one tool call (e.g., ask Claude to read a file).
3. End the session normally (close the session or use `/exit`).
4. Check the output directory:
   ```bash
   ls generated/debug/claude_session_*.md
   ```
5. Open the report and verify:
   - Header shows the correct session ID, project name, and date.
   - `## Session Totals` table has non-zero values in at least one category.
   - `## Turn Details` contains one `### Turn N` section per user message sent.
   - Each turn section contains a per-step table with at least one row.

**Expected outcome**: Report file present and readable within 5 seconds of session end.

---

## Scenario 2 — Per-Step Operation Labels

**Goal**: Verify that tool calls appear as labelled rows, not raw JSON.

1. In a session, ask Claude to read a file AND run a bash command.
2. End the session.
3. Open the report and locate the turn that triggered those tool calls.
4. Verify the step table contains rows with human-readable labels such as:
   - `Read(filename.ext)` for a file read
   - `Bash: "description of command"` for a shell command
5. Verify a pure assistant response step (no tool calls) is labelled `_(response)_`.

**Expected outcome**: Operation column is always a readable string, never raw JSON or a tool name alone.

---

## Scenario 3 — Agent Delegation Labels

**Goal**: Verify that subagent delegations are identifiable in the report.

1. In a session, trigger a task that causes Claude to spawn a subagent (e.g., use a skill that delegates to an Explore subagent).
2. End the session.
3. Open the report and find the delegation step.
4. Verify the operation label reads: `**→ SubagentType**: description...`

**Expected outcome**: Delegation steps are visually distinct and identify the subagent type.

---

## Scenario 4 — Hotspots Section

**Goal**: Verify the Hotspots section appears and ranks steps correctly.

1. Run a session with several turns where Claude reads large files or processes long prompts.
2. Open the report and scroll to the bottom.
3. Verify `## Hotspots — Top Cache-Write Steps` is present.
4. Verify the table has at most 5 rows, sorted by Cache-W descending.
5. Verify each row shows Turn number, Step number, Cache-W value, and operation label.

**Expected outcome**: Top 5 most context-loading steps are listed in the Hotspots section.

---

## Scenario 5 — Manual Invocation

**Goal**: Verify reports can be regenerated from an existing transcript.

1. Locate a session transcript:
   ```bash
   ls ~/.claude/projects/*/  # find a .jsonl file
   ```
2. Run the script manually:
   ```bash
   python tools/claude_session_stats.py <path-to-transcript.jsonl>
   ```
3. Verify `generated/debug/claude_session_<id>.md` is created (or overwritten).
4. Optionally write to a custom directory:
   ```bash
   python tools/claude_session_stats.py <transcript> --output-dir /tmp/reports
   ```

**Expected outcome**: Report generated successfully; exit code 0; report path printed to stderr.

---

## Scenario 6 — Empty Session Graceful Exit

**Goal**: Verify graceful handling when the session has no user turns.

1. Locate (or create) a minimal transcript with no `user` entries of type non-tool-result.
2. Run manually:
   ```bash
   python tools/claude_session_stats.py <transcript>
   ```
3. Verify: no report file is written; a message is printed to stderr; exit code is 0.

**Expected outcome**: Script exits cleanly without writing a partial file.

---

## Scenario 7 — Missing Transcript Graceful Exit

**Goal**: Verify graceful handling when the transcript file does not exist.

```bash
python tools/claude_session_stats.py /tmp/nonexistent.jsonl
```

**Expected outcome**: Error message on stderr: `Transcript not found: ...`; exit code 1; no report file written.

---

## Reference

- CLI contract: [`contracts/cli-contract.md`](contracts/cli-contract.md)
- Data model: [`data-model.md`](data-model.md)
- Implementation: `tools/claude_session_stats.py`
- Hook: `.claude/hooks/post_stop_notify.sh`
- Hook wiring: `.claude/settings.local.json` (Stop event)
