# Ghostty

[Ghostty](https://ghostty.org) terminal configuration. **This repo is
the source of truth** — the config is symlinked into place, so a `git
pull` here updates your terminal with no re-copying.

## 1. Get the repo

```sh
git clone https://github.com/vishwajayawickrama/my-configs.git ~/Codes/my-configs
# or, if already cloned:
cd ~/Codes/my-configs && git pull
```

## 2. Symlink the config into place

Ghostty reads its config from one of two locations. Pick whichever you
prefer and link `ghostty/config` there.

| Platform / preference | Config path |
|-----------------------|-------------|
| macOS (default) | `~/Library/Application Support/com.mitchellh.ghostty/config` |
| XDG (`~/.config`) | `~/.config/ghostty/config` |

macOS default location:

```sh
mkdir -p ~/Library/Application\ Support/com.mitchellh.ghostty
ln -sfn ~/Codes/my-configs/ghostty/config \
    ~/Library/Application\ Support/com.mitchellh.ghostty/config
```

XDG location:

```sh
mkdir -p ~/.config/ghostty
ln -sfn ~/Codes/my-configs/ghostty/config ~/.config/ghostty/config
```

(`-n` keeps an existing symlink from being followed into; `-f`
replaces it.)

## 3. Reload the config

Ghostty reads the config at startup. Reload without restarting with
<kbd>Cmd</kbd>+<kbd>Shift</kbd>+<kbd>,</kbd> (macOS), or just open a
new Ghostty window.

## Updating

```sh
cd ~/Codes/my-configs && git pull
```

That's it — the symlink already points at the updated file.

## What's configured

`config` sets an iTerm2-style dark theme: a `#0f1115` background, a
light-grey foreground, and the full 16-colour ANSI palette. Everything
else is left at Ghostty's sensible defaults. See the inline comments in
`config` for a syntax crash course, or run `ghostty +show-config
--default --docs` for every available option.
