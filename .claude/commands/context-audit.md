# /context-audit

Audit the Claude Code customization environment for context cost, inefficient loading patterns, and missing lightweight alternatives. Reports findings — does not auto-fix.

## Usage

```bash
/context-audit                     # full audit: agents, commands, hooks, settings
/context-audit agents              # audit agent context loading patterns only
/context-audit commands            # audit slash command context efficiency only
/context-audit --fix               # audit and propose concrete edits (requires approval)
```

---

## Why Context Cost Matters

Every file loaded in a turn counts against the context window and increases latency and cost. The goal is the smallest context that can solve the task:

```
Summary doc  →  Targeted source read  →  Full reference doc  →  Explore subagent
   (cheap)           (medium)                  (expensive)          (isolated)
```

Skipping levels (e.g., loading full architecture.md when a module map summary would answer the question) is a context waste. Accumulating reads inline instead of delegating to a subagent is a context leak.

---

## Audit Procedure

### Pass 1 — Inventory (1 read)

1. `Glob .claude/**/*.md` to list all agent definitions and commands.
2. Do NOT read each file yet — record paths only.
3. Count: how many agents, how many commands, how many hooks?

### Pass 2 — Agent context patterns (read agents only)

For each agent in `.claude/agents/`:

| Check | Good | Problem |
|-------|------|---------|
| Has a `## Canonical Sources` section with priority order | yes | absent |
| Loading order goes cheapest first (summary → targeted → full doc) | yes | starts with full doc or broad glob |
| Has explicit "stop when you have what you need" instruction | yes | absent |
| Delegates broad exploration to `Agent` subagent | yes | accumulates inline reads beyond 5 files |
| Does not front-load files unrelated to the current task | yes | always loads a fixed set of 5+ files |

Flag each problem with: agent name, the instruction/step that causes it, and a suggested rewrite.

### Pass 3 — Command context patterns (read commands only)

For each command in `.claude/commands/`:

| Check | Good | Problem |
|-------|------|---------|
| References only the files needed for its specific task | yes | loads CLAUDE.md + AGENTS.md + architecture.md as boilerplate |
| Instructs to stop reading once anchor found | yes | absent |
| Uses "read in order, stop when sufficient" pattern | yes | reads all layer files upfront |
| Links to existing summary docs when available | yes | re-reads full source instead |

Cross-reference against `.github/summaries/` — if a summary exists that covers what a command loads wholesale, flag as a **context optimization opportunity**.

### Pass 4 — Missing summary docs

The Copilot side maintains `.github/summaries/` as low-token context anchors. Assess whether the Claude side needs equivalent `.claude/summaries/` files:

| Topic | Copilot summary exists? | Claude equivalent? | Gap? |
|-------|------------------------|-------------------|------|
| Claude environment governance | `.github/summaries/copilot-governance.md` | none | ⚠ |
| Hook registry | none | none | — |
| Command index | none | none | — |
| Agent index | none | none | — |

For each gap: estimate the token savings a summary would provide (number of full docs it could replace × average doc size). Only recommend creating a summary if savings > 500 tokens per typical use.

### Pass 5 — Subagent delegation opportunities

Identify patterns where inline context accumulation could be replaced with an isolated subagent:

- Any workflow step that reads >3 files to answer a single sub-question
- Any audit or survey task that touches the full repo rather than a specific slice
- Any exploratory step that runs before the actual task is scoped

For each: name the command/agent/step, estimate tokens saved, and suggest the subagent type (`Explore` for surveys, `Plan` for design, general-purpose for targeted research).

---

## Report Format

```
CONTEXT AUDIT REPORT
====================
Scope: <agents | commands | full>
Date: <today>

PASS 2 — Agent patterns
  claude-architect.md    ✓/⚠/✗  <finding>

PASS 3 — Command patterns
  sync.md                ✓/⚠/✗  <finding>
  implement.md           ✓/⚠/✗  <finding>
  ...

PASS 4 — Missing summaries
  ⚠ Gap: <topic> — estimated savings: ~<N> tokens/use
  — No gap: <topic>

PASS 5 — Subagent opportunities
  ⚠ <command>:<step> — reads <N> files inline; delegate to Explore subagent

TOTAL CONTEXT WASTE RISK: <Low | Medium | High>
TOP 3 RECOMMENDATIONS (by token savings):
  1. <specific change>  (~<N> tokens saved per invocation)
  2. <specific change>
  3. <specific change>
```

---

## After Audit

- Present the report; do not apply fixes unless `--fix` was passed.
- For `--fix`: propose the highest-savings fix first; wait for approval before each edit.
- Creating a summary doc is itself a context-cost investment — only do it when break-even is <10 invocations.
