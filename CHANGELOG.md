# Changelog

## 2026-11-26 — Whole suite once per wave; tests that last

A 7-leg wave ran the whole test suite about 22 times (once per worktree at provisioning, once or
more per implementer, once per merge, then the final baseline). Now it normally runs once, and
twice only when `main` moved since the last wave.

- `tools/test-project related [--base REF] [-- FILE ...]`: runs `[commands].test_related` on the
  files changed since the merge base with REF (default `main`), including uncommitted and untracked
  ones; `{files}` in the command becomes the paths. Falls back to `[commands].test` with a note.
  The checker uses `--base HEAD^1` after each merge: exactly the leg just merged.
- `tools/test-project full` records its result (commit, each command's exit status and closing
  output) in the shared git directory when the tree is clean; `tools/test-project recorded [--ref
  REF]` prints it while REF is still at that commit, else exits 1. Spec counts come from here.
- `tools/prepare-worktree`: runs `[commands].test_collect` (load every test, run none) instead of the
  whole suite; falls back to `test` with a note.
- `writespec`: counts from `recorded`, one `full` run on `main` per wave when stale. `closing.md`:
  the implementer runs the listed commands, not the whole suite. The baseline block renders
  `test_related` as `tools/test-project related`.
- `speccheck`: step 5 says what tests to write (behaviour, named for what they protect) and makes
  checks that read source as text temporary review evidence, deleted before committing; step 6 runs
  new plus related tests only, matching `delegation.md` step 11 (it used to say the whole suite);
  step 7 commits repairs first so the final run is recorded.
- `verification.md`: the new commands, the blind spots of import-based selection, and "End-to-end
  checks, where applicable" (browser test for a UI, fixture run of the real entry point otherwise).
- Profile template: `test_related`, `test_collect`, `e2e` (commented, with examples), a
  `## Critical flows` section. `agent_profile.py` reserves the profile names `related` and
  `recorded`. `check-agent-setup` prints a NOTE (not a failure) while a profile still runs the
  whole suite routinely.
- `delegation.md`, `change_safety.md`, `parallel_sessions.md`, `ORCHESTRATION.md`, AGENTS block:
  wording to match. New `tests/test_test_project.py`.

**Each project, after `kit sync`:** add `test_related` and `test_collect` to `[commands]` in
`docs/project_profile.md` and put `"test_related"` in `[implementer].run`. Vitest:
`npx vitest related --run --passWithNoTests {files}` and `npx vitest list > /dev/null`. pytest has
no import-based selection built in: `pytest-testmon` (`pytest -q --testmon`) or a project script,
with `pytest -q --collect-only` for the load check. Until then `related` runs the whole suite.

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
