---
name: Copilot Environment Audit
description: 'Audit the GitHub Copilot customization environment for drift, context cost, security issues, or missing assets.'
agent: GH Copilot Architect
argument-hint: 'Describe the audit scope or leave blank for a general Copilot environment audit'
tools: [read, search, edit]
---

Audit the GitHub Copilot environment in this repository.

Requirements:
- Stay inside `.github/**` plus shared repo guidance unless cross-tool governance is explicitly requested.
- Check for context bloat, duplicated guidance, missing summaries, insecure patterns, and overly broad tool scopes.
- Prefer concise findings with file-level recommendations.
- Return: top issues, priority order, and the smallest safe next steps.