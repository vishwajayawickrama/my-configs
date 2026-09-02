# Skills

Reusable agent skills. **This repo is the source of truth** — coding
agents (Claude Code, Codex, or anything else that reads a skills
directory) get them via symlinks, so a `git pull` here updates every
tool at once with no re-copying.

## 1. Get the repo

```sh
git clone https://github.com/vishwajayawickrama/my-configs.git ~/Codes/my-configs
# or, if already cloned:
cd ~/Codes/my-configs && git pull
```

## 2. Symlink into your agent's skills directory

Each skill is one directory containing a `SKILL.md`. Link the ones you
want (or all of them) into the tool's skills root:

| Tool | Skills directory |
|------|------------------|
| Claude Code (personal) | `~/.claude/skills/` |
| Claude Code (per-project) | `<project>/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Other agents | wherever that tool discovers skills |

Link a single skill:

```sh
ln -s ~/Codes/my-configs/skills/beej-guide ~/.claude/skills/beej-guide
```

Link **all** skills in this repo (repeat with the appropriate target
directory for each tool):

```sh
mkdir -p ~/.claude/skills
for s in ~/Codes/my-configs/skills/*/; do
    ln -sfn "${s%/}" ~/.claude/skills/"$(basename "$s")"
done
```

(`-n` keeps an existing symlink from being followed into; `-f`
replaces it. The loop skips nothing — this README isn't a directory,
so it won't be linked.)

## 3. Restart the agent session

Most tools discover skills at session start. After linking, start a
new session and the skills are invocable (e.g. `/beej-guide` in
Claude Code).

## Updating

```sh
cd ~/Codes/my-configs && git pull
```

That's it — the symlinks already point at the updated files.

## Adding a new skill

1. Create `skills/<skill-name>/SKILL.md` with `name:` and
   `description:` frontmatter (supporting files in `references/` and
   `assets/` subdirectories as needed).
2. Commit, push, re-run the link-all loop on each machine.
3. Add a row to the skill index in the repo's top-level `README.md`.

## Current skills

| Skill | What it does |
|-------|--------------|
| `beej-guide` | Writes a full-length technical guide/book on any topic in the style of Beej's Guides (beej.us) — friendly voice, chapter projects, exercises, verified examples — producing PDF + split-per-chapter HTML. |
| `lecture-decks-to-academic-notes` | Converts lecture decks into concise, coverage-audited academic LaTeX notes and a compiled PDF, with OCR support, semantic list formatting, configurable page limits, navigation bookmarks, and visual verification. |
| `model-paper-creator` | Creates challenging, syllabus-complete model examination papers that reproduce supplied past-paper structure in clean LaTeX while keeping every question original across the set. |
| `video-to-slide-deck` | Extracts high-resolution, OCR-searchable PDF slide decks from lecture and presentation video recordings (MP4, MKV, MOV) with canvas auto-cropping, UI overlay removal, slide deduplication, and hierarchical Table of Contents bookmarks. |
