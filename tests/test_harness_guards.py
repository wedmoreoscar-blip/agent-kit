"""The kit's guards in Codex and opencode (plan docs/plans/2026-11-06-guards-codex-opencode.md).

Run from the kit root: python3 -m unittest discover -s tests
Standard library only; the opencode plugin cases need `node` and are skipped without it.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
TOOLS = KIT / "packs/core/files/tools"
PLUGIN = KIT / "packs/core/files/.opencode/plugins/kit-guards.js"


def load(name: str, path: Path):
    loader = SourceFileLoader(name, str(path))
    module = module_from_spec(spec_from_loader(name, loader))
    sys.modules[name] = module
    loader.exec_module(module)
    return module


guard = load("writespec_guard", TOOLS / "writespec-guard")
kit = load("kit_cli", KIT / "bin/kit")


def run_guard(payload: dict) -> str:
    result = subprocess.run([sys.executable, str(TOOLS / "writespec-guard")], input=json.dumps(payload),
                            capture_output=True, text=True, check=False, timeout=30)
    return result.stdout


class ExtractNative(unittest.TestCase):
    def test_claude_behaviour_is_unchanged(self):
        agent = lambda **kw: {"tool_name": "Agent", "tool_input": {"prompt": "Build it", "description": "x", **kw}}
        self.assertEqual(guard.extract_native(agent(isolation="worktree")), "Build it")
        self.assertIsNone(guard.extract_native(agent()))
        # A Claude research subagent that only mentions a worktree is still not a commission.
        self.assertIsNone(guard.extract_native(
            {"tool_name": "Task", "tool_input": {"prompt": "Read the worktree docs", "description": "x"}}))

    def test_codex_spawn_agent_is_a_commission_when_it_names_a_worktree(self):
        for name in ("spawn_agent", "Agent"):
            spawn = lambda message: {"tool_name": name, "tool_input": {"task_name": "t", "message": message,
                                                                        "fork_turns": "none"}}
            self.assertIn(".worktrees/a", guard.extract_native(spawn("Work only in the worktree .worktrees/a")))
            self.assertIsNone(guard.extract_native(spawn("Explore the repo and report")))

    def test_codex_items_input_is_read_too(self):
        payload = {"tool_name": "spawn_agent",
                   "tool_input": {"task_name": "t", "items": [{"type": "text", "text": "Use worktree w"}]}}
        self.assertIn("worktree w", guard.extract_native(payload))

    def test_opencode_task_is_a_commission_when_it_names_a_worktree(self):
        task = lambda prompt: {"tool_name": "task", "tool_input": {"description": "d", "prompt": prompt,
                                                                    "subagent_type": "general"}}
        self.assertIn("worktree", guard.extract_native(task("Edit only in worktree x")))
        self.assertIsNone(guard.extract_native(task("Find the config file")))

    def test_malformed_input_is_not_a_commission(self):
        self.assertIsNone(guard.extract_native({"tool_name": "spawn_agent", "tool_input": "x"}))
        self.assertIsNone(guard.extract_native({}))


class GuardEndToEnd(unittest.TestCase):
    def test_codex_commission_without_spec_is_denied_and_exploration_passes(self):
        denied = run_guard({"tool_name": "spawn_agent", "hook_event_name": "PreToolUse",
                            "tool_input": {"task_name": "t", "message": "Build it in worktree w"}})
        self.assertEqual(json.loads(denied)["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(run_guard({"tool_name": "spawn_agent",
                                    "tool_input": {"task_name": "t", "message": "Explore"}}), "")


class CodexHooks(unittest.TestCase):
    def test_hooks_json_has_both_guards_with_git_root_commands(self):
        hooks = kit.codex_hooks(["core"])["hooks"]["PreToolUse"]
        self.assertEqual([h["matcher"] for h in hooks], ["^(Bash|Agent|spawn_agent)$", "^Bash$"])
        commands = [h["hooks"][0]["command"] for h in hooks]
        self.assertEqual(commands, ['"$(git rev-parse --show-toplevel)/tools/writespec-guard"',
                                    '"$(git rev-parse --show-toplevel)/tools/spend-guard"'])
        self.assertTrue(all(h["hooks"][0]["timeout"] == 10 for h in hooks))

    def test_claude_hook_entries_are_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            units = kit.hook_units(Path(directory), ["core"])
        claude = [u.value for u in units if getattr(u, "path", "") == ".claude/settings.json"
                  or str(getattr(u, "path", "")).endswith(".claude/settings.json")]
        self.assertEqual(claude, [
            {"matcher": "Bash|Agent|Task", "hooks": [{"type": "command",
             "command": '"${CLAUDE_PROJECT_DIR}/tools/writespec-guard"', "timeout": 10,
             "statusMessage": "Checking writespec compliance..."}]},
            {"matcher": "Bash", "hooks": [{"type": "command",
             "command": '"${CLAUDE_PROJECT_DIR}/tools/spend-guard"', "timeout": 10,
             "statusMessage": "Checking delegation spend ledger..."}]},
        ])
        codex = [u for u in units if str(getattr(u, "path", "")).endswith(".codex/hooks.json")]
        self.assertEqual(len(codex), 1)
        self.assertEqual(json.loads(codex[0].kit_text()), kit.codex_hooks(["core"]))


@unittest.skipUnless(shutil.which("node"), "node not installed")
class OpencodePlugin(unittest.TestCase):
    def decide(self, tool, args, stdout="", status=0, error=False, guards=("writespec-guard", "spend-guard")):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "tools").mkdir()
            for name in guards:
                (Path(root) / "tools" / name).write_text("")
            script = f"""
                import {{ KitGuards }} from {json.dumps(PLUGIN.as_uri())}
                const calls = []
                const run = (path, args, opts) => {{
                  calls.push({{ path, payload: JSON.parse(opts.input) }})
                  return {json.dumps({"stdout": stdout, "status": status})}
                    {"&& { error: new Error('boom') }" if error else ""}
                }}
                const reason = KitGuards.decide({json.dumps(root)}, {json.dumps(tool)}, {json.dumps(args)}, run)
                console.log(JSON.stringify({{ reason, calls }}))
            """
            out = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True,
                                 text=True, check=True, timeout=30).stdout
            result = json.loads(out)
            for call in result["calls"]:
                call["path"] = Path(call["path"]).name
            return result

    def test_deny_returns_the_reason_and_sends_a_claude_shaped_payload(self):
        deny = json.dumps({"hookSpecificOutput": {"permissionDecision": "deny",
                                                  "permissionDecisionReason": "no spec"}})
        result = self.decide("bash", {"command": "traycer agent send x --message y"}, stdout=deny)
        self.assertEqual(result["reason"], "no spec")
        self.assertEqual(result["calls"][0]["path"], "writespec-guard")
        self.assertEqual(result["calls"][0]["payload"]["tool_name"], "Bash")
        self.assertEqual(result["calls"][0]["payload"]["tool_input"]["command"],
                         "traycer agent send x --message y")

    def test_allow_runs_both_guards_for_bash_and_one_for_task(self):
        self.assertEqual([c["path"] for c in self.decide("bash", {"command": "ls"})["calls"]],
                         ["writespec-guard", "spend-guard"])
        task = self.decide("task", {"prompt": "p"})
        self.assertIsNone(task["reason"])
        self.assertEqual([(c["path"], c["payload"]["tool_name"]) for c in task["calls"]],
                         [("writespec-guard", "task")])

    def test_other_tools_and_failing_or_missing_guards_let_the_call_through(self):
        self.assertEqual(self.decide("read", {"filePath": "x"})["calls"], [])
        self.assertIsNone(self.decide("bash", {"command": "ls"}, stdout="not json")["reason"])
        self.assertIsNone(self.decide("bash", {"command": "ls"}, status=1,
                                      stdout='{"hookSpecificOutput": {"permissionDecision": "deny"}}')["reason"])
        self.assertIsNone(self.decide("bash", {"command": "ls"}, error=True)["reason"])
        self.assertEqual(self.decide("bash", {"command": "ls"}, guards=())["calls"], [])


if __name__ == "__main__":
    unittest.main()
