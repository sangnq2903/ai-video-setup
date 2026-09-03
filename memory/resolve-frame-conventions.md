---
name: resolve-frame-conventions
description: Measured frame-number conventions in the davinci-resolve MCP - exclusive end_frame, relative vs absolute record frames, and why transform zoom values never port between timelines
metadata:
  type: reference
---

Measured 2026-09-02 while rebuilding the phonetotreamdesk cut as an EN timeline. Each
of these failed silently first, with `success: true`.

**`media_pool create_timeline_from_clips` — `end_frame` is EXCLUSIVE.** Passing
`src_in + duration - 1` (what the /video skill's text says) makes every clip one frame
short, and because `record_frame` is still honoured exactly, the result is a **one-frame
gap at every cut**. Pass `end_frame = src_in + duration`. Verify with
`timeline detect_gaps_overlaps`, which reports `gap_count: 0` when it is right.

**`media_pool append_to_timeline` — `recordFrame` is RELATIVE to timeline start.**
`create_timeline_from_clips`'s `record_frame` is relative too. Passing the absolute
108000 put the clip at 216000. Pass 0 for "start of timeline".

**`timeline_frame capture` — `frame` is ABSOLUTE.** Anything below the timeline's
start frame silently clamps to the first frame, so three captures at "10", "220" and
"270" all returned frame 0 and looked like a broken edit. Add the timeline's
`start_frame` (read it from `timeline get_current`).

**Transform zoom does NOT port between projects.** The same clip with the identical
stored transform (`RotationAngle -90, Zoom 0.56`) filled the frame in the user's
timeline and letterboxed in a fresh one — same resolution, same
`timelineInputResMismatchBehavior`. Zoom is relative to whatever conform base that
timeline gave the clip, and that base is not reproducible from settings. **Measure
instead of copying:** capture with `out_path`, get the content bounding box
(`ffmpeg -vf scale=1:H,format=gray` and find the non-black rows/columns), then
`zoom = 1920 / content_height`. Here 0.56 had to become **1.778**.

**Rotation metadata decides whether a clip needs a manual rotate.** In this folder
C1166/C1173 carry `rotation=-90` side data and Resolve uprights them automatically at
zoom 1; C1174 was shot portrait but the camera wrote no flag, so it needs
`RotationAngle -90` by hand. Check with
`ffprobe -show_entries stream_side_data=rotation` before assuming a clip is landscape.

Related: [[english-vo-config]], [[elevenlabs-stt-timestamps]]

**Hit again 2026-09-04 on the tranhtreotuong VN cut — the user caught it, not me.**
I passed `src_in + duration - 1` to `create_timeline_from_clips` and produced a
one-frame gap at all 12 cuts. The rule was already written in this very file and I
did not read it. `detect_gaps_overlaps` reported `gap_count: 27` and named every one.
**Run that check after every assembly**; V1 must read `gap_count: 0`.

**New, measured the same day: `append_to_timeline` fails when the linked audio has
nowhere to go.** Re-placing Video+Audio clips onto V1 while A1 still held the old
audio items failed with `missing timeline item at index 0` — an error that never
mentions audio. Passing **`mediaType: 1`** (video only) succeeded immediately. Also
note a **disabled** audio track does not help; only clearing it or using `mediaType`
does.

