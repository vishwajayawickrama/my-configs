#!/usr/bin/env python3
"""
verify_deck.py - Automated PDF Slide Deck Quality & OCR Verification

Usage:
  python verify_deck.py --pdf deck.pdf --expected-pages 40
"""

import argparse
import pymupdf
import sys

def verify_deck(pdf_path, expected_pages=None):
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    print(f"=== Verifying PDF: {pdf_path} ===")
    print(f"Total Pages: {total_pages}")
    
    if expected_pages and total_pages != expected_pages:
        print(f"❌ Error: Expected {expected_pages} pages, but got {total_pages}")
        sys.exit(1)
        
    toc = doc.get_toc()
    print(f"Bookmarks count: {len(toc)}")
    for lvl, title, pno in toc[:10]:
        indent = "  " * (lvl - 1)
        print(f"{indent}• [Level {lvl}] Page {pno:02d}: {title}")
    if len(toc) > 10:
        print(f"  ... and {len(toc) - 10} more entries")
        
    empty_pages = []
    for idx, page in enumerate(doc, start=1):
        txt = page.get_text().strip()
        if len(txt) == 0:
            empty_pages.append(idx)
            
    if empty_pages:
        print(f"❌ Error: Pages without searchable OCR text: {empty_pages}")
        sys.exit(1)
        
    print(f"✓ All {total_pages} pages contain active OCR text layers!")
    print(">>> VERIFICATION PASSED 100% <<<")
    doc.close()

def main():
    parser = argparse.ArgumentParser(description="Verify PDF slide deck quality")
    parser.add_argument("--pdf", required=True, help="Path to PDF")
    parser.add_argument("--expected-pages", type=int, default=None, help="Expected page count")
    args = parser.parse_args()
    
    verify_deck(args.pdf, args.expected_pages)

if __name__ == "__main__":
    main()
