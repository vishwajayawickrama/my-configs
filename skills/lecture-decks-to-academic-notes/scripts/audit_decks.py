#!/usr/bin/env python3
"""Extract PDF slide text, flag sparse pages, optionally OCR them, and write a manifest."""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError as exc:
    raise SystemExit("pypdf is required: install it or use the bundled document runtime") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="PDF files or directories")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--threshold", type=int, default=35, help="native-word threshold for review/OCR")
    parser.add_argument("--ocr", action="store_true", help="OCR pages below the threshold")
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--pdftoppm", default="pdftoppm")
    parser.add_argument("--tesseract", default="tesseract")
    return parser.parse_args()


def collect_pdfs(inputs: list[Path]) -> list[Path]:
    found: dict[str, Path] = {}
    for item in inputs:
        if item.is_dir():
            candidates = item.glob("*.pdf")
        elif item.is_file() and item.suffix.lower() == ".pdf":
            candidates = [item]
        else:
            raise SystemExit(f"Not a PDF file or directory: {item}")
        for path in candidates:
            found[str(path.resolve())] = path.resolve()
    if not found:
        raise SystemExit("No PDF files found")
    return [found[key] for key in sorted(found, key=str.casefold)]


def require_program(name: str) -> str:
    resolved = shutil.which(name) if "/" not in name else name
    if not resolved or not Path(resolved).exists():
        raise SystemExit(f"Required program not found: {name}")
    return str(resolved)


def run_ocr(
    pdf: Path,
    page_number: int,
    image_dir: Path,
    dpi: int,
    pdftoppm: str,
    tesseract: str,
) -> str:
    prefix = image_dir / f"page-{page_number:04d}"
    subprocess.run(
        [
            pdftoppm,
            "-f", str(page_number),
            "-l", str(page_number),
            "-singlefile",
            "-png",
            "-r", str(dpi),
            str(pdf),
            str(prefix),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    result = subprocess.run(
        [tesseract, f"{prefix}.png", "stdout", "--psm", "6"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> int:
    args = parse_args()
    pdfs = collect_pdfs(args.inputs)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    pdftoppm = require_program(args.pdftoppm) if args.ocr else ""
    tesseract = require_program(args.tesseract) if args.ocr else ""
    rows: list[dict[str, str | int]] = []

    for deck_index, pdf in enumerate(pdfs, start=1):
        deck_dir = args.output_dir / f"{deck_index:02d}-{pdf.stem}"
        deck_dir.mkdir(parents=True, exist_ok=True)
        image_dir = deck_dir / "ocr-images"
        if args.ocr:
            image_dir.mkdir(exist_ok=True)

        reader = PdfReader(pdf)
        sections: list[str] = []
        for page_number, page in enumerate(reader.pages, start=1):
            native = (page.extract_text(extraction_mode="layout") or "").strip()
            native_words = len(native.split())
            sparse = native_words < args.threshold
            ocr_text = ""
            if args.ocr and sparse:
                try:
                    ocr_text = run_ocr(
                        pdf, page_number, image_dir, args.dpi, pdftoppm, tesseract
                    )
                except subprocess.CalledProcessError as exc:
                    print(f"OCR failed for {pdf.name} page {page_number}: {exc}", file=sys.stderr)

            best_text = ocr_text if len(ocr_text.split()) > native_words else native
            sections.append(
                f"\n===== PAGE {page_number:04d} | native_words={native_words} "
                f"| ocr={'yes' if ocr_text else 'no'} =====\n{best_text}\n"
            )
            rows.append(
                {
                    "deck_order": deck_index,
                    "deck": pdf.name,
                    "page": page_number,
                    "native_words": native_words,
                    "ocr_words": len(ocr_text.split()),
                    "needs_visual_review": "yes" if sparse else "no",
                    "disposition": "review",
                    "note_location": "",
                }
            )

        (deck_dir / "pages.txt").write_text("".join(sections), encoding="utf-8")

    manifest = args.output_dir / "coverage-manifest.tsv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Processed {len(pdfs)} deck(s), {len(rows)} page(s)")
    print(f"Coverage manifest: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
