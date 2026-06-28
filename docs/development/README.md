# Development Documentation

Technical reference and guides for contributors and AI agents working on this codebase.

## Core Docs

| Document | What it covers |
|----------|----------------|
| [Architecture](architecture.md) | Module map, data flow, technology stack, extension patterns, setup guide |
| [CI Pipeline](pipeline.md) | GitHub Actions pipeline, stage configuration, troubleshooting, dependabot |

## Subdirectories

| Directory | What it covers |
|-----------|----------------|
| [adr/](adr/README.md) | Architecture Decision Records |
| [confluence/](confluence/README.md) | Confluence REST API reference, CRUD operations, extension guide |
| [jira/](jira/README.md) | Jira REST API reference, agile API, extension guide |
| [quality/](quality/README.md) | Test strategy, coverage gates, performance baselines |

## Templates

- [ADR template](adr/adr-template.md) — use when creating a new Architecture Decision Record

Copy the template to `adr/NNNN-short-title.md`, fill in the context, decision, and consequences sections, then link the new file from `adr/README.md`.
