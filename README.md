# my-configs

Personal configuration and tooling, version-controlled. **This repo is
the source of truth** — everything is installed by symlinking it into
the place each tool expects, so a `git pull` here updates every machine
at once with no re-copying.

## Get the repo

```sh
git clone https://github.com/vishwajayawickrama/my-configs.git ~/Codes/my-configs
# or, if already cloned:
cd ~/Codes/my-configs && git pull
```

## Install: symlink what you want

The general pattern is the same for everything in this repo — point a
symlink from the location a tool reads at the file or directory here:

```sh
ln -sfn ~/Codes/my-configs/<source> <destination-the-tool-reads>
```

(`-s` makes it a symlink, `-f` replaces an existing link, and `-n`
keeps an existing symlink from being followed into.)

Each subdirectory has its own `README.md` with the exact source and
destination paths, plus any reload/restart step:

| Config | What it is |
|--------|------------|
| [`skills/`](skills/README.md) | Reusable agent skills (Claude Code, Codex, or anything that reads a skills directory). |
| [`plugins/`](plugins/README.md) | Installable Codex plugins with bundled skills and MCP servers. |
| [`ghostty/`](ghostty/README.md) | [Ghostty](https://ghostty.org) terminal configuration. |

## Updating

```sh
cd ~/Codes/my-configs && git pull
```

The symlinks already point at the updated files.
