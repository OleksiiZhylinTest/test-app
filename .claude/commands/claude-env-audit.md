# /claude-env-audit

Audit the full Claude Code customization environment for drift, security issues, missing assets, and governance compliance. Reports findings — does not auto-fix.

## Usage

```bash
/claude-env-audit                  # full audit across all 5 layers
/claude-env-audit hooks            # hooks layer only
/claude-env-audit agents           # agents layer only
/claude-env-audit security         # security posture only
/claude-env-audit governance       # namespace compliance only
```

---

## Audit Layers

### Layer 1 — Hook Registry

**Goal:** Verify every hook script is wired, functional, and necessary.

1. `Glob .claude/hooks/*.sh` — list all hook scripts.
2. Read `.claude/settings.json` — extract all registered hooks.
3. For each script found:
   - Is it registered in `settings.json`? If not → **DORMANT** gap
   - Is the `matcher` correct for its purpose? (PreToolUse vs PostToolUse vs Stop)
   - Does the `timeout` reflect the script's worst-case runtime?
   - Does the script exit non-zero on blocked input? (spot-check the guard condition)
4. For each registered hook:
   - Does the referenced script exist? If not → **BROKEN** gap
5. Report: dormant scripts, broken references, misconfigured matchers.

### Layer 2 — Agents

**Goal:** Verify agent definitions are complete, role-scoped, and non-overlapping.

Delegate to an Explore subagent — do not read all 14 agent files inline:

```
Explore .claude/agents/ — agent completeness audit:
For each .md file in .claude/agents/:
1. Read frontmatter: is name, description, and tools present?
2. Check body for these top-level sections (## headings):
   Role/Ownership, Responsibilities or Core Responsibilities, Workflow, Constraints, Output Expectations.
3. Check tools list: for each tool, does a workflow step invoke it?
Return a table: agent | D1 frontmatter ✓/⚠/✗ | D3 sections present | D2 tool gaps | finding.
```

Wait for result. For agents flagged with ⚠ or ✗ findings, invoke `/agent-eval <agent-name>` individually for a full D1-D6 rubric score. Include all findings in the Layer 2 section of the report.

### Layer 3 — Slash Commands

**Goal:** Verify commands are current, non-redundant, and referenced in workflow docs.

1. `Glob .claude/commands/*.md` — list all commands.
2. Cross-reference against `docs/development/localAgenticDevelopmentWorkflow.md` — is every command in the workflow doc present as a file?
3. For each command file:
   - Is there a corresponding entry in `CLAUDE.md` commands section?
   - Does the command body match what `CLAUDE.md` or the workflow doc describes?
   - Any commands defined in docs but missing as files? → **MISSING** gap
   - Any command files with no doc reference? → **UNDOCUMENTED** gap
4. Check for commands that duplicate each other's scope.

### Layer 4 — Settings and MCP

**Goal:** Verify `settings.json` is minimal and `settings.local.json` is correctly structured.

1. Read `.claude/settings.json`:
   - All hooks registered? (cross-reference Layer 1)
   - No committed secrets or local-only values?
2. Read `.claude/settings.local.json` (if exists — local only, not committed):
   - `permissions.allow` list: any overly broad patterns (e.g., `*`, `Bash(*)`)?
   - MCP server entries: do referenced scripts exist? Are credentials env-injected (not hardcoded)?
3. Read `.claude/mcp-jira-wrapper.sh` if present — confirm env-var injection pattern is followed.
4. Read `.claude/mcp-servers-template.json` — does it stay in sync with what `settings.local.json` registers?

### Layer 5 — Governance Compliance

**Goal:** Verify Claude namespace stays within its ownership boundary and shared docs are current.

1. Read `.claude/summaries/claude-governance.md` — Claude namespace ownership rules (cheap anchor); only load `docs/development/ai/assistant_customization_governance.md` if the summary flags a gap that requires the authoritative full doc.
2. Check `CLAUDE.md`:
   - Does it reference `AGENTS.md` as the shared contract?
   - Does the Customization Ownership section match the governance doc?
   - Are the cross-tool exception conditions current?
3. Check `AGENTS.md`:
   - Does the Assistant Ownership Model table reflect the current namespace split?
   - Any Claude-specific guidance that leaked into the shared layer?
4. Check `.github/**` customization files only if governance explicitly needs it — use `ALLOW_CROSS_ASSISTANT_CUSTOMIZATION_EDIT=1` and document reason.
5. Flag any drift between `CLAUDE.md`, `AGENTS.md`, and the governance doc.

---

## Report Format

```
CLAUDE ENVIRONMENT AUDIT REPORT
================================
Date: <today>

Layer 1 — Hooks
  ✓ pre_edit_customization_boundary.sh  registered, matcher correct
  ✗ DORMANT: pre_bash_safety.sh         exists but not in settings.json
  ✗ DORMANT: post_edit_lint.sh          exists but not in settings.json
  ✗ DORMANT: post_stop_notify.sh        exists but not in settings.json

Layer 2 — Agents
  ✓ claude-architect.md  all sections present, tools justified

Layer 3 — Commands
  ✓ commit.md   referenced in localAgenticDevelopmentWorkflow.md
  ⚠ UNDOCUMENTED: claude-env-audit.md  not yet in CLAUDE.md commands section

Layer 4 — Settings and MCP
  ✓ settings.json  valid JSON, no secrets
  ⚠ settings.local.json  mcp-wrapper.sh path: confirm script exists

Layer 5 — Governance
  ✓ CLAUDE.md ownership section matches governance doc
  ⚠ AGENTS.md ownership table: may need refresh after agent additions

TOTAL GAPS: <N>  (✗ Fail: <n>  ⚠ Warn: <n>)
PRIORITY ACTIONS:
  1. [✗] Activate dormant hooks in settings.json
  2. [⚠] Add claude-env-audit.md to CLAUDE.md commands section
```

---

## After Audit

- Present the report; do not auto-fix.
- For approved fixes: hook activation → use `/agent-eval --fix` → update docs in that order.
- If cross-tool governance drift is found, escalate: prefer the owning assistant to author changes in its namespace.
