---
name: broll-gap-mode
description: The user's third shooting mode — one long talking take where the job is to mark B-roll spots and blank the picture while keeping the audio
metadata:
  type: project
---

Added 2026-09-02. Besides the multi-clip assembly and the dead-air tightening
routes, the user shoots a **single long talking take** and wants a different job
done on it: decide which stretches should be covered by B-roll, then **remove the
picture there while the audio runs unbroken**. They insert the B-roll themselves.

**Their standard lengths: TikTok 30–45 seconds, YouTube 4–10 minutes.** Don't ask.

**Why:** the deliverable is not a finished cut — it is a shot list with holes cut
in the right places, so they know exactly what to go and film.

**How to apply:** lay the audio down whole on A1 (`clipInfo` `mediaType: 2`, full
range, never trimmed), then place only the keeper stretches on V1 as separate
`mediaType: 1` clips at matching `recordFrame`s. The gaps between them are the
B-roll holes. Marker each gap `BROLL 01`, `BROLL 02`… with the shot to film in the
note, taken from what is actually being said at that second. Never ripple-delete
here — ripple slides the audio out of sync with the picture.

Reachable as the `broll` option in both video skills. **The mediaType split is
untested as of 2026-09-02** — prove one gap first (frame in the gap reads empty,
audio continuous across it) before building the whole piece.

Related: [[vietnamese-voice-to-instagram-pipeline]], [[editing-deliverable-preferences]]

## SIMPLIFIED 2026-09-02: mark only, never cut

The user dropped the picture-removal half. The recording now stays **whole and
uncut** on the timeline; the entire job is **marking** where B-roll should go.

One marker per span, using the marker's **`duration`** field so it draws as a bar
covering the whole insert — start and end in a single object, no paired in/out
markers. `name` = `BROLL 01`, `BROLL 02`…, `note` = the shot to film, `color`
distinct from the chapter markers.

This also retires the untested `mediaType` audio/video split — nothing about this
mode is unproven any more, markers with durations are ordinary API.

