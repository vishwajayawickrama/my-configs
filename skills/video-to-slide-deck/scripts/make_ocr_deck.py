#!/usr/bin/env python3
"""
make_ocr_deck.py - High-Resolution OCR PDF Slide Deck Generator & Bookmarker

Usage:
  python make_ocr_deck.py --images-dir ./enhanced_frames --output deck.pdf --title "Lecture Title" --author "Instructor"
"""

import argparse
import os
import glob
import pytesseract
import pymupdf
from PIL import Image, ImageFilter

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH", "/opt/homebrew/bin/tesseract")

def generate_ocr_pages(image_files, temp_pdf_dir):
    os.makedirs(temp_pdf_dir, exist_ok=True)
    pdf_paths = []
    
    print(f"Generating OCR searchable pages for {len(image_files)} slides...")
    for idx, img_path in enumerate(image_files, start=1):
        out_pdf = os.path.join(temp_pdf_dir, f"page_{idx:03d}.pdf")
        pdf_bytes = pytesseract.image_to_pdf_or_hocr(img_path, extension='pdf')
        with open(out_pdf, 'wb') as f:
            f.write(pdf_bytes)
        pdf_paths.append(out_pdf)
        print(f"  [{idx:02d}/{len(image_files):02d}] OCR generated for {os.path.basename(img_path)}")
        
    return pdf_paths

def assemble_pdf(page_pdf_paths, output_path, toc_entries=None, metadata=None):
    doc = pymupdf.open()
    for p in page_pdf_paths:
        page_doc = pymupdf.open(p)
        doc.insert_pdf(page_doc)
        page_doc.close()
        
    if toc_entries:
        doc.set_toc(toc_entries)
        
    if metadata:
        doc.set_metadata(metadata)
        
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\nPDF successfully assembled: {output_path} ({len(page_pdf_paths)} pages, {file_size_mb:.2f} MB)")

def main():
    parser = argparse.ArgumentParser(description="Assemble OCR PDF slide deck from images")
    parser.add_argument("--images-dir", required=True, help="Directory containing sorted slide images")
    parser.add_argument("--output", required=True, help="Path to output PDF")
    parser.add_argument("--title", default="Lecture Slide Deck", help="Document title")
    parser.add_argument("--author", default="Presenter", help="Author name")
    parser.add_argument("--subject", default="Lecture Notes", help="Subject")
    args = parser.parse_args()
    
    image_files = sorted(glob.glob(os.path.join(args.images_dir, "*.png")) + glob.glob(os.path.join(args.images_dir, "*.jpg")))
    if not image_files:
        print(f"No images found in {args.images_dir}")
        return
        
    temp_dir = os.path.join(args.images_dir, "_temp_ocr_pages")
    page_pdfs = generate_ocr_pages(image_files, temp_dir)
    
    metadata = {
        "title": args.title,
        "author": args.author,
        "subject": args.subject,
        "creator": "Google Antigravity High-Resolution OCR Pipeline"
    }
    
    assemble_pdf(page_pdfs, args.output, metadata=metadata)

if __name__ == "__main__":
    main()
