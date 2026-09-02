---
name: hook-construction-taste
description: How the user re-cut a hook by hand — subject close-up first, A-B-A flash rhythm, blur transition out, riser SFX, breath after the hook line
metadata:
  type: feedback
---

Learned 2026-09-02 by reading the user's own re-cut of the hook on the English
`tranhtreotuong` Reel. I had built S1 as **one 68-frame wide of the finished wall**.
They rebuilt it entirely:

| Frame | Length | What |
|---|---|---|
| 0-22 | 22f | `C0784` zoom **1.88** — the three printed posters flat on the desk, close, filling frame |
| 22-38 | **16f** | `C0805` — a flash of the finished wall |
| 38-68 | 30f | `C0784` zoom 1.88 — back to the posters |
| 57-79 | 22f | `Blur Dissolve` straddling the f68 hook→body cut |

Plus: a riser SFX (`popular-riser-metallic-sound-effect.mp3`, 2.76s, their own file
from `~/Downloads`, used untrimmed) on a second audio track at f22-105 — starting on
the flash cut and resolving *past* the transition into the body. And the VO was split
at f68 with the remainder pushed to f75, leaving a 7-frame breath after the hook line.

What to copy next time:

- **Open on the subject itself, close and filling frame — not a room wide.** If the
  video is about the art, frame one is the art. The wide belongs to the context beat.
- **Cut the hook fast, A-B-A.** ~22f / ~16f / ~30f. The short middle beat is a *flash*
  of the payoff — half a second, enough to intrigue, not enough to study. One long
  hold is too static for a hook.
- **Leave the hook on a transition, not a hard cut.**
- **Riser under the hook**, entering on the flash and landing past the transition.
- **Give the VO a breath after the hook line** (~7 frames) instead of one continuous block.
- **One clip can carry two framings.** `C0784` is 1.88 in the hook and 3.16 at S5 —
  reframe per purpose, don't reuse a zoom value across a clip's appearances.

**Why:** my version stated the payoff; theirs creates a question. Showing the object
close first and only flashing the finished wall is what makes a viewer stay.

**How to apply:** build the hook this way by default. I cannot place the transition —
re-confirmed 2026-09-02 that Resolve 20.3.3 has no transition API at all
(see [[resolve-2033-effects-limits]]) — so leave the hard cut, drop a marker at that
frame naming the transition I'd use, and say so in the final report.

**Settled 2026-09-02 (they chose this):** music must still come from Epidemic for the
licence, but **SFX prefers Epidemic without requiring it** — if a file already on their
machine fits better, use it and say so in the report. Their SFX live loosely in
`~/Downloads` (whoosh / pop / riser / error), mixed in with ElevenLabs VO renders and
scraped audio, so check a file before trusting its name. They use SFX **untrimmed**.

Related: [[editing-deliverable-preferences]], [[caption-placement-rule]],
[[ai-edits-my-videos-project]]
