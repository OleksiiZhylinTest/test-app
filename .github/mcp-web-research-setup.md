# Copilot Web Research MCP Setup

Use this companion guide when enabling external lookup for the `Web Research` Copilot agent.

## Goal

Provide one approved external lookup capability for narrow documentation research without broadening the default Copilot tool surface.

## Local-Only Placement

- Put the MCP server registration in `.vscode/mcp.json`.
- Do not commit `.vscode/mcp.json`.
- Keep secrets out of `.github/**`, `AGENTS.md`, prompts, skills, and agent files.

## Design Requirements

- Scope the server to read-only external lookup whenever possible.
- Prefer official documentation and standards sources.
- Use environment variables or secure secret storage for credentials when the server needs them.
- Expose the capability only where it is needed for external research workflows.
- Review the server with `.github/prompts/secure-mcp-review.prompt.md` before treating it as approved.

## Minimum Local Checklist

1. Choose a server that solves a real external research need and does not duplicate an existing built-in capability.
2. Confirm the server can run without storing secrets in repo files.
3. Confirm the server does not require `.claude/**` wrappers or Claude-owned config.
4. Confirm the blast radius if the server is compromised or misconfigured is acceptably small.
5. Confirm the server's tool names locally before using them in prompts or agent instructions.

## Sanitized `.vscode/mcp.json` Shape

Use this as a shape example only. Replace placeholder names locally after the server is reviewed.

```json
{
  "servers": {
    "web-research": {
      "command": "<local-command-or-launcher>",
      "args": ["<server-arg-1>", "<server-arg-2>"],
      "env": {
        "EXTERNAL_RESEARCH_API_KEY": "${env:EXTERNAL_RESEARCH_API_KEY}"
      }
    }
  }
}
```

## After Local Setup

- Verify the server starts locally.
- Verify the exposed tool names and behavior.
- Keep `Web Research` compact-output constraints in place even after external lookup becomes available.
- If the server exposes more than external lookup, restrict usage procedurally to the smallest safe subset.

## Shared-Layer Impact

- No `AGENTS.md` update is required unless Copilot MCP setup location or ownership rules become shared repo policy.