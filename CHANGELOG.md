# Changelog

## 2026-10-03 — first version

Extracted from DrinkSmart's agent setup (as of `22faad3`) and made project- and harness-neutral:

- Core: 12 skills from DrinkSmart plus `find-skills` (from vercel-labs/skills, changed to install into
  the project only); workflows `agent_selection`, `benchmarking`, `change_safety`, `context_audit`,
  `delegation`, `session_lifecycle`, `skill_authoring`, `verification`, `visual_check`;
  `ORCHESTRATION.md`; setup docs; tools `agent-lock`, `check-agent-setup`, `prepare-worktree` (new),
  `spec-block` (new), `spend-guard`, `test-project` (now reads the profile), `writespec-guard` (now
  also governs Claude Code subagents launched into a worktree).
- Project commands moved into `docs/project_profile.md`; `writespec`'s baseline block is rendered
  from it.
- Traycer content moved into the `traycer` pack; the Codex TUI relay into the `relay` pack.
- Packs `mcp-playwright` and `mcp-context7`.
