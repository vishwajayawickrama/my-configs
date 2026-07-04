# my-configs

Personal configuration and tooling, version-controlled.

## skills/

Claude Code skills. **This repo is the source of truth** — install a
skill by symlinking it into `~/.claude/skills/`, so edits here are
live immediately:

```
ln -s "$(pwd)/skills/beej-guide" ~/.claude/skills/beej-guide
```

(On a machine where this repo isn't cloned, `cp -R` works too — but
then remember the copy won't track updates.)

| Skill | What it does |
|-------|--------------|
| `beej-guide` | Writes a full-length technical guide/book on any topic in the style of Beej's Guides (beej.us): friendly voice, chapter projects, exercises, verified examples, PDF + split HTML output. Includes the style dossier and build templates. |
