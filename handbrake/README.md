# HandBrake lecture presets

Import `Lectures.json` in HandBrake using **Presets → Import…**. The presets
appear under **My Presets → Lectures**. Select one before adding a new encode
to the queue; importing presets does not update jobs already queued.

| Preset | Encoder | RF | Speed preset |
|--------|---------|----|--------------|
| Lecture - Balanced (x265) | H.265 10-bit (x265) | 26 | medium |
| Lecture - Small (x265) | H.265 10-bit (x265) | 30 | medium |
| Lecture - Sharp Text (x265) | H.265 10-bit (x265) | 23 | slow |
| Lecture - Compatible (x264) | H.264 (x264), high profile | 23 | slow |

All four use MP4, a 15 FPS peak frame rate, a 1920×1080 size limit with
aspect ratio preserved and no upscaling, and the first audio track encoded
as **AAC 64 kbps mono** with automatic sample rate. Subtitle selection is disabled.

## Updating

Keep the portable preset JSON in this directory and import it again after
pulling changes. HandBrake imports this file rather than reading it through
a symlink. Importing a matching category can create a duplicate; verify the
updated presets before removing the older category. Export the older presets
first if you need a backup.
