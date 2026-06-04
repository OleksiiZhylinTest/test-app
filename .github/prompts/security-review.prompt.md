---
name: security-review
description: 'OWASP Top 10 structured security review for GH Security QA. Run before any auth-adjacent, credential-adjacent, or network-adjacent change merges.'
model: 'Claude Sonnet 4.5 (copilot)'
---

# Security Review

## Purpose
Apply OWASP Top 10 checks to changed code before merge.

## Steps

1. Read `.github/summaries/dev-conventions.md` — load credential and logging rules.
2. Identify the changed files from the task context.
3. Apply the review checklist:
   - [ ] No hardcoded credentials, tokens, or API keys
   - [ ] No credential values logged at any log level
   - [ ] HTTP inputs validated at system boundary before use
   - [ ] No path traversal risk in file operations
   - [ ] No command injection via subprocess or shell calls
   - [ ] TLS certificate validation not bypassed (`verify=True`)
   - [ ] No sensitive data in error messages returned to clients
   - [ ] New dependencies reviewed for CVEs (run `python tests/runners/run_security_checks.py`)
4. For each FAIL item: document affected file, line range, severity (CRITICAL/HIGH/MEDIUM/LOW), and recommended fix.
5. Write the full findings report to `generated/tmp/security-findings-<YYYY-MM-DD>.md`.
6. Present findings to the user and wait for human decision before any remediation begins.

## Output
A findings report at `generated/tmp/security-findings-<YYYY-MM-DD>.md` plus a one-line summary to the user.
