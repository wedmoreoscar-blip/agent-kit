# Updating Traycer (Linux / WSL)

Traycer has three parts that update separately: the **desktop app**, the **host** (the background
service agents run under) and the **`traycer` CLI**. Check the versions first:

```
dpkg -l traycer          # desktop app (.deb package, installed in /opt/Traycer)
traycer --version        # CLI
traycer host status      # host
```

## Desktop app

### Why `dpkg -i` can fail

The built-in updater has downloaded the **AppImage** into
`~/.cache/@traycer-clientsdesktop-updater/pending/` instead of the `.deb`. An AppImage is not a
Debian archive, so `dpkg -i` fails with "is not a Debian format archive". The fix is always to
install the `.deb` from the same release, with `apt`.

### Steps

1. **Quit the Traycer desktop app completely.**
2. **Get the `.deb`.** If the updater's pending folder holds `traycer-desktop-linux-amd64.deb`, use
   that. Otherwise download it from the GitHub release:
   ```
   curl -Lo ~/Downloads/traycer-desktop-linux-amd64.deb https://github.com/traycerai/traycer/releases/download/desktop-v<version>/traycer-desktop-linux-amd64.deb
   ```
   The latest version is the `tag_name` of
   `https://api.github.com/repos/traycerai/traycer/releases/latest`.
3. **Copy it into `~/Downloads`.** `apt` refused a path under `/tmp/claude-…` with "Unsupported
   file", and works from `~/Downloads`:
   ```
   cp ~/.cache/@traycer-clientsdesktop-updater/pending/traycer-desktop-linux-amd64.deb ~/Downloads/
   ```
4. **Install with `apt`, not `dpkg -i`**, so any new dependencies come too. `apt` needs the absolute
   path:
   ```
   sudo apt install "$HOME/Downloads/traycer-desktop-linux-amd64.deb"
   ```
   A notice that the download is "performed unsandboxed as root" is harmless.
5. **Check it:** `dpkg -l traycer` shows the new version. Start the app with `traycer-desktop`; the
   `~/.local/bin/traycer-desktop` launcher needs no change.
6. **Tidy up:** delete `~/Downloads/traycer-desktop-linux-amd64.deb` and
   `~/.cache/@traycer-clientsdesktop-updater/pending`.

### Optional: verify the download

The release's `latest-linux.yml` lists the `.deb`'s SHA-512 in base64. Compare it with:

```
sha512sum traycer-desktop-linux-amd64.deb | cut -d' ' -f1 | xxd -r -p | base64 -w0
```

## Host and CLI

```
traycer host available   # host versions in the registry
traycer host update      # update the host to the latest compatible release, then check it answers
traycer cli upgrade      # update the CLI (Desktop-installed and manual installs only)
```

`traycer cli upgrade` refuses CLIs installed by a package manager (Homebrew, npm, winget, Scoop,
apt, rpm) and names that manager's upgrade command instead. Updating the host restarts it, which
interrupts running agents, so update between sessions.

## After any update

- Agents spawned through the traycer pack's `claude-router` depend on Traycer's Claude Code binary
  setting (Settings ▸ Providers ▸ Claude Code ▸ custom path `~/.local/bin/claude-router`). Check it
  survived the update; if it reverted, every Claude agent runs plain Claude Code again.
- Re-run `kit doctor` in a repository to confirm the Traycer guide and home scripts are current.
