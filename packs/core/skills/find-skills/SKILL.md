---
name: find-skills
description: Finds and installs an existing third-party skill or Claude Code plugin for a capability. Searches what is installed, the official plugin marketplaces, OpenAI's curated skills, skills.sh and GitHub, reviews every file, and installs into this project only after approval. Use when asked to find, search for, recommend or install a skill or plugin. Not for ordinary how-to questions, and not for writing a new skill (that is skill-writing).
---

Work in the repository root. Download only into the session's scratch directory (`<scratch>` below);
nothing enters the repo before step 4. Never run a downloaded script.

## 1. Search, in this order

Run every source within a stage; stop after the first stage that yields fitting candidates. In the
report, mark each source as searched (with or without hits) or skipped.

1. **Already here:** `ls .claude/skills`; `claude plugin list --json`; `ls ~/.claude/skills
   ~/.agents/skills` (should be empty here: report anything found).
2. **Official sources.** Only these two count as official.
   - Claude Code marketplaces. The output is large JSON (`{"installed": [...], "available": [...]}`),
     so filter it instead of reading it:
     ```bash
     claude plugin list --available --json | python3 -I -c 'import json,re,sys; q=re.compile(sys.argv[1],re.I); d=json.load(sys.stdin)["available"]; [print(p["pluginId"], "|", p.get("description","")[:120]) for p in d if q.search(p["name"]+" "+p.get("description",""))]' '<regex>'
     ```
     Entries from `claude-plugins-official` are Anthropic's curated catalogue and count as official.
     Entries from `anthropic-plugin-directory` are community plugins.
   - OpenAI's curated skills: `git clone -q --depth 1 --filter=blob:none --sparse
     https://github.com/openai/skills <scratch>/openai-skills`, then `git -C <scratch>/openai-skills
     sparse-checkout set skills/.curated`, then grep `^description:` across
     `skills/.curated/*/SKILL.md`.
3. **skills.sh index:** `npx --yes skills find <keywords> < /dev/null` (`--owner <owner>` narrows).
   Search only. Never `npx skills add`, which symlinks by default, writes a lockfile and sends
   telemetry.
4. **GitHub, for anything not indexed:** `gh search code "<keywords> filename:SKILL.md"` and
   `gh search repos "<keywords> skill" --json fullName,stargazersCount,pushedAt`.

## 2. Review the best few

Review at most five, best fits first. Fetch the exact commit that would be installed. A plain
shallow clone only has the newest commit:

```bash
git init -q <scratch>/<name> && git -C <scratch>/<name> fetch -q --depth 1 <repo-url> <sha-or-branch> && git -C <scratch>/<name> checkout -q FETCH_HEAD
```

Use the `sha` from a marketplace entry, otherwise the default branch. Record the commit (`git -C
<dir> log -1 --format='%H %cs'`) and the licence (`gh api repos/<owner>/<repo> --jq
.license.spdx_id`). Read every file and note:

- scripts and what they execute; network calls; reads of credentials, keys or environment variables;
  writes outside the skill's own folder; `git push`, releases or other outward actions;
- plugin components: `hooks/` (run on every matching tool call), `.mcp.json` (servers started with
  your permissions), agents and commands;
- instructions to skip confirmations, widen permissions or fetch more code or instructions;
- minified or obfuscated code, and bundled binaries.

If a candidate is too large to read in full, say which files you read. It is "partly reviewed" and
is not offered for installation unless the user accepts that.

## 3. Shortlist for the user

Show only reviewed candidates that fit; add weaker partial matches only if labelled as such. For each:
what it does, kind (skill or plugin), source URL and commit, last commit date, licence, review
findings, and recommended install route. Rank official, then maintained, then popular. Install counts
and stars are weak hints and are often missing.

## 4. Install, only after the user approves that item

- **Route A: a skill, or a plugin containing only skills, with a licence that permits copying.**
  Copy the skill folder to `.claude/skills/<name>/` (the name must not clash with an existing skill).
  Reduce the frontmatter to `name` and `description`, add `agents/openai.yaml` if missing, keep any
  `LICENSE`, and write `ORIGIN.md` (below). Copy the folder byte-identically to
  `.agents/skills/<name>/` (no symlinks). Run `tools/check-agent-setup` and fix every failure.
  The skill is then invoked as `/<name>` (a plugin's skill would have been `/<plugin>:<name>`).
- **Route B: a plugin with hooks, MCP servers, agents or commands, or with no licence:**
  `claude plugin install <plugin>@<marketplace> --scope project`. This records it in
  `.claude/settings.json` without copying its files into the repo, and works in Claude Code only. A
  marketplace not yet added gets added to user settings, so ask first.
- Never install with `-g`, `--scope user` or `--scope local`, into a home directory, or with Codex's
  skill-installer (its default destination is `~/.codex/skills`).

`ORIGIN.md`, in a skill installed by route A:

```text
source: https://github.com/<owner>/<repo>/tree/<commit>/<path>
commit: <full sha>
fetched: <YYYY-MM-DD>
licence: <SPDX id>
local changes: <e.g. frontmatter keys removed: license, metadata; agents/openai.yaml added>
```

## 5. Nothing suitable

Say so, then offer to do the task directly, or to write a skill with `skill-writing` if it will
recur.
