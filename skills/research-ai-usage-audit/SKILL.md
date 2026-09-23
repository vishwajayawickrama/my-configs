---
name: research-ai-usage-audit
description: Audit research papers in Markdown, PDF, DOCX, or plain text for evidence of AI-assisted writing using the current Wikipedia "Signs of AI writing" field guide, quantitative textual signals, close reading, citation checks, and calibrated uncertainty. Use when the user asks how much of a paper appears AI-written, requests an AI-usage or authorship-style report, or wants suspicious passages identified. Do not use as a plagiarism detector or as proof of misconduct.
---

# Research AI-Usage Audit

Produce an evidence-backed audit of AI-like writing while preserving the source file. Separate observable textual traits from claims about authorship.

## Non-negotiable constraints

- Never modify the source paper unless the user separately asks for revisions.
- Do not present a detector score, stylistic estimate, or human judgment as proof that AI was used.
- Distinguish:
  1. **Observed signal prevalence**: how much prose exhibits listed traits.
  2. **Likelihood of substantial AI assistance**: a calibrated whole-document judgment.
  3. **Authorship provenance**: normally indeterminable from text alone.
- Treat Wikipedia-specific markup clues as inapplicable or low-weight for ordinary Markdown, PDF, and Word papers.
- Exclude the bibliography, metadata, equations, tables, code, and verbatim quotations from prose-percentage estimates unless there is a reason to audit them separately.
- Quote sparingly. Prefer location-linked examples and paraphrase surrounding material.

## Required workflow

1. Resolve the input file and record its format, size, word count, and section structure. Read [references/input-formats.md](references/input-formats.md) when the input is PDF or DOCX, or when extraction quality is uncertain.
2. Fetch and read the current [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) page. Record the access date. Treat it as an evolving, descriptive field guide rather than a validated authorship test.
3. Read [references/audit-rubric.md](references/audit-rubric.md). Apply all relevant categories and explicitly mark irrelevant or unobserved categories rather than silently omitting them.
4. Run `scripts/analyze_ai_signals.py` on the paper for reproducible counts. Treat its output as leads for close reading, not a verdict.
5. Read the entire extracted paper. Inspect every section, including the abstract, introduction, methods, results or review body, discussion, conclusion, and references.
6. Verify high-value objective clues when present: leaked chatbot language, placeholders, malformed citation tokens, impossible or mismatched references, abrupt cutoffs, and unexplained style shifts. When citations are in scope, sample or validate identifiers against publisher or DOI metadata; state the coverage and any access failures.
7. Compare signals across sections. Identify whether the style is uniformly templated, clustered in likely rewritten passages, or plausibly explained by disciplinary conventions.
8. Produce the report defined below. If saving it to disk, choose a new file and never overwrite the source.
9. Verify that the source file has not changed. For a tracked file, use a path-scoped diff; otherwise compare a checksum captured before and after.

## Calibration

Do not calculate a fake probability by summing indicators. Use the following verbal scale, supported by explicit evidence:

- **Minimal**: isolated weak indicators with substantial natural variation.
- **Low**: several weak indicators but no consistent cross-section pattern.
- **Moderate**: recurring patterns in multiple sections, with plausible human or disciplinary explanations.
- **High**: dense co-occurrence of several independent indicator families across much of the prose.
- **Very high**: high-density linguistic signals plus objective artifacts or strong provenance evidence.

If the user requests a percentage, provide a **range for AI-like or likely AI-assisted prose**, not a precise generated-text percentage. Explain the denominator and uncertainty. Use section-level ranges before deriving a document-wide range. Do not score references as prose.

## Required report

Lead with the conclusion and confidence. Then include:

1. **Scope and limitations** — input, text included/excluded, Wikipedia access date, and why the result is not proof of authorship.
2. **Document-level assessment** — signal-prevalence range, likelihood rating, confidence, and a one-paragraph rationale.
3. **Section-level assessment** — section, words reviewed, prevalence range, confidence, dominant signals, and representative locations.
4. **Indicator matrix** — each relevant Wikipedia category, observed count or qualitative prevalence, strength, examples, counterevidence, and interpretation.
5. **Quantitative profile** — normalized counts as well as raw counts; repeated transitions, negative parallelisms, triads/enumerations, AI-associated vocabulary, sentence and paragraph regularity, formatting artifacts, and repeated n-grams.
6. **Close-reading findings** — explain why the strongest passages are suspicious in context. Include benign explanations and false-positive risks.
7. **Objective-artifact and citation audit** — distinguish checked, clean, suspicious, and not checked.
8. **Evidence against AI generation** — concrete specificity, uneven human syntax, source-grounded detail, revision history, or explainable disciplinary conventions.
9. **Final calibrated judgment** — separate likely assistance, apparent coverage, and unknowable provenance.
10. **Integrity statement** — confirm that the source was not modified and report the verification method.

Use clickable file links with line numbers for Markdown/text. For PDF, cite page numbers; for DOCX, use heading and paragraph numbers. Avoid allegations of misconduct or disciplinary recommendations unless the user explicitly asks for policy guidance.
