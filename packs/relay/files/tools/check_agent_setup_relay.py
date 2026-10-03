"""Relay pack checks for tools/check-agent-setup: the ledger helper works, and every part of the
relay stays reachable from the codex-tui-relay skill (its single entry point)."""
import subprocess
import tempfile
from pathlib import Path

MARKERS = (
    ("AGENTS.md", "$codex-tui-relay"),
    ("docs/agent_setup/CODEX_TUI_MESSAGE_RELAY.md", "codex-tui-a2a-hub"),
    ("docs/agent_setup/CODEX_TUI_HUB_SETUP.md", "HUB_READY"),
    (".agents/skills/codex-tui-relay/SKILL.md", "docs/agent_setup/CODEX_TUI_MESSAGE_RELAY.md"),
    (".agents/skills/relay-waker/SKILL.md", "docs/agent_setup/RELAY_WAKER.md"),
    ("docs/agent_setup/RELAY_WAKER.md", "a2a-hub-waker"),
    (".agents/skills/codex-tui-relay/SKILL.md", "docs/agent_setup/RELAY_WAKER.md"),
    (".agents/skills/codex-tui-relay/SKILL.md", "a2a-hub-waker"),
    (".agents/skills/codex-tui-relay/SKILL.md", "tools/waker-daemon-start"),
    ("docs/agent_setup/CODEX_TUI_MESSAGE_RELAY.md", "docs/agent_setup/RELAY_WAKER.md"),
    ("docs/agent_setup/CODEX_TUI_HUB_SETUP.md", "a2a-hub-waker"),
)
EXECUTABLE = ("tools/codex-tui-relay-ledger", "tools/relay-hub-waker", "tools/traycer-identity",
              "tools/waker-daemon-start")


def check(root: Path, fail) -> None:
    for relative, marker in MARKERS:
        path = root / relative
        if not path.is_file() or marker not in path.read_text():
            fail(f"relay: {relative} is missing marker {marker!r}")
    for relative in EXECUTABLE:
        path = root / relative
        if not path.is_file() or not path.stat().st_mode & 0o100:
            fail(f"relay: {relative} missing or not executable")
            return
    helper = root / "tools/codex-tui-relay-ledger"
    with tempfile.TemporaryDirectory(prefix="relay-check-") as directory:
        ledger = Path(directory) / "index.md"
        for command in (
            [str(helper), "init", "--ledger", str(ledger)],
            [str(helper), "append", "--ledger", str(ledger), "--type", "command.send",
             "--event-id", "01KZQ000000000000000000001", "--actor", "codex:test",
             "--ticket", "RELAY-TEST", "--target", "agent:test", "--content", "payload"],
            [str(helper), "append", "--ledger", str(ledger), "--type", "command.claimed",
             "--event-id", "01KZQ000000000000000000002", "--actor", "hub:test",
             "--ticket", "RELAY-TEST", "--target", "agent:test",
             "--command", "01KZQ000000000000000000001"],
            [str(helper), "validate", "--ledger", str(ledger)],
        ):
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            if result.returncode:
                fail(f"relay ledger regression: {(result.stderr or result.stdout).strip()}")
                return
