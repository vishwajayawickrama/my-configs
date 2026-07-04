---
name: beej-guide
description: Write a full-length technical guide/book in the style of Beej's Guides (beej.us) on any topic, producing both PDF and split-per-chapter HTML. Use when the user asks for a "Beej-style guide", a friendly example-first tutorial book, or a fun-but-rigorous guide to a language, tool, or framework.
---

# Beej-Style Guide Author

Produce a complete tutorial book: conversational Beej voice, chapter
projects, exercises, verified examples, PDF + split HTML from one
Markdown source. The reference implementation of this workflow is
`~/Codes/docs/ballerina-for-impatient-people/` ("Ballerina for
Impatient People") — consult it for a worked example of everything
below.

## Phase 0 — Scope with the user

Ask (once, up front): topic + target version, book size (full ~16
chapters / compact ~8), HTML form (split per chapter vs single page),
title, author byline. Never title it "Beej's ..." — credit Beej in the
Acknowledgments instead.

## Phase 1 — Research and accuracy (mandatory, before writing)

The foreword will promise "every example was compiled and run, and the
output shown is real." Make that true:

1. **Pin the version.** WebSearch/WebFetch the official docs and
   release notes *at writing time*; state the verified version in the
   foreword (footnote) and use only features that exist in it. Do not
   write from memory for anything version-sensitive: current version
   numbers, CLI flags, API signatures, install commands — fetch and
   confirm against primary sources (official docs > spec > release
   notes > blog posts).
2. **Executable topics** (languages, CLIs, frameworks): locate the
   toolchain (`which X`, version check). Keep an `examples/` scratch
   tree, one directory per chapter. **Every code example that appears
   with output must have been run**; paste transcripts verbatim. Batch
   verification runs (one file exercising many claims) to save time.
   Verify BEFORE writing the chapter, not after.
3. **Failures are content.** When a "should work" example fails to
   compile or behaves unexpectedly, that's a gift: quote the real
   error message in a Protip. The best material in a Beej-style book
   is honestly documented sharp edges. Also: if a verified fact
   contradicts something written earlier (in this book or a companion
   doc), fix the earlier text and tell the user.
4. **Unverifiable claims** (cloud consoles, paid services, things you
   can't execute): source them from docs fetched this session, hedge
   explicitly ("as of <version/date>"), or cut them. Never invent
   terminal output, version numbers, or API responses.
5. **Live network examples**: prefer stable public endpoints (e.g.
   jsonplaceholder.typicode.com) or spin up a local server from a
   later/earlier chapter and test client and server against each other
   — then say so in the book; readers love the circularity.

## Phase 2 — Scaffold and toolchain

Copy the templates from `assets/` (build.sh, style.css,
metadata.yaml) into a new book directory:

```
<book-slug>/
  metadata.yaml   style.css   build.sh   [<lang>.xml]
  chapters/NN-slug.md          # 01..NN, appendices last
  out/                         # generated: PDF + html/
  examples/chNN/               # scratch verification code (not shipped)
```

- Pipeline: pandoc → pdflatex for the PDF; pandoc per chapter for
  split HTML with prev/Contents/next nav + generated index.html (the
  build.sh template does all of this).
- If pandoc's highlighter lacks the language, write a KDE-syntax
  `<lang>.xml` (see the ballerina.xml in the reference book) and pass
  `--syntax-definition`.
- **Build a one-chapter skeleton first** and fix toolchain problems
  before writing 90 pages. Known trap: BasicTeX lacks `framed.sty` /
  `xurl.sty` — no sudo needed: drop the .sty files into
  `~/Library/texmf/tex/latex/<pkg>/` (macOS) and kpsewhich finds them.
- Rebuild after every 3–4 chapters, not only at the end.

## Phase 3 — Book structure

Write `outline.md` FIRST: numbered chapter list with one-line scope
each. This file is the **source of truth for all cross-references**;
get user sign-off on it. The Beej blueprint:

1. Foreword — fixed subsections: opening joke (absurd code sample,
   deflated), Audience, How to Read This Book, Platform and Tools
   (with pinned version), Copyright, Acknowledgments (credit Beej's
   Guides explicitly).
2. "What is X, Anyway?" — history, philosophy, honest "what it's NOT
   for" section, comparison table with neighbors.
3. "Hello, X!" — install, first program **dissected line by line**,
   break it on purpose and read the error, real project layout.
4. Foundation chapters (variables → control flow → functions →
   core data structures).
5. The deep/distinctive chapters — whatever makes this topic itself.
6. A capstone chapter whose project ties earlier chapters together
   (ideally earlier chapters' code tests it, or vice versa).
7. "Common Questions" — rapid-fire FAQ chapter (steal the format from
   Beej's network guide).
8. Appendix A: reference cheat sheet, man-page terse.
9. Appendix B: ALL exercise solutions (collect while writing).
10. Appendix C: tooling/ecosystem tour ("beyond hello world").

## Phase 4 — Chapter depth (write DENSE chapters)

Per-chapter skeleton, in order: **Objective** (bullets) → **The
Chapter Project** (concrete spec with sample transcript, up front) →
concept sections → **The Chapter Project** (built top-down in
numbered get-it-working-first steps) → **Exercises** → **Summary**
(bullets).

Density floor per chapter — do not write thin chapters:

- 2,500–4,500 words; 4–7 concept sections.
- Every concept: motivation → short runnable example (3–15 lines) →
  **real output shown** → explanation of the output → at least one
  edge case, failure mode, or gotcha.
- Hard concepts get **two or more analogies** (Beej gives pointers
  Post-its AND house addresses AND paper-copying).
- At least one **Protip** or **Fun Fact** callout (blockquote with
  bold label) per chapter; 1–3 footnotes (tangents, jokes, honest
  asides) per chapter.
- An "Interlude" section when theory needs a home; comparison tables
  where the topic invites them.
- Exercises: 3–6, imperative voice ("Write a function that..."),
  include one observe-the-error exercise; state the house rule once
  in the foreword: 20 minutes stuck → Appendix B allowed.
- Voice: first person, address the reader as "you", deploy humor
  BEFORE hard concepts then deflate it, be honest about sharp edges,
  use explicit deferrals. Full voice dossier with verbatim Beej
  quotes: `references/style-dossier.md`. Read it before writing
  chapter 1, and re-skim if chapters start sounding like
  documentation.

## Phase 5 — Cross-references

- Refer to chapters in prose as "Chapter N" (matching outline.md) —
  plain-text references survive both the concatenated PDF and split
  HTML. "Next chapter" is fine only for the adjacent chapter.
- **Footnote IDs must be globally unique across files** — the PDF
  build concatenates all Markdown. Prefix them: `[^ch7-elvis]`.
- Forward references are a feature ("we'll get to that in Chapter
  11") but every promise must pay off. Before final build:
  `grep -n "Chapter [0-9]" chapters/*.md` and check each reference
  against outline.md — right number, and the promised topic actually
  exists there. Do the same for "Appendix [A-C]".
- Exercises point to "Appendix B"; Appendix B restates
  chapter/exercise numbers so it works standalone.
- Renumbering chapters = rename files AND re-grep every "Chapter N"
  mention. Avoid by finalizing outline.md first.
- Callbacks are as valuable as forward refs: when a chapter reuses an
  earlier idea, say so by number ("Chapter 8's binding patterns,
  moonlighting"). This is what makes the book feel engineered.

## Phase 6 — Formatting rules (hard-won; violating these breaks the build)

- **ASCII only inside code blocks and verbatim** — pdflatex dies on
  `├ ↔ →` etc. ASCII trees (`|--`), arrows as words in prose.
- Long inline code spans cause overfull hboxes in the PDF: if a code
  span is over ~40 chars, move it to a display block or shorten it.
- Shell transcripts in plain ``` blocks (styled dark by the CSS);
  code in ```<lang> blocks for highlighting.
- Tables: pipe tables; escape `|` inside table cells as `\|`.

## Phase 7 — Final QA (all of these, every time)

1. Full `build.sh` run, zero pandoc/LaTeX errors.
2. Generate the intermediate .tex (`pandoc -s -o book.tex`), compile,
   then: `grep -E "^!"` (must be 0) and `grep Overfull` (fix anything
   > ~10pt by rewording).
3. Render 2–3 PDF pages to images and LOOK at them (title page, a
   code-heavy page): wrap `\includegraphics[page=N]` in a scratch
   .tex, then `sips` to PNG.
4. HTML: index has all chapter links; first page has empty prev, last
   has no next; spot-check a middle chapter's nav and highlighting
   spans.
5. Cross-reference grep (Phase 5) clean.
6. Page count and chapter count reported to the user, with the
   verification story (how many examples run, against which version).
