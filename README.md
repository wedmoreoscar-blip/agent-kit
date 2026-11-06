# agent-kit

The single source of truth for the agent workflow layer shared by all my repositories: skills,
workflow docs, tools, guards, permission rules, `AGENTS.md` rules and record templates, for Claude
Code, Codex and opencode alike.

Each project holds **real copies** of what it uses, so a clone works for anyone, on any machine,
with or without Traycer. The `kit` command keeps those copies in step with this repository and never
overwrites anything without showing the diff first.

## Install on a machine

```bash
git clone <this repo> ~/agent-kit
ln -s ~/agent-kit/bin/kit ~/.local/bin/kit     # any directory on PATH
kit packs
```

Needs Python 3.11+ and git.

## Daily use

| You want to… | Run |
| --- | --- |
| Set up a brand-new repository | `kit init` (add `--with traycer`, `--with relay`, …) |
| Bring an existing agent setup under the kit | `kit adopt --dry-run`, then `kit adopt` |
| See what differs from the kit | `kit status` |
| Take kit improvements into this repository | `kit sync` (diff shown, asked file by file) |
| Send an edit you made here back to the kit | `kit push <path>` |
| Make a project skill or file shared | `kit push --new <path> --pack core` |
| Install an optional pack later | `kit add relay` / `kit remove relay` |
| Make skills visible to another AI tool | `kit target add grok` |
| Check this machine and repository | `kit doctor` |

Direction is always explicit: `sync`/`add` copy kit → repository, `push` copies repository → kit and
commits here. Then `git push` this repository so other machines get it.

## What's in it

```
bin/kit            the command
packs/core/        every repository gets this
  skills/          13 skills (writespec, speccheck, handoff, kickoff, …)
  files/           docs/workflows/*, docs/agent_setup/*, ORCHESTRATION.md, tools/*
  agents_block.md  the shared rules inserted into each AGENTS.md
  permissions.toml deny rules → Claude, opencode and Codex formats
  hooks.toml       Claude and Codex hooks for writespec-guard and spend-guard
  files/.opencode/ the opencode plugin that runs the same guards
  gitignore_block  shared .gitignore lines
packs/traycer/     delegation through Traycer; inert without Traycer
packs/relay/       Codex TUI orchestration through an A2A hub (needs traycer)
packs/mcp-*/       one MCP server each, written into all three clients' configs
templates/         starter files `kit init` copies once; the project owns them afterwards
docs/DESIGN.md     why it works the way it does
docs/COMMANDS.md   every kit command, one line each
```

## Rules

- **No global skills.** Nothing goes in `~/.claude/skills`, `~/.agents/skills` or any other home
  skill folder. A skill is either project-only or lives here.
- Project facts (commands, known failures, quirks) live in each repository's
  `docs/project_profile.md`, never in kit files. Kit workflows refer to the profile instead.
- Generic content only. A rule that only makes sense for one project belongs in that project.
