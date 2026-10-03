## Traycer

This section is managed by the agent kit's `traycer` pack. **It applies only when Traycer is
present** (the `traycer` CLI is on `PATH`, or Traycer launched this agent). Otherwise ignore it.

- Delegate through Traycer agents and worktrees as `docs/workflows/delegation_traycer.md` describes;
  it replaces the native-subagent steps of `docs/workflows/delegation.md`.
- The orchestrator always writes to the main checkout on `main`, even when Traycer launched it in a
  worktree.
- Traycer artifacts are a review surface, not storage. Specs live in `tasks/specs/`.
