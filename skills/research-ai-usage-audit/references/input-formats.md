# Input extraction and location references

## Markdown and plain text

Read the original directly. Preserve line numbers with `nl -ba`. Exclude YAML/front matter, bibliography, code fences, tables, and image captions from prose counts when appropriate. Use absolute clickable file links in the final report.

## PDF

Prefer a layout-preserving extraction such as `pdftotext -layout`. The bundled analyzer falls back to `pypdf` when available; in Codex desktop, the bundled workspace Python normally provides it. Check the page count and render representative pages when layout, columns, equations, or scanned pages may corrupt reading order. Use OCR only when ordinary extraction is empty or clearly incomplete. Preserve page boundaries so findings can cite PDF page numbers. Compare extracted headings and references against rendered pages before relying on counts.

## DOCX

Extract paragraphs, heading styles, footnotes where available, and table text. Preserve heading names and sequential paragraph numbers. DOCX has no stable visual page numbers unless rendered; if page citations matter, render to PDF and cite the rendered pages. Do not save the document from Word or alter its package contents.

## Extraction-quality gate

Before analysis, verify:

- Character and word counts are plausible.
- Major headings occur in the expected order.
- Multi-column PDF text is not interleaved.
- Ligatures and hyphenated line breaks have not distorted vocabulary counts.
- References are separable from body prose.
- Tables, equations, and code have not been misclassified as sentences.

If extraction is materially unreliable, report the limitation and avoid a document-wide percentage until the text is recovered correctly.
