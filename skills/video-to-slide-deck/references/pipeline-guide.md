# Video-to-Slide-Deck Pipeline Reference Guide

This reference documents the key heuristics, aspect ratio mathematics, and cleanup techniques used when transforming video recordings into presentation slide decks.

---

## 1. Canvas Geometry & Aspect Ratio Math

### Aspect Ratios
- **16:9 Widescreen**: Ratio $\approx 1.7778$ (e.g., $1920 \times 1080$, $2560 \times 1440$, $1440 \times 810$).
- **4:3 Standard**: Ratio $\approx 1.3333$ (e.g., $1024 \times 768$, $1440 \times 1080$, $1920 \times 1440$).

### Pillarbox / Letterbox Detection
When a slide deck is presented inside a video recording of different dimensions:
- If presentation is 4:3 inside a 16:9 video: Black pillarbox bars exist on left and right.
  - Video width $W = 1092$, height $H = 614$.
  - Slide width $w = H \times 4/3 \approx 818$.
  - Left bar $x_1 = (W - w)/2 \approx 137$, Right bar $x_2 \approx 955$.
- If presentation is 16:9 inside a 4:3 or windowed stream: Black letterbox bars exist on top and bottom.

### Proportional Centering Algorithm
When embedding external images (handouts, title slides, phone captures) without distortion:
```python
scale = min(target_w / source_w, target_h / source_h)
new_w = int(source_w * scale)
new_h = int(source_h * scale)
offset_x = (target_w - new_w) // 2
offset_y = (target_h - new_h) // 2
```

---

## 2. Common UI Overlays & Masking Coordinates

| Presentation Software / Platform | Overlay Element | Typical Position | Clean Treatment |
| :--- | :--- | :--- | :--- |
| **Zoom Meeting** | "Talking: [Name]" badge | Top-Right (`y: 0–25, x: W-100–W`) | Solid fill with `#FFFFFF` or slide background color |
| **Zoom Meeting** | Participant Floating Video Strip | Top-Right / Right sidebar | Select alternate timestamp or crop slide viewport |
| **PowerPoint (Slide Show)** | Pointer, Pen & Navigation Menu | Bottom-Left (`y: H-60–H, x: 0–60`) | Pure white solid fill |
| **Microsoft Teams** | Speaker Spotlight border / Bar | Bottom bar or Top bar | Tight crop to slide inner bounding box |
| **OBS Studio / Screen Capture** | Status bar / Window title | Top/Bottom edges | Crop out window titlebar & OS taskbars |

---

## 3. Image Enhancement & Typography Sharpening

To prevent blurry text when upscaling lower-resolution video streams ($720p$ or $1080p$) to $2K$ ($1440p$):
1. **Lanczos Resampling**: Computes a sinc filter across an $8 \times 8$ pixel neighborhood, preventing the blur of bilinear filtering and the blockiness of nearest-neighbor.
2. **Unsharp Masking**: High-pass filter enhancement:
   $$\text{Sharpened} = \text{Original} + \text{weight} \times (\text{Original} - \text{Gaussian}(\text{Original}))$$
   - Recommended parameters: `radius=1.2`, `percent=120`, `threshold=3`.
