---
name: timeline-and-render-defaults
description: The user's fixed spec — cut at Full HD 30fps, pre-configure a 4K/20000 render job, never press render
metadata:
  type: project
---

Stated 2026-09-02, applies to every video job.

**Timeline: Full HD, 30 fps.** Set through `project_settings` **at project creation,
before importing anything** — changing frame rate once clips are on the timeline
throws every cut and marker out of sync with the VO, and there is no repair short
of rebuilding.

- Vertical (TikTok/Reels): `timelineResolutionWidth` 1080, `timelineResolutionHeight` 1920
- Horizontal (YouTube): 1920 × 1080
- `timelineFrameRate` and `timelinePlaybackFrameRate` both 30

**Render: 4K at VideoQuality 20000** — `render safe_set_render_settings` (dry-run
first) then `prepare_render_job`.

- Vertical: `FormatWidth` 2160, `FormatHeight` 3840
- Horizontal: 3840 × 2160
- `FrameRate` 30, `VideoQuality` 20000

**Why the 1080 → 4K mismatch is deliberate:** platforms hand a 4K upload a higher
bitrate, so the clip survives their re-encode without falling apart. Resolve
upscales at render; the timeline stays 1080.

**How to apply:** `prepare_render_job` only queues the job. **Never start the
render** — this does not loosen [[editing-deliverable-preferences]]. The user
grades against a still they pick themselves and presses render on their own.

Related: [[editing-deliverable-preferences]], [[vietnamese-voice-to-instagram-pipeline]]

## DROPPED 2026-09-02: do not touch Deliver at all

The user removed the render step. **Set no render settings and queue no render job.**
The timeline settings above (Full HD, 30 fps, set before importing) still stand — the
change is only that nothing on the Deliver side is configured any more.

Their own export spec, kept here for reference only, never applied automatically:
4K (vertical 2160×3840, horizontal 3840×2160) at `VideoQuality` 20000.

