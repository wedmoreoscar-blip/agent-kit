// The kit's guards in opencode (agent-kit core pack; `kit sync` keeps this file).
//
// Claude Code and Codex run tools/writespec-guard and tools/spend-guard as PreToolUse hooks. This
// plugin runs the same scripts before opencode's `bash` and `task` tools, with the payload shape
// the guards read, and throws on a denial: a throw from `tool.execute.before` blocks the call
// (checked 2026-11-06, opencode 1.18.33). A guard that is missing, crashes or times out lets the call
// through, as the guards themselves do on a malformed payload.
import { spawnSync } from "node:child_process"
import { existsSync } from "node:fs"
import { join } from "node:path"

const GUARDS = { bash: ["writespec-guard", "spend-guard"], task: ["writespec-guard"] }
const TOOL_NAMES = { bash: "Bash", task: "task" }

function decide(root, tool, args, run = spawnSync) {
  const guards = GUARDS[tool]
  if (!guards) return null
  const payload = JSON.stringify({ tool_name: TOOL_NAMES[tool], tool_input: args ?? {}, cwd: root })
  for (const name of guards) {
    const path = join(root, "tools", name)
    if (!existsSync(path)) continue
    const result = run(path, [], { input: payload, encoding: "utf8", timeout: 10000, cwd: root })
    if (result.error || result.status !== 0) continue
    let output
    try {
      output = JSON.parse(result.stdout || "{}").hookSpecificOutput
    } catch {
      continue
    }
    if (output?.permissionDecision === "deny") return output.permissionDecisionReason || `Blocked by ${name}`
  }
  return null
}

// opencode loads every export of a plugin file as a plugin, so the helper hangs off this one.
export const KitGuards = async ({ worktree, directory }) => {
  const root = worktree || directory
  return {
    "tool.execute.before": async (input, output) => {
      const reason = decide(root, input.tool, output.args)
      if (reason) throw new Error(reason)
    },
  }
}
KitGuards.decide = decide
