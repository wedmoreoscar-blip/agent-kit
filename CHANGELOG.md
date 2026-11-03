# Changelog

## 2026-11-03 — questions, parallel sessions, dismissals

Generalised from job-automation (which keeps its own versions):

- Core skill `questions`: one answerable questions file per topic or lane, with an optional review
  copy in whatever surface the client offers; `scripts/questions.py` (`status`, `pull`, `push
  --meta`).
- Core workflow `docs/workflows/parallel_sessions.md` and tools `tools/claim` (lane ownership,
  claims, notice board, scope check) and `tools/land` (per-lane integration branch), driven by
  `[lanes.<name>]` tables in the profile. `agent_profile.py` validates them. `session_lifecycle.md`
  points to the per-lane kickoff layout; the core AGENTS block names both.
- `kit dismiss` / `kit undismiss`: stop reporting and syncing chosen kit files in one repository.

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
