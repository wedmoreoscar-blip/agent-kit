## Shared agent rules

This section is managed by the agent kit (`kit sync`). Change it in a kit repository with
`kit push AGENTS.md`, not by hand-editing only here, or the next sync will report a local edit.

### Authority

The project sections of this file come first, then `LOCKED` entries in `docs/decisions.md`, then the
current continuation in `tasks/next_session_kickoff.md`. Project facts (commands, known failures,
quirks, high-risk areas) live in `docs/project_profile.md`. `CLAUDE.md` imports this file.

### Working rules

- Preserve unrelated changes in a dirty worktree. Never stage, revert, or delete work you did not
  create.
- Plan non-trivial work with acceptance criteria. Record multi-session or multi-agent plans in
  `tasks/todo.md` and check in before broad rewrites or changes spanning roughly 50 lines or several
  files.
- Make the smallest correct change. Reuse existing helpers, state patterns, and components before
  creating another abstraction.
- Verify the changed behavior and inspect the complete diff before reporting completion. Report
  `PASS`, `FAIL`, `SKIP` and `BLOCKED` distinctly (`docs/workflows/verification.md`); run checks with
  `tools/test-project <profile>`.
- Never push, deploy, migrate a remote database, rotate secrets, or publish a release without an
  explicit user request. Never use `git -C <path> push` or any other form of push. Commit locally
  only.
- Never read or print `.env` files or other secrets, and never commit them, generated output, or
  local agent state (`.claude/settings.local.json`, `CLAUDE.local.md`, `.worktrees/`).
- Follow `docs/workflows/change_safety.md` for writes, commits, worktrees, and integration.

### Delegation

- Delegate only when `docs/workflows/delegation.md` ("When to delegate at all") says it is worth it;
  keep small, design-heavy, or dense work inline.
- Every delegation is commissioned by a `writespec` spec and accepted only through `speccheck`. After
  handback the checker owns repairs and fixes almost everything inline; re-contact the implementer
  only under a named `speccheck` exception, and confirm with the user before reusing a warm agent.
- `docs/workflows/agent_selection.md` decides which agent runs which role. The default delegation
  mechanism is the orchestrating client's native subagents, each in its own git worktree. An
  orchestration tool is used only where its pack is installed **and** the tool is present on this
  machine; otherwise ignore its files and use native subagents.
- Each spec states its verification baseline in literal numbers obtained by running the commands.
- The final visual check of a redesign follows `docs/workflows/visual_check.md`, not the delegation
  path. Halt and wait for the user on reaching it.
- Serialize dependency installs, shared dev servers, local service mutations, and costly benchmarks
  with `tools/agent-lock <scope> -- <command>`.

### Skills

Repository skills live in identical copies under `.agents/skills/` (Codex, opencode) and
`.claude/skills/` (Claude Code, opencode). Codex invokes them with `$<skill>`, Claude Code with
`/<skill>`, opencode by name. There are **no personal or global skills**: never write a skill into a
home directory. A skill is either project-only or shared through the agent kit; see
`docs/workflows/skill_authoring.md`. Setup and cloning: `docs/agent_setup/CROSS_MACHINE_SETUP.md`.
Validate with `tools/check-agent-setup`.
