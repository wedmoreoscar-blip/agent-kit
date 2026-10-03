## Codex TUI relay

This section is managed by the agent kit's `relay` pack. It applies only when a Traycer-launched
Codex TUI is the orchestrator (`TRAYCER_AGENT_ID` and `TRAYCER_EPIC_ID` set). In every other session,
ignore it.

- Invoke `$codex-tui-relay` before kickoff or commissioning agents. The user creates the persistent
  OpenCode GUI hub `codex-tui-a2a-hub` once per epic; Codex records exact spawn/send commands and
  returned messages in the epic's single append-only artifact ledger, and the hub executes them.
  `docs/agent_setup/CODEX_TUI_MESSAGE_RELAY.md` is authoritative.
- Codex TUI is an orchestrator only, never an implementation target, and never calls a mutating
  Traycer agent command itself. The relay is a messaging adapter: `docs/workflows/delegation.md`
  still governs the work.
- `relay-waker` keeps the hub-waking daemon alive; see `docs/agent_setup/RELAY_WAKER.md`.
