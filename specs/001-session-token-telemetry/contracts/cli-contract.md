# Contract: claude_session_stats.py CLI Interface

**Branch**: `001-session-token-telemetry` | **Date**: 2026-06-05

## Invocation Modes

### Mode 1 — Stop Hook (automatic)

Triggered by `.claude/hooks/post_stop_notify.sh` at session end.

**Input**: JSON object on stdin

```json
{
  "session_id": "<uuid>",
  "transcript_path": "<absolute path to .jsonl file>",
  "cwd": "<project working directory>",
  "permission_mode": "<string>",
  "hook_event_name": "Stop",
  "stop_hook_active": false,
  "last_assistant_message": "<string>"
}
```

**Required fields**: `transcript_path` (script exits with code 1 if absent or file not found).
**Optional fields**: `session_id` (falls back to transcript filename stem), `cwd` (falls back to `Path.cwd()`).

**Output**: Report written to `{cwd}/generated/debug/claude_session_{session_id[:8]}.md`
**Stdout**: empty (report path written to stderr)
**Exit code**: `0` on success or empty session; `1` on missing transcript

---

### Mode 2 — Manual Invocation

```
python tools/claude_session_stats.py <transcript_path> [--output-dir <dir>]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `transcript_path` | Yes | Absolute or relative path to a session `.jsonl` file |
| `--output-dir` | No | Directory to write the report (default: `./generated/debug/`) |

**Output**: Report written to `{output_dir}/claude_session_{transcript_stem[:8]}.md`
**Exit code**: `0` on success or empty session; `1` on missing/invalid transcript

---

## Output File Contract

| Property | Contract |
|----------|----------|
| File name | `claude_session_{session_id[:8]}.md` |
| Location | `generated/debug/` (hook mode) or `--output-dir` (manual mode) |
| Encoding | UTF-8 |
| Overwrite | Always overwrite; never append |
| Format | GitHub-Flavored Markdown |

### Required Report Sections (in order)

1. `# Claude Session Token Report` — header with session ID, project, branch, date, duration, model
2. `## Session Totals` — 5-row table: Input, Cache read, Cache write, Output, Total effective
3. `## Turn Details` — one `### Turn N` subsection per user prompt turn
4. `## Hotspots — Top Cache-Write Steps` — present only when ≥1 step has `cache_creation_input_tokens > 0`

### Turn Section Format

```markdown
### Turn N · HH:MM:SS UTC
**Prompt:** "..."
**Subtotal:** in=X · cache-r=X · cache-w=X · out=X (N steps)

| # | Time (UTC) | Operation | In | Cache-W | Cache-R | Out |
|---|------------|-----------|---:|--------:|--------:|----:|
| 1 | HH:MM:SS   | ...       | X  | X       | X       | X   |
```

### Hotspots Section Format

```markdown
## Hotspots — Top Cache-Write Steps

| Turn | Step | Cache-W | Operation |
|------|-----:|--------:|-----------|
| T1   | S2   | X       | ...       |
```

Maximum 5 rows. Rows sorted by Cache-W descending. Rows with Cache-W = 0 excluded.

---

## Hook Invocation Contract

**File**: `.claude/hooks/post_stop_notify.sh`

The hook MUST:
- Read stdin to a variable before any other output
- Pipe stdin to the Python script only when non-empty
- Suppress Python script stderr (`2>/dev/null`) to avoid noise in Claude's terminal
- Always print the "Claude finished" banner regardless of script success/failure

The hook MUST NOT:
- Block the session completion by waiting indefinitely
- Fail silently without the banner if the script errors
