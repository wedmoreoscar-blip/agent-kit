# Changelog

## 2026-11-06 — Guards in Codex and opencode

- Core `hooks.toml`: entries take an optional `codex_matcher`; `kit sync` writes those into a
  generated `.codex/hooks.json` (command finds the root with `git rev-parse --show-toplevel`).
  Codex runs project hooks only after the user trusts them in `/hooks`; `kit doctor` reports it.
- Core file `.opencode/plugins/kit-guards.js`: runs `writespec-guard` (bash, task) and `spend-guard`
  (bash) before opencode's tools and throws on a deny, which blocks the call.
- `writespec-guard`: a Codex `spawn_agent` or opencode `task` whose text names a worktree is a
  commission (neither harness creates worktrees, so delegation.md has the spec name one). Claude
  Code behaviour is unchanged.
- `check-agent-setup`: Codex and opencode regression cases. `tests/` (new): `python3 -m unittest
  discover -s tests`.

## 2026-11-04 — DeepSeek launcher: no auto-mode notice

- `traycer` pack, `home/bin/deepseek`: sets `CLAUDE_CODE_AUTO_MODE_SERVER=0`. Auto mode's
  server-side classifier checks cannot pass through `api.deepseek.com`, so every new DeepSeek
  session stopped at an "isn't eligible" notice until someone pressed Enter, stalling unattended
  agents. Billing is unchanged.

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
