# Parallel orchestrator sessions

Several orchestrator sessions may work on one repository at once, each in its own **lane** (a
module or area of the code). This file applies only when `docs/project_profile.md` declares lanes
(`[lanes.<name>]` tables); a repository without them has a single orchestrator and ignores it.
The other workflow files (`delegation.md`, `change_safety.md`, `session_lifecycle.md`) assume one
orchestrator; where they disagree with this file, this file wins.

Nothing here depends on a particular client or orchestration tool. Sessions coordinate through
files and git alone: lane ownership in the profile, claims and notices kept by `tools/claim`, and
`tools/land`.

## Lanes

Declare each lane in the profile's TOML block:

```toml
[lanes.search]
writes = ["search/", "data/search/", "tests/search/"]   # directories (trailing /), files or globs
prefix = "S"                                            # question ID prefix (optional)
```

- A lane writes only its `writes` paths and its own task files: `tasks/questions/<lane>.md`,
  `tasks/kickoff/<lane>.md`, specs named `tasks/specs/<lane>-<task>.md`, and history files in
  `tasks/kickoff_history/` with the lane in the name. Name any other new file after the lane where a
  name is needed.
- Everything else is **shared**: common code, `tools/`, `AGENTS.md`, `CLAUDE.md`, `docs/` (the
  profile and decisions included), dependency manifests, `tasks/todo.md`, `tasks/lessons.md` and
  `tasks/next_session_kickoff.md`.
- `tools/claim lanes` lists the lanes; `tools/claim owner <path>` says who owns a path.
- Starting a session: name the lane (`/kickoff <lane>`), read the notice board
  (`tools/claim board`) and the current claims (`tools/claim list`).

## Shared files: claim first

- **Claim before editing:** `tools/claim take <lane> <path>... -m "<why>"`. It refuses (exit 75)
  when another lane owns the path or has claimed an overlapping one; then post a note asking that
  session, and wait or work elsewhere. `tools/claim release <lane>` when the change is committed.
- **Shared code changes are small and additive:** new functions, new fields with defaults, never a
  changed meaning. Commit each on its own and post its commit id with `tools/claim note`.
- **Records** (`docs/decisions.md`, `tasks/lessons.md`, `tasks/todo.md`): no claim needed for an
  appended entry or your own lane's section. Append, then commit that file at once, by explicit
  path. Never commit another session's uncommitted edit.
- A dependency install goes through `tools/agent-lock dependencies` and is announced with a note.

## The notice board

`tools/claim note <lane> "<text>"` posts to a board every session sees; `tools/claim board` reads
it. Claims and releases post themselves. Read the board when a session starts, before claiming,
before landing and before a heavy run; post after landing, after a shared-code commit, before a
heavy run, and when you hit a shared limit. If your client can also message the other sessions
directly, you may do that as well, but the board stays the record.

Claims and notices live in the git directory, shared by the main checkout and every worktree, and
are never committed.

## Commits in the shared main checkout

All orchestrator sessions run in the main checkout on `main`. Therefore:

- Stage explicit paths only: never `git add -A`, `git add .` or `git commit -a`.
- Commit your own record and doc edits as soon as they are final.
- Before committing, check `git status` for files that are not yours, and leave them alone.

## Delegation and landing

- Implementers never work in the main checkout. Each gets its own worktree and branch, named after
  the lane: `<lane>-<task>`. A spec's write scope lies inside its lane's paths, plus shared paths
  the lane has claimed for the task; `speccheck` rejects anything outside it.
- Each lane has its own integration branch `integration-<lane>`, in its own worktree
  `.worktrees/integration-<lane>` (never checked out in the main checkout). Delegated work merges
  there, as in `delegation.md`.
- **Landing on `main`:** run `tools/land <lane>`. Under the `resource-heavy` lock it merges the
  current `main` into `integration-<lane>`, checks that every changed file is the lane's or claimed
  by it (`tools/claim check`), then runs `tools/test-project full` and `git diff --check`. Then, in
  the main checkout: `git merge --ff-only integration-<lane>`. If another session landed in
  between, the fast-forward refuses: rerun `tools/land`.
- Inline work that needs no integration branch is committed directly to `main` by explicit path.
- After landing, post the new `main` commit and any shared file it touched.

## Shared limits

Sessions share the machine and often one usage limit or quota.

- Announce a heavy run (a long job, a batch, a wave of implementers) on the board before starting
  it, and run it detached with a log.
- Run the full test profile only through `tools/land` or `tools/agent-lock resource-heavy`.
- A session that hits a usage or rate limit posts it, so the others know.

## Handoffs

`docs/workflows/session_lifecycle.md` applies per lane:

- Each session writes its continuation to `tasks/kickoff/<lane>.md` (with the fenced `## PROMPT`)
  and its history file to `tasks/kickoff_history/<date_time>-<lane>.md`. It never replaces another
  lane's kickoff.
- `tasks/next_session_kickoff.md` is an index: one line per lane pointing to its kickoff file, plus
  anything that spans lanes. A session updates only its own line.
- Kickoff (`/kickoff <lane>`) reads the index, then that lane's file. Without a lane name, list the
  lanes from the index and ask which one.

## Questions for the user

Each lane keeps its open questions in `tasks/questions/<lane>.md`, with IDs using the lane's
`prefix`; see the `questions` skill.
