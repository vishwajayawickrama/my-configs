# Research-paper AI-writing audit rubric

Use this rubric after reading the current Wikipedia field guide. The source page is optimized for Wikipedia; this rubric adapts its observable signals to academic manuscripts without treating them as proof.

## Evidence hierarchy

### Tier 1 — objective artifacts

Give these the greatest weight when they cannot be explained by the document workflow:

- Chatbot-to-user language accidentally pasted into the manuscript.
- Prompt refusals, knowledge-cutoff disclaimers, answer labels, or offers to continue.
- Placeholder text, dummy dates, unfilled template fields, or abrupt output cutoffs.
- Leaked internal citation tokens such as `turn0search0`, `oaicite`, `contentReference`, `[cite: 1]`, `attributableIndex`, or similar model/app markup.
- Fabricated, unrelated, or internally inconsistent citations and identifiers.
- A pronounced, localized style shift that aligns with other AI-associated signals.

### Tier 2 — convergent content and rhetorical patterns

These become meaningful through density, repetition, and co-occurrence:

- Generic claims of importance, impact, significance, or broader relevance unsupported by specific evidence.
- Superficial synthesis appended with participial phrases such as “highlighting,” “ensuring,” “reflecting,” or “contributing to.”
- Vague attribution: “researchers argue,” “studies show,” or “critics note” without an identifiable source.
- Promotional or overly positive tone.
- Formulaic challenges/future-work conclusions that resolve into generic optimism.
- Repeated abstract distinctions that sound corrective: “not X but Y,” “not merely,” “rather than,” or “while X, Y.”
- Repeated triads and exhaustive enumerations used to simulate completeness.
- Uniform paragraph templates, such as method summary → benefit → qualification → limitation.
- Excessive claim calibration and symmetrical trade-offs that recur regardless of subject matter.
- Restatement across abstract, discussion, and conclusion with little added synthesis.

### Tier 3 — lexical and surface patterns

Count and normalize these, but never use them alone:

- High density of the current page’s AI-associated vocabulary, including words such as `additionally`, `align with`, `crucial`, `delve`, `emphasizing`, `enhance`, `fostering`, `highlighting`, `intricate`, `key`, `landscape`, `pivotal`, `robust`, `showcasing`, `underscore`, `valuable`, and `vibrant`.
- Avoidance of simple `is`/`are` constructions in favor of inflated verbs.
- Vague “associated with” or “connected to” phrasing.
- Excessive em dashes, title-case headings, boldface, emoji, inline-header lists, thematic breaks, or unnecessary tables.
- Unnaturally uniform sentence length, paragraph length, or sentence openings.
- Repeated transition vocabulary and repeated three-to-five-word phrases.

## Research-paper applicability matrix

| Wikipedia category | Academic-paper treatment |
|---|---|
| Significance/legacy inflation | Applicable; require claim-to-evidence checking |
| Notability/media coverage | Usually irrelevant except literature-positioning prose |
| Superficial analysis | Strongly applicable |
| Promotional language | Applicable |
| Vague attribution | Strongly applicable |
| Challenges/future prospects formula | Strongly applicable in discussion/conclusion |
| AI vocabulary density | Applicable only as a normalized co-occurrence signal |
| Copulative avoidance | Weak-to-moderate supporting evidence |
| Negative parallelisms | Strong when unusually dense and cross-sectional |
| Rule of three | Moderate supporting evidence |
| Markdown/wikitext artifacts | Markdown itself is irrelevant; leaked mixed markup remains relevant |
| Heading capitalization/bold/table style | Usually explained by journal or template conventions |
| Chatbot communication/placeholders | Strong objective evidence |
| Broken citations/invalid identifiers | Strong objective evidence after verification |
| Edit-summary/comment indicators | Not applicable unless reviewing revision metadata |
| Human-writing signs | Use as counterevidence, not proof |

## Counting rules

- Report raw counts and counts per 1,000 prose words.
- Count phrases case-insensitively and inspect every hit in context.
- Distinguish terminology required by the topic from stylistic preference. For example, `robust` in “robustness test” may be domain-specific.
- Do not count occurrences inside titles in the reference list as authorial prose.
- Treat enumerations as suspicious only when recurrent and rhetorically unnecessary. Methods sections naturally contain lists.
- Compare section densities; a high abstract density can be partly explained by compression.
- Use repeated n-grams as leads. Shared technical phrases and method names are not evidence.

## Section-level estimation

For each section, assign a prevalence range based on the proportion of prose materially shaped by convergent signals:

- 0–20%: sparse or isolated
- 20–40%: noticeable but localized
- 40–60%: mixed or uncertain
- 60–80%: widespread and recurrent
- 80–100%: pervasive, highly uniform, or supported by objective artifacts

These ranges describe **AI-like prose coverage**, not the literal percentage of tokens generated by a model. Weight the document estimate by prose word count, then widen the range when section boundaries, quotations, extraction quality, or disciplinary style create uncertainty.

## Counterevidence checklist

Actively look for:

- Precise, source-grounded claims that are correctly cited.
- Concrete methodological details, limitations tied to actual data, and non-generic failure cases.
- Natural variation in syntax, paragraph purpose, and authorial emphasis.
- Idiosyncratic but coherent reasoning that can be traced across revisions.
- Consistent terminology demanded by the field rather than elegant variation.
- Verified references and accurate quotations.
- Revision history or process evidence, while recognizing that incremental commits do not rule out AI assistance.
- The author’s ability to explain source selection, wording, and analytical choices. Do not infer this ability from the document alone.

## Prohibited conclusions

Do not write “X% was generated by ChatGPT,” identify a particular model from style alone, or accuse the author of misconduct. Appropriate conclusions are “X–Y% of the reviewed prose exhibits AI-like traits” and “the document shows low/moderate/high evidence of substantial AI assistance.”
