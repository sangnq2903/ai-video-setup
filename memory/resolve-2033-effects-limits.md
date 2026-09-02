---
name: resolve-2033-effects-limits
description: Measured on Studio 20.3.3.10 — what the scripting API cannot do (transitions, transform keyframes, clip-attached Fusion comps, insert_title), plus the nested-timeline text route that DOES work and two silent bugs (exclusive end_frame, audio-less renders)
metadata:
  type: reference
---

Measured live on DaVinci Resolve Studio **20.3.3.10** (2026-08-25), while trying
to add a transition + dynamic zoom to the Gear A6700 cut. All three routes fail:

- **Transitions** — no AddTransition/CreateTransition anywhere in the API.
  Existing transitions can be read and deleted, never created.
  **Re-confirmed 2026-09-02** on 20.3.3.10: `timeline.CreateTransition`,
  `timeline.AddTransition`, `item.AddTransition` and `item.GetTransition` all
  resolve to `None` (`'NoneType' object is not callable`), and `dir()` lists none
  of them. Note `hasattr()` returns True for every one of these — the proxy
  objects answer any attribute — so `hasattr` is NOT a valid probe here; call the
  method or read `dir()`. The documented
  workaround is the advanced Node server's `drp place_transition` (author
  offline, re-import), but that server is **not connected** in this setup.
- **Native Dynamic Zoom** — `GetProperty("DynamicZoom")` returns null. Only
  `DynamicZoomEase` exists (returns 0), which is useless without the feature
  being switchable. `ZoomX`/`ZoomY` exist but are static values.
- **Transform keyframes** — `timeline_item add_keyframe` / `get_keyframes` both
  raise `'NoneType' object is not callable`; the methods are absent on this build.
- **Fusion comps do not render.** A `MediaIn1 -> Transform -> MediaOut1` comp
  with animated Size was built successfully and `get_keyframes` read the
  keyframes back — but the rendered frame was **identical at Size 1.0 and
  Size 2.0**. The comp is accepted and silently ignored.
- `delete_comp` returns false for an item's only comp; remove the tools and
  rewire MediaIn->MediaOut instead.

**Why:** each of these fails *silently* or looks like it worked, so they burn a
lot of calls and can produce a false "done" claim.

**How to apply:** do not promise transitions, dynamic zoom, or any Fusion-based
effect on this build — they are a Resolve UI task. Prove any motion/effect claim
by rendering the SAME frame under two different parameter values; comparing two
different frames of moving footage proves nothing (the subject moves and fakes
the effect). Note that `add_comp` and marker edits auto-archive the timeline —
clean up the `_archived_vNN` timelines afterwards.



**`insert_title` is actively destructive, not merely misplaced.** Re-confirmed
2026-09-01 (v2 cut): it ignores `track_index` completely AND performs a *ripple
insert* on V1 — it splits the clip under the playhead and pushes every later clip
downstream, silently desyncing the whole cut from the VO. It also reports
`success: true`. Two further traps found the same session: with no mark in/out it
appends the title to the END of V1; with marks set, `mark_in`/`mark_out` are
**relative** to timeline start, and passing absolute frames lands the title at
start+offset (e.g. 216002 instead of 108002). There is no `import_subtitles`
action, and `import_into_timeline` rejects .srt (it is for AAF/EDL/XML only).
Do not attempt titles on a finished timeline — rebuild is the only repair.

## The route that does work: burn text/effects after the render

Confirmed 2026-09-01 on the Tranh Treo Tuong TikTok. Resolve 20.3.3 cannot put
text over picture at all (`Insert*IntoTimeline` has no trackIndex, so a title
always lands on V1), so captions were burned into the **rendered** mp4 with a
small Swift AVFoundation tool: `AVMutableVideoComposition` +
`AVVideoCompositionCoreAnimationTool`, one `CALayer` per caption with
`CAKeyframeAnimation` for pop-in/fade-out, plus `AVMutableAudioMix` for a gain
boost. Renders in ~40s for a 34s 1080x1920 clip.

**Trap inside the trap:** a `CATextLayer` in that offscreen compositor draws its
background but **no glyphs** — the caption boxes come out empty. Pre-render each
caption to a `CGImage` with CoreText (`CTFramesetterCreateFrame` + `CTFrameDraw`
into a `CGContext`) and set it as the layer's `contents` instead. Use a concrete
font name (`HelveticaNeue-Bold`); Vietnamese diacritics and per-word colour runs
survive fine.

The tool lives in the session scratchpad, not in the repo — rebuild it from this
description rather than hunting for it.

## CONFIRMED WORKING on 20.3.3: the nested-timeline route for text

Tested 2026-09-02 on the Tranh Treo Tuong Reels and **proved with rendered
frames** — this supersedes the "burn text after render" section above as the
preferred route. Text is now a real, editable clip on V2 inside Resolve.

Recipe, per caption:

1. `media_pool create_timeline` a sub-timeline (e.g. `TXT_S1`).
2. `timeline insert_fusion_title {name: "Text+"}` — it lands on V1 *there*,
   which does not matter.
3. Set everything while the handle is live, via `fusion_comp` on
   `timeline_item {track_type:"video", track_index:1, item_index:0}`,
   `tool_name:"Template"`:
   - `set_text_plus` -> `StyledText`
   - `set_input Size = 0.10`
   - `set_input Center = [0.5, 0.16]` (lower third)
4. Switch to the real timeline, `add_track` video, then
   `media_pool append_to_timeline` with the SUB-TIMELINE's **media pool item id**
   (from `project_settings project_summary`, NOT the id `create_timeline` returns —
   they differ) and `clipInfo {track_index: 2, record_frame, start_frame, end_frame}`.

V1 is untouched — no ripple. Vietnamese diacritics render correctly.

**Hard limits found:**
- A sub-timeline made this way is **150 frames** long. A caption needing more
  must be split into two (splitting on the sentence's own comma is usually
  better editorially anyway).
- At `Size 0.10`, a caption longer than **~23 characters** overflows the 1080-wide
  vertical frame. `Size 0.13` overflowed at 26 chars; 0.075 fits but reads small
  on a phone.

## `clipInfo.end_frame` is EXCLUSIVE — the silent 1-frame-hole bug

Cost a full rebuild on 2026-09-02. Computing `end = start + n - 1` (inclusive
style) yields n-1 frames per clip while `record_frame` still advances by n,
leaving a **1-frame black hole at every single cut**. Resolve reports success and
the readback's `start`/`end` still look contiguous, so nothing flags it.

Always use `end_frame = start_frame + duration`.

**How to catch it:** sampling a few frames will miss it — 9 sample points caught
1 of 15 holes. Render the timeline and scan every frame:
`ffmpeg -i out.mp4 -vf "signalstats,metadata=print:key=lavfi.signalstats.YAVG"
-fps_mode passthrough -f null -` then flag any frame whose luma is under half of
BOTH neighbours. `blackdetect` does **not** find these (one frame is shorter than
its minimum duration).

## Render jobs silently drop audio

`prepare_render_job` inherits the Deliver page's preset, which is **unreadable**
via the API (`GetRenderSettings` does not exist). If that preset has ExportAudio
off, the render comes out video-only and still reports success. Always pass
`settings: {ExportAudio: true, AudioCodec: "aac", AudioBitDepth: 16,
AudioSampleRate: 48000}` explicitly, and verify with
`ffprobe -show_streams` that an audio stream exists.

Related: [[ai-edits-my-videos-project]], [[vietnamese-voice-to-instagram-pipeline]]

## Animated text: the test the user approved (2026-09-02)

The user wants Apple-keynote-style animated text, each instance a *different*
effect. They chose **test-before-building** over doing it by hand or relaxing the
no-export rule. Note their no-export rule kills the previously-proven burn-in
fallback, so this test decides whether animated text is reachable at all.

Test in a throwaway project, in this order — stop at the first failure:
1. `CreateEmptyTimeline` + `InsertFusionTitleIntoTimeline` on a scratch timeline.
2. Set the Text+ (`set_text_plus`) while the handle is live.
3. Place it via `GetMediaPoolItem()` + `AppendToTimeline` clipInfo trackIndex 2.
4. **Prove motion**: grab two stills at two different frames OF THE SAME title and
   compare them. Readback is not evidence — a comp that accepts every call and
   renders motionless has already happened on this build.

There are **zero `.setting` title templates on disk** (checked the whole app
bundle), so built-in animated Fusion titles cannot be enumerated by filename —
names have to be probed at runtime.

## SETTLED 2026-09-02: ANIMATED TEXT WORKS ON 20.3.3 — proven end to end

Ran the test in a throwaway project (`_mcp_animated_title_probe`, deleted after).
Every step succeeded, and the motion was proven with rendered frames, not readback:

1. `media_pool create_timeline "probe_inner_01"` — the title's own inner timeline.
2. `timeline insert_fusion_title` with name **`"Text+"`** — lands on V1 there.
   Readback: item name `Text+`, `get_comp_count` = 1, tool list =
   `Template` (TextPlus) -> `MediaOut1`.
3. `fusion_comp set_input Template/StyledText` — text set.
4. `fusion_comp add_keyframe Template/Size` at **time 0 = 0.02** and
   **time 24 = 0.2**. Comp time is CLIP-RELATIVE (0 = first frame of the title),
   not absolute timeline frames.
5. **PROOF:** `timeline_frame capture` at 00:00:00:00 -> tiny text;
   at 00:00:01:00 -> large text. Same title, two times, visibly different.
6. `timeline get_media_pool_item` on the inner timeline, then
   `media_pool append_to_timeline` with
   `{media_pool_item_id, start_frame: 0, end_frame: 47, trackIndex: 2,
   recordFrame: 48}` — **`start_frame`/`end_frame` are REQUIRED**, the call errors
   without them. Readback confirmed it landed on V2.
7. **PROOF again on the outer timeline:** capture at 00:00:02:00 -> tiny,
   00:00:03:00 -> large. The nested title renders AND animates from the parent.

So: Fusion **titles** honour keyframes and render on 20.3.3. The old
"Fusion comps do not render" finding is specific to comps attached to
**media clips** — it does not generalise. Animated, editable-in-Resolve text is
reachable, and neither `insert_title` nor post-render burn-in is needed.

`timeline_frame capture` (quality 'frame') is the cheap proof tool — one rendered
frame, `max_width` to keep it small.

## 113 built-in animated title presets — use these, don't hand-keyframe (2026-09-02)

They are NOT loose `.setting` files (that search returns zero and misled an earlier
conclusion). They are packed inside
`/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Resources/Fusion/Templates/Templates.drfx`
— a zip; `unzip -l` lists them.

`timeline insert_fusion_title` accepts these preset names directly (verified live:
`"Rise Fade"` and `"Word Highlight"` both inserted and rendered). Pass the **leaf
name only** — `"Word Highlight"`, not `"Subtitles/Animated/Word Highlight"`.

`Rise Fade` came in as a 9-tool rig with a `StyledTextFollower` (per-character
stagger), BezierSplines and a KeyStretcher — professional motion, no keyframing
needed. Rendered frame at 0:08 showed characters mid-stagger, at 1:12 the full
Vietnamese line with correct diacritics.

**Trap: the TextPlus tool name differs per preset** — `Rise Fade` uses `upperText`,
`Word Highlight` uses `Template`. Always `get_tool_list` before `set_input`;
writing to a wrong tool name still reports success.

Project timebase on the user's current job is **24 fps** (a timecode frame
component above 23 is rejected).

**Title presets animate; `Subtitles/…` presets do not.** Measured 2026-09-02:
`Rise Fade` inserted as a title animates immediately (per-character stagger visible
at 0:08). `Word Highlight` inserted the same way renders a styled line that never
moves — keyframing `MacroTool1/Input31` ("Write On Words") changed nothing across
frames 12, 16, 36 and 40. Its published inputs (`StyledText` labelled *Subtitle*,
"Words per line", highlight fill/outline/background) show it is a **subtitle-track
styling preset**: the motion is driven by subtitle cues, not by a title item. For
karaoke-style captions, build a subtitle track first and style it there.

**Six presets tested live 2026-09-02** (text tool name in brackets — it differs per
preset, always `get_tool_list` first):

- `Rise Fade` [`upperText`] — best default. Per-character rise+fade stagger,
  transparent background, quick entry.
- `Center Reveal` [`mainText`] — masked reveal outward from centre, very clean.
- `Scale Up` [`Text1_1`] — per-character scale-up, but slow (>40 frames at 24fps).
- `Slide From Center Line` [`leftText` + `rightText`] — two-part title split by a
  line; the line defaults to **cyan** and must be recoloured for a dark look.
- `Elegant Shadow` [`Text3D1`] — REJECT for overlay work: opaque white full-frame
  background, a 27-tool 3D rig, and it crops long lines.
- `Word Highlight` [`Template`] — static (subtitle-track preset, see above).

Heuristic: if `get_tool_list` shows a `Background` tool, the preset is a full-frame
title card, not an overlay.

## 2026-09-02: the good text presets were downloaded but NEVER INSTALLED

The user said Resolve's stock title effects look ugly and asked for *Preset Manager*
and *Text Elite*. Neither was visible because both `.drfx` packs were sitting
unextracted in
`~/Library/Application Support/.../Fusion/Templates/` — the earlier "this machine
has no title templates" reading came from checking only `/Library`, never `~/Library`.

Installed them by unzipping each `.drfx` into that `Templates/` root (that is all a
`.drfx` install does). **Resolve picked them up with no restart.** Now available:

- **`Preset Manager` — 53 presets, the one to use by default.** Names follow
  `[Letter|Word|none] + [Slide Up/Down/Left/Right | Scale In/Out | Rotate | Fade |
  Flicker] + [+ Fade | + Blur | + Bounce]`. Text tool is **`Template`** (an
  `Instance_Template` also exists; write to `Template`). Verified live:
  `Word Slide Up + Fade` staggered word by word, transparent background.
- `Text Elite Presets 01`…`20`.
- `AkittPro_Presets` — 257 titles + 32 effects.

The user's own saved presets sit loose at the Titles root: `elite-1`, `Rise`,
`text-effect-*`. **`Rise` contains only MediaIn→MediaOut and no text tool** — do not
use it for text.

**Preset text animations run too slow for this user's speech — always retune.**
Measured 2026-09-02 on `Word Scale In Bounce`. Two knobs, both on the preset's
`Follower1` (StyledTextFollower):

- `Delay` — default `3`, and it is **per CHARACTER, not per word**, even on presets
  named `Word ...`. A 16-character line therefore costs 48 frames of stagger alone.
  Set `1` for short-form.
- The size spline (`WordSizeX`, or `CharacterSizeX` on `Letter ...` presets) ramps
  0→1 over **20 frames** by default. `delete_keyframe(time=20)` +
  `add_keyframe(time=8, value=1)` halves it. `WordSizeY` carried only one key and
  followed X automatically.

Total ≈ (character count × Delay) + ramp. To land the animation exactly as the
sentence ends: `Delay = (spoken frames − ramp) / character count`, min 1, using
`speech_to_text` timestamps rather than a guess.

"Thử cho góc của bạn": frame 48 before, **frame 22 after** — stagger and bounce
both preserved.

