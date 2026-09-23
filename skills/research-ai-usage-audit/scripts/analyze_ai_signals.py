#!/usr/bin/env python3
"""Extract a research paper and report reproducible AI-writing signal counts.

The output is descriptive. It is not an AI detector and produces no authorship score.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


AI_VOCAB = [
    "additionally", "align with", "boasts", "bolstered", "crucial", "deep dive",
    "delve", "emphasizing", "enduring", "enhance", "fostering", "garner",
    "highlight", "interplay", "intricate", "key", "landscape", "meticulous",
    "pivotal", "robust", "showcase", "tapestry", "testament", "underscore",
    "valuable", "vibrant",
]

TRANSITIONS = [
    "therefore", "however", "nevertheless", "consequently", "thus", "whereas",
    "while", "rather than", "yet", "in contrast", "taken together",
]

OBJECTIVE_PATTERNS = {
    "chatbot_language": r"(?i)\b(?:i hope this helps|would you like me to|let me know if|here(?:'s| is) a (?:breakdown|template)|of course!|certainly!)\b",
    "placeholder_text": r"(?i)(?:\[(?:insert|enter|add)[^\]]*\]|\b(?:insert|paste)_[a-z0-9_]+|20\d\d-xx-xx|\bplaceholder\b)",
    "leaked_citation_markup": r"(?i)\b(?:turn\d+(?:search|view|fetch)\d+|oaicite|oai_citation|contentReference|attributableIndex|grok_card|attached_file)\b|\[cite:\s*\d+\]",
    "prompt_refusal_or_cutoff": r"(?i)\b(?:as an ai(?: language model)?|i (?:cannot|can't) (?:comply|assist)|my knowledge cutoff)\b",
}


def extract_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ET.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    blocks = []
    for para in root.findall(".//w:body/w:p", ns):
        text = "".join(node.text or "" for node in para.findall(".//w:t", ns)).strip()
        if text:
            blocks.append(text)
    for table in root.findall(".//w:body/w:tbl", ns):
        for row in table.findall(".//w:tr", ns):
            cells = []
            for cell in row.findall("./w:tc", ns):
                value = " ".join(node.text or "" for node in cell.findall(".//w:t", ns)).strip()
                cells.append(value)
            if any(cells):
                blocks.append(" | ".join(cells))
    return "\n\n".join(blocks)


def extract_pdf(path: Path) -> str:
    with tempfile.TemporaryDirectory(prefix="ai-writing-audit-") as temp_dir:
        output = Path(temp_dir) / "paper.txt"
        try:
            result = subprocess.run(
                ["pdftotext", "-layout", str(path), str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise RuntimeError(
                    "PDF extraction needs pdftotext or pypdf; use the Codex bundled "
                    "workspace Python when the system Python lacks pypdf"
                ) from exc
            reader = PdfReader(str(path))
            pages = []
            for page_number, page in enumerate(reader.pages, 1):
                pages.append(f"\n\fPAGE {page_number}\n{page.extract_text() or ''}")
            return "".join(pages)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "pdftotext failed")
        return output.read_text(errors="replace")


def extract(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown", ".txt"}:
        return path.read_text(errors="replace")
    if suffix == ".docx":
        return extract_docx(path)
    if suffix == ".pdf":
        return extract_pdf(path)
    raise ValueError(f"unsupported format: {suffix or '(none)'}")


def body_without_references(text: str) -> tuple[str, bool]:
    match = re.search(r"(?im)^\s*(?:#{1,6}\s*)?(?:references|bibliography|works cited)\s*$", text)
    if not match:
        return text, False
    return text[: match.start()], True


def prose_only(text: str) -> str:
    text = re.sub(r"(?ms)^```.*?^```\s*$", " ", text)
    kept = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            kept.append("")
            continue
        if stripped.startswith("|") or stripped.startswith("!["):
            continue
        if re.match(r"^#{1,6}\s+", stripped):
            continue
        kept.append(line)
    return "\n".join(kept)


def phrase_count(text: str, phrase: str) -> int:
    escaped = re.escape(phrase)
    if phrase.endswith("e") and " " not in phrase:
        stem = re.escape(phrase[:-1])
        pattern = rf"(?i)\b(?:{escaped}(?:s|d|ly)?|{stem}ing)\b"
    else:
        pattern = rf"(?i)\b{escaped}(?:s|ed|ing|ly)?\b"
    return len(re.findall(pattern, text))


def section_profiles(text: str) -> list[dict[str, object]]:
    heading = re.compile(
        r"(?m)^(?:#{1,6}\s+.+|(?:[IVXLC]+\.|\d+(?:\.\d+)*)\s+[A-Z][^\n]{2,100})\s*$"
    )
    matches = list(heading.finditer(text))
    if not matches:
        return []
    profiles = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        title = re.sub(r"^#{1,6}\s+", "", match.group(0)).strip()
        chunk = prose_only(text[match.end() : end])
        words = re.findall(r"[A-Za-z][A-Za-z'-]*", chunk)
        if not words:
            continue
        vocab_count = sum(phrase_count(chunk, phrase) for phrase in AI_VOCAB)
        transition_count = sum(phrase_count(chunk, phrase) for phrase in TRANSITIONS)
        negative_count = sum(
            (
                len(re.findall(r"(?i)\bnot (?:only|just|simply|merely)\b", chunk)),
                len(re.findall(r"(?i)\bnot\b[^.!?]{0,140}\bbut\b", chunk)),
                len(re.findall(r"(?i)\brather than\b", chunk)),
                len(re.findall(r"(?i)\b(?:not|does not|is not) (?:itself|by itself)\b|\bby itself\b", chunk)),
            )
        )
        profiles.append(
            {
                "section": title,
                "prose_words": len(words),
                "ai_vocabulary": vocab_count,
                "transitions": transition_count,
                "negative_parallelisms": negative_count,
            }
        )
    return profiles


def repeated_ngrams(words: list[str], n: int, minimum: int = 3) -> list[dict[str, object]]:
    stop = {"of", "the", "and", "to", "in", "a", "an", "for", "with", "is", "are"}
    counts = Counter(tuple(words[i : i + n]) for i in range(len(words) - n + 1))
    rows = []
    for gram, count in counts.most_common():
        if count < minimum:
            break
        if sum(token in stop for token in gram) >= n - 1:
            continue
        rows.append({"phrase": " ".join(gram), "count": count})
        if len(rows) == 20:
            break
    return rows


def analyze(text: str, source: Path) -> dict[str, object]:
    body, references_removed = body_without_references(text)
    prose = prose_only(body)
    tokens = re.findall(r"[A-Za-z][A-Za-z'-]*", prose)
    lower_words = [word.lower() for word in tokens]
    word_count = len(tokens)
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])(?:[\"”’])?\s+", re.sub(r"\s+", " ", prose))
        if len(sentence.split()) >= 3
    ]
    paragraphs = [
        re.sub(r"\s+", " ", paragraph.strip())
        for paragraph in re.split(r"\n\s*\n", prose)
        if len(paragraph.split()) >= 8
    ]
    vocab = {phrase: phrase_count(prose, phrase) for phrase in AI_VOCAB}
    vocab = {phrase: count for phrase, count in vocab.items() if count}
    transitions = {phrase: phrase_count(prose, phrase) for phrase in TRANSITIONS}
    transitions = {phrase: count for phrase, count in transitions.items() if count}
    objective = {
        name: len(re.findall(pattern, prose)) for name, pattern in OBJECTIVE_PATTERNS.items()
    }
    negative = {
        "not_only_or_just": len(re.findall(r"(?i)\bnot (?:only|just|simply|merely)\b", prose)),
        "not_x_but_y": len(re.findall(r"(?i)\bnot\b[^.!?]{0,140}\bbut\b", prose)),
        "rather_than": len(re.findall(r"(?i)\brather than\b", prose)),
        "not_by_itself": len(re.findall(r"(?i)\b(?:not|does not|is not) (?:itself|by itself)\b|\bby itself\b", prose)),
    }
    enumeration_sentences = [
        sentence for sentence in sentences
        if sentence.count(",") >= 3 and re.search(r"\b(?:and|or)\b", sentence, re.I)
    ]
    sentence_lengths = [len(re.findall(r"[A-Za-z][A-Za-z'-]*", sentence)) for sentence in sentences]
    paragraph_lengths = [len(re.findall(r"[A-Za-z][A-Za-z'-]*", paragraph)) for paragraph in paragraphs]

    def summary(values: list[int]) -> dict[str, float | int]:
        if not values:
            return {"count": 0, "mean": 0, "min": 0, "max": 0}
        return {
            "count": len(values),
            "mean": round(sum(values) / len(values), 2),
            "min": min(values),
            "max": max(values),
        }

    per_1000 = lambda count: round(count * 1000 / word_count, 2) if word_count else 0
    return {
        "source": str(source.resolve()),
        "format": source.suffix.lower(),
        "references_removed": references_removed,
        "counts": {
            "prose_words": word_count,
            "sentences": len(sentences),
            "paragraphs": len(paragraphs),
            "em_dashes": prose.count("—"),
            "spaced_em_dashes": prose.count(" — "),
            "curly_quotes_or_apostrophes": len(re.findall(r"[“”‘’]", prose)),
            "enumeration_sentences": len(enumeration_sentences),
        },
        "normalized_per_1000_words": {
            "ai_vocabulary": per_1000(sum(vocab.values())),
            "transitions": per_1000(sum(transitions.values())),
            "negative_parallelisms": per_1000(sum(negative.values())),
            "enumeration_sentences": per_1000(len(enumeration_sentences)),
        },
        "ai_vocabulary": vocab,
        "transitions": transitions,
        "negative_parallelisms": negative,
        "objective_artifacts": objective,
        "sentence_length_words": summary(sentence_lengths),
        "paragraph_length_words": summary(paragraph_lengths),
        "repeated_3grams": repeated_ngrams(lower_words, 3),
        "repeated_4grams": repeated_ngrams(lower_words, 4),
        "section_profiles": section_profiles(body),
        "enumeration_examples": enumeration_sentences[:20],
        "warning": "Descriptive signal inventory only; not an AI-authorship detector.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper", type=Path, help="Markdown, text, DOCX, or PDF paper")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()
    if not args.paper.is_file():
        parser.error(f"file not found: {args.paper}")
    try:
        report = analyze(extract(args.paper), args.paper)
    except (OSError, RuntimeError, ValueError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
