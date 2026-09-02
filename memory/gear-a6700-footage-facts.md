---
name: gear-a6700-footage-facts
description: What the Gear A6700 footage actually is — silent, portrait-flagged, and where each gear item is covered
metadata:
  type: project
---

The `/Volumes/Data/share/0826/gear6700` footage (14 clips, ~11m20s, iPhone 15
Pro Max HEVC 30p):

- **Every clip is silent** — all peak at or below -30 dB, no speech anywhere.
  The voiceover was recorded separately; the takes live in the `geara6700`
  Resolve project's media pool as `Audio 4_xxx` / `Audio 5_xxx` WAVs.
- **Stored 3840x2160 but rotation-flagged to portrait**, so it displays
  2160x3840. Resolve honours this. Do NOT reframe for a vertical timeline.
- `C011` is a 7m47s locked-off top-down build take, chronological: bare body →
  cage on (~130-220s) → hot-shoe part in hand (~304-309s) → Sigma with hood
  mounted (~333-339s) → finished rig (~450s). It is the spine for any build cut.
- Hero shots per item: `C013` cage, `C015` Ulanzi CA05, `C014` Sigma 18-50,
  `C019`/`C020`/`C021` DJI RX mounted, `C022`/`C023` finished rig, `C012` the
  set-down (the arrival motion is at 8.8-10.8s, not later).

**Why:** re-deriving this costs a full pass of frame extraction and audio
analysis, and `ffprobe`/`ffmpeg` are not installed on this machine.

**How to apply:** with no ffmpeg, probe media by compiling a small Swift
AVFoundation tool (frames via `AVAssetImageGenerator` with
`appliesPreferredTrackTransform`, levels via `AVAssetReader`) — `swiftc` is
available at `/usr/bin/swiftc`. Tile frames into contact sheets rather than
reading them one at a time.

Related: [[ai-edits-my-videos-project]]

## CORRECTION 2026-09-01: ffmpeg IS installed

The earlier "no ffmpeg on this Mac" note is **wrong**. ffmpeg/ffprobe **9.0.1**
are at `/opt/homebrew/bin/`. They are missing only from the *Bash tool's* PATH,
so prefix commands with `export PATH="/opt/homebrew/bin:$PATH"` or call the
absolute path. The MCP server is unaffected — `_ensure_path_includes_standard_tool_dirs()`
in `src/utils/media_analysis.py` already prepends `/opt/homebrew/bin`.

**This build has NO text filters:** `drawtext`, `subtitles` and `ass` are all
absent (built without libass/freetype). Present and usable: `silencedetect`,
`ebur128`, `scale`, `select`. So ffmpeg can analyse and make contact sheets, but
**cannot burn captions** — the Swift AVFoundation tool stays the burn-in fallback.

