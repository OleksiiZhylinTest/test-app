# Reporting Back to PM

When a task delegated by PM is complete, return **only** the following to PM:

1. **Status**: `COMPLETE`, `BLOCKED`, or `ESCALATE`
2. **Changes made**: list of files created or modified, each with a one-line description
3. **Open items**: any risks, blockers, or follow-up items requiring PM or human attention

Do **not** return intermediate content, draft specs, sub-agent output, or internal chain details to PM. PM needs the result, not the process.

If the task is `BLOCKED` or requires `ESCALATE`, stop all sub-delegation immediately and report to PM. PM will present to the human and wait for instruction before any further work.
