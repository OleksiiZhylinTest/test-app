# DevOps Conventions

Source of truth: `docs/development/pipeline.md` and `AGENTS.md`

## Generated Artifacts Policy

- All runtime artifacts (reports, logs, screenshots, debug output, temp files) must go to `generated/` — never in the source tree.
- Subdirectory convention:
  - `generated/tmp/` — scratch files
  - `generated/debug/` — diagnostic output
  - `generated/reports/` — report artifacts
  - `generated/tmp/screenshots/` — UI screenshots
- `generated/` is gitignored; never commit generated artifacts.

## CI/CD Rules

- Never bypass CI hooks: `--no-verify` is forbidden without explicit user instruction.
- Never force-push to `main` or `master`.
- Never amend published commits — create a new commit instead.

## Escalate to Full Pipeline Doc When

- Adding or removing a CI stage (lint / unit / component / integration / e2e / security).
- Changing `smoke-tests` or `sanity-tests` job configuration.
- Modifying secret, environment variable, or caching strategy in any workflow file.
- Any change that affects the job dependency graph in `.github/workflows/`.
