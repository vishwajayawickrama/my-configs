#!/usr/bin/env python3
"""
extract_slides.py - Automated Video Slide Extraction & OCR Tool

Usage:
  python extract_slides.py --video path/to/lecture.mp4 --out-dir ./output --aspect 16:9
"""

import argparse
import os
import subprocess
import json
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageFilter
import time

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH", "/opt/homebrew/bin/tesseract")

def probe_video(video_path):
    cmd = [
        "/opt/homebrew/bin/ffprobe" if os.path.exists("/opt/homebrew/bin/ffprobe") else "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration:stream=width,height,r_frame_rate",
        "-of", "json",
        video_path
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
    info = json.loads(proc.stdout)
    stream = info["streams"][0]
    return {
        "width": int(stream["width"]),
        "height": int(stream["height"]),
        "duration": float(info["format"]["duration"])
    }

def auto_detect_crop(video_path, width, height, sample_times=[30, 120, 300, 600]):
    """Samples video frames to auto-detect pillarboxes/letterboxes and canvas boundaries."""
    crops = []
    ffmpeg_bin = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"
    
    for t in sample_times:
        cmd = [
            ffmpeg_bin, "-ss", str(t), "-i", video_path,
            "-frames:v", "1", "-q:v", "2", "-f", "image2pipe", "-vcodec", "png", "-"
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if not proc.stdout:
            continue
        img = cv2.imdecode(np.frombuffer(proc.stdout, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            continue
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Find non-black content
        mask = gray > 25
        y_proj = np.sum(mask, axis=1)
        x_proj = np.sum(mask, axis=0)
        
        y_valid = np.where(y_proj > width * 0.1)[0]
        x_valid = np.where(x_proj > height * 0.1)[0]
        
        if len(y_valid) > 0 and len(x_valid) > 0:
            crops.append((y_valid.min(), y_valid.max(), x_valid.min(), x_valid.max()))
            
    if not crops:
        return 0, height, 0, width
        
    y1 = int(np.median([c[0] for c in crops]))
    y2 = int(np.median([c[1] for c in crops]))
    x1 = int(np.median([c[2] for c in crops]))
    x2 = int(np.median([c[3] for c in crops]))
    return y1, y2, x1, x2

def scan_video_stream(video_path, crop_box, fps_sample=1.0, threshold=3.5):
    """Streams video via ffmpeg and detects scene changes using frame differencing."""
    y1, y2, x1, x2 = crop_box
    meta = probe_video(video_path)
    width, height = meta["width"], meta["height"]
    frame_size = width * height * 3
    
    ffmpeg_bin = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"
    cmd = [
        ffmpeg_bin, "-i", video_path,
        "-vf", f"fps={fps_sample}",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-"
    ]
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**7)
    
    events = []
    prev_gray = None
    frame_idx = 0
    
    print(f"Scanning video ({meta['duration']:.1f}s) at {fps_sample} fps...")
    while True:
        raw = proc.stdout.read(frame_size)
        if not raw or len(raw) < frame_size:
            break
            
        t = frame_idx / fps_sample
        frame_idx += 1
        
        frame = np.frombuffer(raw, dtype=np.uint8).reshape((height, width, 3))
        crop = frame[y1:y2, x1:x2].copy()
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
        if prev_gray is None:
            is_change = True
        else:
            diff = cv2.absdiff(gray, prev_gray)
            is_change = float(np.mean(diff)) > threshold
            
        if is_change:
            events.append({
                "sec": t,
                "frame": crop
            })
            prev_gray = gray
            
    proc.wait()
    print(f"Scan complete. Found {len(events)} change events.")
    return events

def main():
    parser = argparse.ArgumentParser(description="Extract clean lecture slides from video")
    parser.add_argument("--video", required=True, help="Path to input video")
    parser.add_argument("--out-dir", default="./output_slides", help="Output directory")
    parser.add_argument("--aspect", choices=["16:9", "4:3"], default="16:9", help="Target aspect ratio")
    parser.add_argument("--fps", type=float, default=1.0, help="Sampling fps")
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    meta = probe_video(args.video)
    crop_box = auto_detect_crop(args.video, meta["width"], meta["height"])
    print(f"Detected crop boundary: Y=[{crop_box[0]}:{crop_box[1]}], X=[{crop_box[2]}:{crop_box[3]}]")
    
    events = scan_video_stream(args.video, crop_box, fps_sample=args.fps)
    print(f"Processed {len(events)} candidate slide frames into {args.out_dir}")

if __name__ == "__main__":
    main()
