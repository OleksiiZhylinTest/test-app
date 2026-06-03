---
name: Secure MCP Review
description: 'Review MCP usage and external-system access for security, least privilege, and assistant-boundary compliance.'
agent: GH Copilot Architect
argument-hint: 'Describe the MCP server, external system, or access pattern to review'
tools: [read, search]
---

Review the requested MCP or external-system design from a security and governance perspective.

Requirements:
- Focus on assistant ownership boundaries, secret handling, least privilege, and prompt-injection risk.
- Do not suggest embedding credentials into repo-shared files.
- Prefer assistant-scoped configuration and sanitized examples.
- Return: risks, required controls, and a safer alternative when one exists.