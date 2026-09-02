# Source-to-note workflow

## 1. Inventory and ordering

Create a deterministic inventory of all user-scoped decks. Sort by explicit lesson number or user order, not by filesystem accident. Record the filename, page/slide count, and extraction status. Exclude backups or `old` directories unless the user places them in scope.

## 2. Extraction and OCR

Extract text page by page while preserving page boundaries. Native extraction alone is insufficient for image-based slides, diagrams, screenshots, and scans.

- Flag pages with little or no native text.
- Render flagged pages at readable resolution and OCR them.
- Visually inspect diagrams, charts, matrices, timelines, and screenshots even when OCR returns text; capture their relationships, not merely disconnected labels.
- Treat title pages, logos, repeated module headers, and closing slides as decorative unless they carry substantive facts.

The included audit script writes per-page text and a manifest. Its word threshold is a triage signal, not a decision that a page is unimportant.

## 3. Coverage ledger

Maintain a ledger before and during drafting. Each substantive page should have one of these dispositions:

- `included` — mapped to a note section;
- `merged` — duplicate content consolidated elsewhere, with the destination recorded;
- `visual-captured` — the meaning of a diagram/chart is expressed in prose, bullets, a formula, or a compact table;
- `decorative` — no substantive teaching content; or
- `review` — unresolved and requiring another inspection.

Do not mark a page covered merely because its title appears in the note. Check its distinct claims, examples, qualifications, sequences, labels, and numerical information. Re-run a reverse audit after drafting: compare every source page with the finished note and resolve all `review` entries.

## 4. Structure and synthesis

Build a content map from lesson to section to subsection before writing. Merge repeated explanations without losing unique details. Preserve the source's intended logical order unless rearranging materially improves understanding; when rearranging, keep all dependencies clear.

Definitions should normally be an unboxed bold term followed by a precise explanation. A short academic note can still be complete: compress repeated wording, merge overlapping examples, and express stable comparisons in a table where useful.

### List decision rule

Use prose when the reader needs an argument or connected explanation. Use an unordered list when items are parallel and can be scanned independently. Use an ordered list only when order has meaning.

Correct pattern:

```latex
\noindent The process has four stages:
\begin{enumerate}
  \item identify the problem;
  \item evaluate alternatives;
  \item choose and implement a response; and
  \item review the result.
\end{enumerate}
```

The lead-in is flush left and outside the list. Configure a visible first-level left margin, and make nested lists incrementally deeper. Avoid isolated one-item lists, paragraph-length bullets containing several unrelated claims, and artificial fragmentation.

## 5. Navigation without a visible contents page

When the user asks for PDF navigation but no contents page, create an outline only. With `hyperref`, lesson commands can emit top-level `\pdfbookmark` entries while numbered `\subsection` and `\subsubsection` commands populate lower levels. Ensure bookmark destination identifiers are unique. Inspect the compiled outline rather than assuming it exists.

## 6. Page-limit management

Draft for completeness first, then tighten:

1. remove duplicated explanations;
2. shorten transitions and examples without deleting their instructional purpose;
3. combine parallel facts into well-formed lists;
4. use compact comparison tables selectively;
5. tune spacing conservatively; and
6. reduce type size only as a last resort while retaining readability.

Never satisfy a page cap by silently omitting substantive source content. If completeness and the cap are genuinely incompatible, report the trade-off and ask for direction.

## 7. PDF quality control

After compilation:

1. inspect the log for overfull/underfull boxes, missing glyphs, and unresolved references;
2. check page count and document metadata;
3. inspect embedded fonts when the user named an exact face;
4. inspect the bookmark outline and its hierarchy;
5. render all pages to images and examine a montage for density, blank pages, clipped material, and inconsistent whitespace;
6. inspect representative and suspicious pages at full size, especially pages with tables, formulas, nested lists, and lesson boundaries; and
7. search the source for forbidden meta-language and visually audit every list lead-in.

Compile again after any fix and repeat the checks affected by that change.
