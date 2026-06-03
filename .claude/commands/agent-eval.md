# /agent-eval

Evaluate one or more Claude Code subagent definitions against the quality rubric. Reports gaps and recommendations — does not auto-fix.

## Usage

```bash
/agent-eval                        # evaluate all agents under .claude/agents/
/agent-eval claude-architect       # evaluate a specific agent by name
/agent-eval --fix                  # evaluate and propose concrete edits (requires approval)
```

---

## Evaluation Procedure

### Step 1 — Locate agents

1. `Glob .claude/agents/*.md` to list all agent definitions.
2. If a specific name was given, read only that file; otherwise read all.
3. Do not load other docs until you need them to verify a specific claim.

### Step 2 — Apply the rubric (one agent at a time)

Score each dimension `✓ Pass`, `⚠ Warn`, or `✗ Fail`. A finding at `✗ Fail` must include a concrete fix recommendation.

#### D1 — Frontmatter

| Check | Pass | Warn | Fail |
|-------|------|------|------|
| `name` is a short, specific role title | clear & unique | generic ("Helper") | missing |
| `description` starts with a trigger phrase ("Use when…") | yes | vague benefit claim | missing or >2 sentences |
| `description` names the owned namespace(s) | explicit | implied | absent |
| `tools` list is present | yes | — | missing |

#### D2 — Tool list minimality

For each tool in the `tools` list, verify the agent body contains a use case that requires it:

| Tool | Justified if… |
|------|---------------|
| `Read` | agent reads files |
| `Edit` / `Write` | agent modifies files |
| `Bash` | agent runs shell commands |
| `Glob` / `Grep` | agent searches files |
| `Agent` | agent spawns subagents |
| `WebFetch` / `WebSearch` | agent accesses external URLs |
| MCP tools | agent calls an external system |

Flag any tool that has no corresponding workflow step as `⚠ Warn` (may be latent) or `✗ Fail` (clearly unused and widens attack surface).

#### D3 — System prompt structure

All five sections must be present and non-empty:

| Section | Purpose | Fail condition |
|---------|---------|----------------|
| **Role / Ownership** | Defines what the agent is and what namespace it owns | Missing or too broad ("you help with everything") |
| **Responsibilities** | Numbered list of concrete tasks | Absent or contains product-feature work |
| **Workflow** | Step-by-step procedure with decision points | Absent; or just "do what the user asks" |
| **Constraints** | Explicit "do not" rules | Absent or empty |
| **Output Expectations** | Describes what a good response looks like | Absent |

#### D4 — Namespace compliance

1. Does the agent body name its owned surfaces explicitly?
2. Does it state which surfaces are off-limits without explicit user override?
3. If it references cross-tool access, does it name the bypass mechanism (`ALLOW_CROSS_ASSISTANT_CUSTOMIZATION_EDIT=1`)?
4. Does it reference `docs/development/assistant_customization_governance.md` or `AGENTS.md` as anchors?

#### D5 — Context loading discipline

1. Does the agent define a canonical sources loading order (cheapest first)?
2. Does the workflow load broad docs on first pass, or only when a targeted read is insufficient?
3. Are there instructions to stop loading once the question is answered?
4. Does the agent use subagents or `Agent` for exploration that would otherwise bloat inline context?

#### D6 — Security posture

| Check | Pass | Fail |
|-------|------|------|
| No secrets / credentials in agent body | yes | any hardcoded value |
| Least-privilege: does not claim tools it doesn't use | yes | extra tools present |
| Bypass env var flagged as security-sensitive | flagged | not mentioned |
| No instruction to log/echo sensitive prompt content | yes | present |

---

## Report Format

```
AGENT EVALUATION REPORT
=======================
Agent: <name>  File: <path>

D1 Frontmatter         ✓/⚠/✗  <finding>
D2 Tool minimality     ✓/⚠/✗  <finding>
D3 Prompt structure    ✓/⚠/✗  <finding>
D4 Namespace compliance ✓/⚠/✗ <finding>
D5 Context discipline  ✓/⚠/✗  <finding>
D6 Security posture    ✓/⚠/✗  <finding>

RECOMMENDED ACTIONS (priority order):
  1. [✗ Fail] <dimension>: <specific fix>
  2. [⚠ Warn] <dimension>: <specific improvement>
```

---

## After Evaluation

- Present the report; do not apply fixes unless `--fix` was passed.
- For `--fix`: propose each change as a diff; wait for user approval before editing.
- If the agent being evaluated is `claude-architect.md` itself, note that self-referential evaluation is inherently limited — suggest a peer review pass.
