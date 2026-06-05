# Research: Agentic SDLC Token Consumption Telemetry

**Branch**: `001-session-token-telemetry` | **Date**: 2026-06-05

No NEEDS CLARIFICATION items were outstanding after the clarification phase. This document records the key design decisions made during implementation.

## Decision 1: Data Source — Stop Hook Stdin vs. Polling

**Decision**: Use the Claude Code Stop hook stdin, which provides a JSON payload containing `transcript_path` pointing to the live session JSONL file.

**Rationale**: The Stop hook delivers the transcript path automatically at session end — zero configuration, zero polling, zero external API calls. The JSONL file contains complete per-API-call token usage already attached to each assistant message entry.

**Alternatives considered**:
- Polling the Claude projects directory for new/changed JSONL files: rejected — introduces race conditions and requires file system watching.
- Claude Code Telemetry API (if one existed): not available; Stop hook is the only supported extension point.

---

## Decision 2: API Call Grouping — Usage Fingerprint vs. parentUuid

**Decision**: Group consecutive assistant JSONL entries with identical `(input_tokens, cache_creation_input_tokens, cache_read_input_tokens, output_tokens)` as one API call (one step).

**Rationale**: Claude Code emits one JSONL entry per content block (thinking, text, tool_use) for a single API response, all carrying **identical** usage values. The `parentUuid` field does not reliably link blocks from the same API call — blocks from the same call have distinct UUIDs. The usage fingerprint is the only shared signal. Since `cache_read_input_tokens` grows monotonically across calls, false collisions between distinct API calls are practically impossible.

**Alternatives considered**:
- `parentUuid` grouping: rejected — validated empirically to produce duplicate rows (Turn 2 showed 5 rows instead of 2).
- `requestId` field: not present in observed transcripts.

---

## Decision 3: Hotspots Metric — Cache-Write vs. Total Tokens

**Decision**: Rank Hotspots by `cache_creation_input_tokens` (new context written to cache), not by total tokens.

**Rationale**: Cache-write tokens represent newly-loaded context priced at the full input rate (not the cheaper cache-read rate). They are the primary lever for cost optimization: shortening prompts, reducing file reads, or restructuring system context reduces cache-write volume directly. Total token sorting conflates cheap cache reads with expensive writes and obscures the actionable signal.

**Alternatives considered**:
- Total tokens (sum of all four fields): rejected — dominated by cache-read which is cheap and not actionable.
- Output tokens: rejected — output is driven by assistant response length, not context loading.

---

## Decision 4: Output Format — Markdown File vs. Terminal Output

**Decision**: Write a Markdown file to `generated/debug/claude_session_<session_id[:8]>.md`, overwriting on each run for the same session.

**Rationale**: Markdown is renderable in any editor, git diff-friendly, and persistable for later inspection. Terminal stdout is ephemeral and not useful for sessions that ran while the developer was away. The 8-char session ID prefix is sufficient for uniqueness within a project's debug directory.

**Alternatives considered**:
- JSON output: rejected — not human-readable without tooling.
- CSV: rejected — multi-table structure doesn't map cleanly.
- Appending to a single log file: rejected — creates unbounded growth and makes it hard to isolate a single session.

---

## Decision 5: Tool-Result User Entries — Skip vs. Include as Turn Boundary

**Decision**: User entries whose `message.content` consists entirely of `tool_result` blocks are treated as transparent connectors and skipped — they do not start a new turn.

**Rationale**: Tool results are the mechanism by which Claude Code connects tool call outputs back to the next assistant step. They carry no user-authored content and would produce empty "turns" with misleading attribution if treated as real prompts.

**Alternatives considered**:
- Include as turn boundary: rejected — produces phantom turns with no prompt text and inflates turn count.
