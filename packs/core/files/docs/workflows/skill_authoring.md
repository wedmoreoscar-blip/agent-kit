# Portable Skill Authoring

Create skills against the open Agent Skills structure so the same core package can be used by Codex
and Claude Code (opencode reads both folders).

## Required structure

```text
skill-name/
  SKILL.md
  agents/openai.yaml     # optional Codex/ChatGPT interface metadata
  references/            # optional detailed material
  scripts/               # optional deterministic helpers
  assets/                # optional output resources
```

`SKILL.md` must use lowercase kebab-case for the folder and `name`, and begin with only the portable
required frontmatter unless a client-specific extension is truly needed:

```yaml
---
name: skill-name
description: State what the workflow does and the concrete requests that should trigger it.
---
```

## Process

1. Define two or three realistic trigger requests, expected inputs, output, safety boundary, and
   requests that must not trigger the skill.
2. Keep one recognizable job per skill. Put detailed policy or examples in one-level-deep references.
3. Prefer imperative, concise instructions. Add a script only when deterministic repetition warrants
   it, and execute-test every added script.
4. Write the files by hand, following "Writing rules" below. Add `agents/openai.yaml` with an
   `interface` block (`display_name`, `short_description`, `default_prompt`) in the style of the
   existing skills. Do not use a client's skill-creator scripts: they default to a home directory
   and allow frontmatter keys this repository forbids.
5. Mirror the whole skill folder byte-identically in `.agents/skills/<name>/` and
   `.claude/skills/<name>/`, plus every extra tool target recorded in `.agent-kit.lock`. Do not use
   symlinks because the repository must clone cleanly on Windows.
6. Test obvious triggers, paraphrases, non-triggers, incomplete inputs, and at least one edge case in a
   fresh session. Restart a client only if its live watcher does not discover a newly created folder.
7. Run `tools/check-agent-setup` to validate structure, frontmatter format and cross-client parity.

## Writing rules

Combined from Anthropic's [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
and OpenAI's [Codex skills guide](https://learn.chatgpt.com/docs/build-skills), checked 2026-11-06.
Re-read both before a large rework; they change.

- **Frontmatter:** `name` and `description` only. `name`: lowercase letters, digits and single
  hyphens, at most 64 characters, matching the folder, and never containing `anthropic` or `claude`.
  `description`: at most 1,024 characters, no `<` or `>`. `tools/check-agent-setup` enforces these.
- **Description:** it alone decides whether the skill is picked, from among every installed skill.
  Third person; what the skill does, then when to use it. Put the trigger words first, because hosts
  shorten long descriptions. Add a "not for …" boundary only where a neighbouring request would
  otherwise misfire. Avoid catch-alls ("how do I do X") that match ordinary questions.
- **Body:** assume a capable model; include only what changes its decisions (project paths, rules,
  sequences, traps). Imperative steps with explicit inputs and outputs. Keep it short; 500 lines is a
  hard ceiling, not a target.
- **Strictness follows risk:** exact commands and fixed order only where a mistake is costly or the
  sequence is fragile; elsewhere state the outcome and the criteria.
- **Detail:** move mode-specific material into files linked directly from `SKILL.md` (one level
  deep), each with a line saying when to read it. A skill whose procedure lives in a
  `docs/workflows/` file points there instead, which is the kit's pattern.
- **Scripts:** only for deterministic, repeated work; handle errors in the script, name every
  constant's reason, say whether to run or read it, and run-test it.
- **Commands in the body:** run every command the skill tells an agent to run, on a realistic case
  (not only the easy one), before finishing. An untested command is the commonest break.
- **Content:** one term per concept; forward slashes in paths; no dated statements ("before
  August …"), facts likely to go stale (install counts, prices), README or changelog files.

## Where skills live

There are no personal or global skills. A skill is either **project-only** (it lives in this
repository and nowhere else) or **kit-owned** (its source is the agent kit, and `kit sync` copies it
into each repository). Never write a skill into `~/.agents/skills`, `~/.claude/skills` or any other
home directory: a second copy there drifts, and Claude Code prefers a personal copy over the
project's.

- Improving a kit-owned skill: edit it here, then `kit push <path>` sends it to the kit.
- Promoting a project skill to the kit: `kit push --new .agents/skills/<name> --pack core`.
- A project-only skill must not reuse a kit skill's name.

Only the user runs `kit`. An agent may suggest a push but never performs one unasked.

Keep user installation guidance outside skill folders. Setup procedure belongs in
`docs/agent_setup/`, not in each skill package.
