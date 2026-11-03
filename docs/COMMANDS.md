# kit commands

Run these from inside a project repository (except `kit packs`). Direction is always explicit:
`sync` and `add` copy kit → repository; `push` copies repository → kit and commits here.

| Command | What it does |
| --- | --- |
| `kit init [--with PACK …]` | Set up a brand-new repository: starter files, core pack (plus any packs named), receipt. Runs `git init` if needed. Refuses if the repo already has agent files. |
| `kit adopt [--with PACK …] [--dry-run]` | Bring a repository that already has its own agent setup under the kit. Lists identical, new and differing files first; then asks per differing file: take kit, keep repo, or push repo's version to the kit. `--dry-run` only shows the plan. |
| `kit status` | Read-only. What differs from the kit (kit updated, edited here, both changed, new, removed) and new kit commits since the last sync. |
| `kit sync` | Bring kit updates in, file by file, showing each diff and asking first. Never overwrites a file edited in this repo. |
| `kit sync --discard` | Also offer to replace locally edited files with the kit's version (still asks per file). |
| `kit sync --yes` | Apply all updates and installs without asking (never discards local edits). |
| `kit push PATH …` | Send local edits of kit-owned files back to the kit, commit them there, and update the other skill copies in this repo. |
| `kit push --new PATH --pack PACK` | Add a project file or whole skill folder to the kit, in the named pack. |
| `kit add PACK` | Install an optional pack later (e.g. `traycer`, `relay`, `mcp-playwright`, `mcp-context7`). |
| `kit remove PACK` | Uninstall a pack; asks before removing files edited here. |
| `kit target add TOOL` | Mirror all skills into another AI tool's project folder (`cursor`, `grok`, `kimi`, `kiro`, `droid`, `qwen`). |
| `kit target remove TOOL` | Remove that tool's skill copies. |
| `kit packs` | List available packs and what they need. |
| `kit doctor` | Check this machine and repository: kit on PATH, kit clean, receipt valid, skill copies identical, Codex trust, no personal skills in home folders, Traycer guide current. |
| `kit doctor --fix` | Apply the safe fixes it finds, asking before each. |
| `kit dismiss PATH …` | Stop `status`, `sync`, `push` and `doctor` reporting the kit files at PATH in this repository (a file, a folder, or a skill folder, which covers every tool copy of it). The repository's own file there is left alone. Kept in `.agent-kit.lock`, so it is committed. Without PATH, lists what is dismissed. |
| `kit undismiss PATH …` | Report and sync them again; the next `sync` treats them as new or differing. |

After `kit push`, run `git -C ~/agent-kit push` so other machines get the change (once the kit has a
remote).
