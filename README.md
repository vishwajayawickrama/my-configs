# my-configs

Personal configuration and tooling, version-controlled. **This repo is
the source of truth** — most configurations are installed by symlinking
them into the place each tool expects. Application-specific imports, such
as HandBrake presets, are documented in their own directories.

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
| [`.agents/`](.agents/) | Workspace skill and MCP discovery for Antigravity and other tools that support the shared `.agents/skills` convention. |
| [`skills/`](skills/README.md) | Reusable agent skills (Claude Code, Codex, or anything that reads a skills directory). |
| [`plugins/`](plugins/README.md) | Installable Codex plugins with bundled skills and MCP servers. |
| [`ghostty/`](ghostty/README.md) | [Ghostty](https://ghostty.org) terminal configuration. |
| [`handbrake/`](handbrake/README.md) | Lecture encoding presets for HandBrake, imported through the app. |

## Updating

```sh
cd ~/Codes/my-configs && git pull
```

Symlinks already point at the updated files. For configurations installed
through an app import, follow the update steps in that directory’s README.
