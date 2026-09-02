---
name: editing-deliverable-preferences
description: Where the user's video work stops (timeline, never a render) and what music taste to search for
metadata:
  type: feedback
---

Stated 2026-09-02, applies to every video job:

**Stop at the timeline. Never render or export.** No render jobs, no mp4, no
Deliver page. The user exports themselves when they are happy with the cut.
Grabbing a still or reading a frame to *verify* the work is fine — that is
inspection, not delivery.

**Why:** the export is their decision point, and a finished file implies the edit
is settled when it is not.

**Music taste: curious + exciting** (*"gây tò mò, hào hứng"*). Search Epidemic
with a curiosity word (curious / mysterious / intriguing / suspense / quirky)
combined with an energy word (energetic / driving / upbeat / euphoric / build up),
`bpm` 110-140, and **always `filter.vocals: false`** — lyrics fight the Vietnamese
VO. Verified-real mood tags: `suspense`, `dark`, `happy`, `hopeful`, `euphoric`.

**How to apply:** don't ask what music they want each time; search this way, send
2-3 `lqmp3Url` previews, let them pick.

Related: [[epidemic-sound-mcp]], [[vietnamese-voice-to-instagram-pipeline]]

**Everything optional is OFF by default (2026-09-02).** No music, no SFX, no
on-screen text unless the user names it: `text`, `music`, `music-auto`, `sfx`.
Markers are the exception and always get placed.

**Why:** adding something unwanted costs them a manual cleanup in Resolve, which is
far more work than typing one more word to ask for it.

**`text` says WHETHER, not WHERE (2026-09-02).** Even with `text` on, captions go
only where the line names a **product or tool**, states a **spec / method / number**,
or is an **emphasis beat** (hook, CTA, closing line). Narration, context, and
feeling lines get nothing — the picture already carries them, and a caption there
just prints the words the viewer is hearing. Consequence for wording: a caption
**names the thing** (`Nano double-sided tape`) instead of summarising the section
(`Small: nano tape`). Roughly 3-5 captions in a 25-30s Reel; about one per 45-60s
in long-form.

**Why:** learned the hard way on the English `tranhtreotuong` cut — I captioned all
9 sections and the user cut it to 4. Wall-to-wall text reads as noise, not emphasis.

**Colour is opt-in too, from 2026-09-02.** No grade is applied unless the user names
a look (`lấy 1.5.1`). The earlier "Sony/1.5.1 is the default" decision was reversed
the same day. So the bare command produces: scene-based cut, real VO, markers — and
nothing else. No render job either; that line was dropped the same day.

