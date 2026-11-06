# Plan: the kit's guards in Codex and opencode (2026-11-06)

Status: **built 2026-11-06** (the user chose Q11 (a) in job-automation's
`tasks/questions/next-build.md`). Two findings changed the design below:

- **Codex probe not run:** auto mode refused `--dangerously-bypass-hook-trust`. The `spawn_agent`
  arguments were read from the Codex 0.160.1 binary instead: `task_name`, `message` or `items`,
  `fork_turns`, `model`; no worktree option.
- **Subagents in both harnesses are guarded after all.** Neither creates a worktree, so
  delegation.md's rule applies (the orchestrator creates one and names it in the spec): a
  `spawn_agent` or `task` call whose text names a worktree is a commission. The design's "`task` is
  left alone" is superseded.
- **opencode probe passed:** a throw from `tool.execute.before` blocked a `bash` call (opencode
  1.18.33, DeepSeek Flash; the command's file was never written).

## Problem

`writespec-guard` (no delegation without a spec) and `spend-guard` (the delegation spend ledger)
run only in Claude Code, through `packs/core/hooks.toml` merged into `.claude/settings.json`. In
Codex the kit writes only `.codex/rules/kit.rules` (push forbidden); in opencode only `permission`
entries in `opencode.json`. Neither guard runs there: the rule exists only as text in `AGENTS.md`.

## What the official docs say (read 2026-11-06)

**Codex** (https://learn.chatgpt.com/docs/hooks, redirected from developers.openai.com/codex/hooks;
installed: codex-cli 0.160.1):

- Hooks load from `~/.codex/hooks.json`, `~/.codex/config.toml` `[hooks]`, `<repo>/.codex/hooks.json`
  or `<repo>/.codex/config.toml`. One form per layer; both forms in one layer are merged with a
  warning. **The kit already owns a region of `.codex/config.toml`**, so `.codex/hooks.json` (a whole
  file the kit generates) is the cleaner choice.
- `PreToolUse` `matcher` is a regex over `tool_name` and its aliases. Shell and `exec_command` match
  as `Bash`; `apply_patch` as `apply_patch|Edit|Write`; MCP tools by full name; **`spawn_agent` also
  matches `Agent`**. (A third-party guide said the tool name was always "Bash": that is wrong.)
- Stdin carries `session_id`, `cwd`, `hook_event_name`, `tool_name`, `tool_use_id`, `tool_input`;
  for Bash, `tool_input.command`.
- Blocking: exit 2 with the reason on stderr, or stdout JSON
  `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
  "permissionDecisionReason": "..."}}`, which is exactly what both guards already print.
- Project hooks run only in a trusted project, and only after the user trusts each hook in `/hooks`
  (trust is recorded per hook hash, so a changed hook needs trusting again). Hooks are on by default
  (`[features] hooks = false` turns them off).
- `timeout` in seconds, default 600.

**opencode** (https://opencode.ai/docs/plugins; installed: 1.18.33):

- Project plugins: JS or TS files in `.opencode/plugins/`, loaded at startup (bundled Bun runtime;
  no Bun install needed on the machine).
- `export const P = async ({ project, client, $, directory, worktree }) => ({ "tool.execute.before":
  async (input, output) => { ... } })`; `input.tool` is the tool name (`bash`, `read`, ...),
  `output.args` its arguments (`output.args.command` for bash).
- The docs' `.env` example throws an `Error` to stop a call, but the docs never state that a throw
  blocks. **Unconfirmed: verify before relying on it** (build step 1).

## Design

One set of guards, thin adapters per harness. The guards stay the single source of every rule.

1. **Codex: `packs/core/codex_hooks.json` → `.codex/hooks.json`** (a generated whole-file unit, like
   `.codex/rules/kit.rules`):
   - `PreToolUse`, matcher `^(Bash|Agent)$` → `writespec-guard`; matcher `^Bash$` → `spend-guard`.
   - Command: `python3 "$(git rev-parse --show-toplevel)/tools/<guard>"` (Codex has no
     `CLAUDE_PROJECT_DIR`; `git rev-parse` is the docs' own pattern).
   - Generated from the same `hooks.toml` entries, so the two harnesses can't drift: each entry gets
     an optional `codex_matcher` (default: the Claude matcher with `Task` removed).
   - The Bash payload already has Claude's shape (`tool_name: "Bash"`, `tool_input.command`), so
     `spend-guard` and the `traycer agent send` plugin work unchanged.
   - A Codex subagent is a commission only when it runs in its own worktree, as with Claude. The
     `spawn_agent` input fields are not documented: capture one real payload (build step 1), then
     add a `codex` branch to `extract_native` for those fields. If `spawn_agent` has no worktree
     option, Codex subagents are not implementer commissions and the guard ignores them, as it
     ignores a Claude research subagent.
2. **opencode: `packs/core/files/.opencode/plugins/kit-guards.js`** (a plain file copied by sync):
   - On `tool.execute.before` for `bash`: builds the Claude-shaped payload
     `{tool_name: "Bash", tool_input: {command}, cwd: directory}`, runs both guards with it on stdin
     (Node `child_process.spawnSync`, which Bun supports; no `$` quoting problems), and on a deny
     throws `new Error(permissionDecisionReason)`.
   - `task` (opencode's subagent tool) runs in the same checkout with no worktree, so it is not an
     implementer commission; it is left alone, matching the Claude rule.
   - A guard that crashes or times out lets the call through (the guards' existing rule: never break
     the session on a malformed payload).
3. **`kit doctor`**: reports Codex hooks that exist but are not yet trusted (one line: open `/hooks`
   in Codex and trust the two kit hooks), and an opencode project without the plugin file.
4. **`AGENTS.md` block and `DESIGN.md`**: the "Spec enforcement" row says all three harnesses now
   run the guards, with Codex's trust step.

Claude Code is unchanged: `.claude/settings.json` and the guard scripts' Claude behaviour stay
byte-for-byte the same.

## Build steps (after the user answers Q11)

1. **Probe** in a scratch repository under the scratchpad (never a real project): a logging hook in
   Codex captures one `Bash` and one `spawn_agent` payload (`codex exec` with a trivial prompt); an
   opencode plugin that throws on `bash` proves whether the call is blocked (`opencode run`). One
   cheap model call each. If a throw does not block opencode, stop and report: the plugin route
   would need another mechanism (opencode `permission` rules cannot run a script).
2. Codex: `codex_matcher` in `hooks.toml`, the `.codex/hooks.json` unit in `bin/kit`, the Codex
   branch in `extract_native` if step 1 shows a worktree option.
3. opencode: the plugin file and its sync unit.
4. `kit doctor` checks; `DESIGN.md` and the `AGENTS.md` block.
5. **Tests** (the kit has none yet; add `tests/` with Python `unittest`, standard library only):
   - Guards fed Codex-shaped payloads: allowed and denied `traycer agent send`, a spend-ledger deny,
     a malformed payload allowed.
   - `kit init` into a temporary repository writes `.codex/hooks.json` with the expected matchers
     and commands, and leaves `.claude/settings.json` identical to today's output.
   - The plugin run under `node` with a stub guard: deny → throws with the reason; allow → returns;
     crashing guard → returns.
   - End to end, once by hand: a denied `traycer agent send` in Codex and in opencode, recorded in
     the commit message.
6. Commit in `~/agent-kit` (local only), then `kit sync` into job-automation and run its
   `tools/test-project quick`.

## Open items

- `traycer_send_message` over MCP (`mcp__traycer_a2a__traycer_send_message`) is not guarded in any
  harness, Claude included: the Claude matcher is `Bash|Agent|Task`. A follow-up could add an MCP
  extractor to the `traycer` pack; out of scope here unless the user wants it.
- Codex's per-hash trust means every guard change needs a re-trust in `/hooks`; `kit sync` should
  say so when it changes a hook.
