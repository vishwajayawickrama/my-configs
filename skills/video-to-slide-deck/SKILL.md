---
name: video-to-slide-deck
description: Extract pristine, high-resolution, OCR-searchable PDF slide decks from lecture and presentation video recordings (MP4, MKV, MOV, AVI, etc.). Use when the user asks to extract slides from a video recording, convert a lecture recording into a PDF slide deck, deduplicate presentation slides, restore missing title slides from images, clean UI overlays (Zoom/Teams/PowerPoint), or generate OCR-searchable lecture notes.
---

# Video to Slide Deck Pipeline

Transform lecture and presentation video recordings into high-resolution, OCR-searchable PDF slide decks with full-text searchability, canvas cropping, UI overlay removal, deduplication, and hierarchical Table of Contents bookmarks.

---

## Workflow Overview

```
Video Recording (.mp4, .mkv, .mov)
  │
  ├─► [Phase 0] Reconnaissance & Canvas Detection (ffprobe, sample inspection)
  │
  ├─► [Phase 1] Streaming Video Scan & Change Detection (ffmpeg pipe @ 1 fps)
  │
  ├─► [Phase 2] Slide Deduplication & Final Build State Selection
  │
  ├─► [Phase 3] Frame Cleaning & Missing Slides Integration (UI mask, centering)
  │
  ├─► [Phase 4] 2K Upscaling & Typography Enhancement (Lanczos, Unsharp Mask)
  │
  ├─► [Phase 5] Tesseract OCR Searchable Text Layer Generation
  │
  ├─► [Phase 6] Assembly, Hierarchical TOC Bookmarking & Metadata Injection
  │
  └─► [Phase 7] Automated QA Verification & Delivery
```

---

## Phase 0 — Video Reconnaissance & Canvas Detection

Before extracting frames, determine video properties and layout geometry:

1. **Probe Video Container**:
   ```sh
   ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of json "input_video.mp4"
   ```

2. **Sample Representative Timestamps**:
   Extract 5–10 frames across the video ($t = 10\text{s}, 100\text{s}, 500\text{s}, 1000\text{s}, 3000\text{s}$) to inspect layout:
   - **Aspect Ratio**: 16:9 Widescreen ($1.777$) vs. 4:3 Standard ($1.333$).
   - **Pillarboxes / Letterboxes**: Identify black or dark borders on left/right or top/bottom.
   - **Presenters / Webcams**: Note if speaker video feeds overlay corners or sidebars.

3. **Compute Exact Canvas Crop**:
   - Determine bounding box `[crop_y1:crop_y2, crop_x1:crop_x2]` enclosing purely the slide white/colored canvas.
   - Verify crop coordinates eliminate black pillarbox borders completely (check $x \pm 2$ pixels to avoid 1-pixel border artifacts).

---

## Phase 1 — Systematic Streaming Scan & Change Detection

Never dump millions of raw video frames to disk. Stream directly via `ffmpeg` stdout into Python:

```python
import subprocess, cv2, numpy as np

width, height = 1920, 1080  # from ffprobe
frame_size = width * height * 3
fps = 1.0  # sample 1 frame per second

cmd = [
    "ffmpeg", "-i", video_path,
    "-vf", f"fps={fps}",
    "-f", "rawvideo", "-pix_fmt", "bgr24", "-"
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**7)
```

- **Scene Change Thresholding**:
  Convert cropped canvas to grayscale and compute mean absolute difference against previous frame:
  $$\Delta = \text{mean}(|\text{gray}_t - \text{gray}_{t-1}|)$$
  Trigger slide event when $\Delta > 3.5$.
- **OCR Quick-Fingerprint**:
  Run lightweight Tesseract PSM 6 or PSM 11 on the title area and bottom corner (slide number) to catalog timestamps and titles.

---

## Phase 2 — Slide Deduplication & Progressive Build Selection

1. **Progressive Bullet Points & Animations**:
   - Lecturers frequently reveal bullet points one by one.
   - Group consecutive frames with matching slide titles or numbers.
   - Select the **last timestamp** with maximum text content before the presenter moves to the next slide (capturing the complete slide).

2. **Multi-Part Lectures & Overlaps**:
   - When merging Part 1 and Part 2 (e.g. multi-session lectures), identify overlapping recap slides at the start of Part 2.
   - Keep exactly one canonical instance to maintain clean numbering and zero redundancy.

3. **Demonstrations, Code Editors & Browser Tabs**:
   - Filter out non-slide screens (IDEs, browser windows, Zoom chat) by checking OCR text density and background uniformity.

---

## Phase 3 — Pristine Frame Selection & UI Cleanup

1. **UI Overlay Removal**:
   - **Zoom / Teams Speaker Badge**: Mask top-right badge area with pure white (`#FFFFFF`) or background color:
     ```python
     crop[0:25, 750:816] = [255, 255, 255]
     ```
   - **PowerPoint / Presenter Controls**: Mask bottom-left pen/navigation icons:
     ```python
     crop[560:612, 0:60] = [255, 255, 255]
     ```

2. **Integrating Missing Slides from Images**:
   - When initial slides (Title slide, Outline) are missing from the video recording:
     1. Crop uploaded images to the exact content boundary.
     2. Clean transient dots or buttons.
     3. Proportionally resize using `scale = min(target_w / w, target_h / h)` and center on the target background canvas to prevent stretching or aspect distortion.

---

## Phase 4 — High-Resolution Upscaling & Typography Enhancement

To produce crisp, high-resolution slides:

1. **Target Dimensions**:
   - **16:9 Widescreen**: $2560 \times 1440$ (2K QHD).
   - **4:3 Standard**: $1920 \times 1440$ (Standard 1440p).

2. **Image Processing Pipeline**:
   ```python
   from PIL import Image, ImageFilter

   # 1. High-quality Lanczos Resampling
   pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
   upscaled = pil_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

   # 2. Unsharp Masking for Typography & Line Art
   enhanced = upscaled.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=3))
   ```

---

## Phase 5 — Tesseract OCR Searchable Text Layer Generation

Generate an invisible, selectable OCR text layer for every page:

```python
import pytesseract

# Generates a 1-page PDF containing the image + aligned text layer
pdf_bytes = pytesseract.image_to_pdf_or_hocr(enhanced_image_path, extension='pdf')
with open(page_pdf_path, 'wb') as f:
    f.write(pdf_bytes)
```

---

## Phase 6 — Assembly, Table of Contents & Metadata Injection

1. **Merge Single Pages**:
   ```python
   import pymupdf

   doc = pymupdf.open()
   for page_path in page_pdf_paths:
       page_doc = pymupdf.open(page_path)
       doc.insert_pdf(page_doc)
       page_doc.close()
   ```

2. **Hierarchical Bookmarks (TOC)**:
   Structure bookmarks with Level 1 for Part/Module sections and Level 2 for individual slides:
   ```python
   toc = [
       [1, "Part 1: Foundations & Core Concepts", 1],
       [2, "Slide 01: Title Slide", 1],
       [2, "Slide 02: Learning Objectives", 2],
       ...,
       [1, "Part 2: Advanced Methodologies & Case Studies", 20],
       [2, "Slide 20: Taxonomy Overview", 20]
   ]
   doc.set_toc(toc)
   ```

3. **Document Metadata**:
   ```python
   doc.set_metadata({
       "title": "Course Code - Lecture Title",
       "author": "Instructor Name",
       "subject": "Complete Searchable Lecture Slide Deck",
       "keywords": "Keywords, Topics, Methodology",
       "creator": "Google Antigravity High-Resolution OCR Pipeline"
   })
   doc.save(output_pdf_path, garbage=4, deflate=True)
   ```

---

## Phase 7 — Automated QA Verification

Always run automated checks before delivering:

1. **Page Count Integrity**: Assert total pages equal expected unique canonical slides.
2. **Text Layer Completeness**: Verify 100% of pages contain non-empty extracted text (`page.get_text().strip()`).
3. **Milestone Keyword Search**: Assert key topic terms are searchable on landmark pages.
4. **Bookmark Validation**: Verify TOC entries link to valid pages without orphan pointers.
5. **Dual Destination Delivery**:
   - Save to user's `~/Downloads/` folder.
   - Save directly to course / academic project directory.
   - Provide clickable `file://` markdown links.

---

## Reusable Scripts in `scripts/`

- [`scripts/extract_slides.py`](./scripts/extract_slides.py): End-to-end automated scanning, filtering, and single-page OCR extraction.
- [`scripts/make_ocr_deck.py`](./scripts/make_ocr_deck.py): Assembles single-page PDFs with hierarchical bookmarks and metadata.
- [`scripts/verify_deck.py`](./scripts/verify_deck.py): Full test suite asserting page counts, OCR text, and bookmarks.
