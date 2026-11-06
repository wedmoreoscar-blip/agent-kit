---
name: skill-writing
description: Creates or revises a skill (a SKILL.md package) in this repository's .agents/skills and .claude/skills folders. Use when asked to write, edit, rename, review or promote a skill or slash-command workflow, and before editing any SKILL.md. Not for finding or installing someone else's skill; that is find-skills.
---

Follow `docs/workflows/skill_authoring.md`: its structure, process and "Writing rules" sections. These
steps are the ones not to skip:

1. Decide it should be a skill: a repeated procedure. A one-off belongs in `docs/workflows/`. Check
   `.agent-kit.lock` to see whether the skill is kit-owned; a project-only skill must not reuse a kit
   skill's name.
2. Start from a real task. List two or three requests that should trigger the skill and one or two
   that must not.
3. Write `SKILL.md` and `agents/openai.yaml` by hand, following the writing rules. Never write into a
   home directory and never use a client's skill-creator scripts.
4. Mirror the folder byte-identically into `.agents/skills/<name>/` and `.claude/skills/<name>/`, plus
   any extra target in `.agent-kit.lock`. No symlinks.
5. Run `tools/check-agent-setup` and fix every failure.
6. For a new or substantially changed skill, test it as step 6 of the doc describes.
7. Report what changed. For a kit-owned skill, give the user `kit push <path>` to run; for a project
   skill useful elsewhere, suggest `kit push --new .agents/skills/<name> --pack core`. Never run
   `kit` yourself.
