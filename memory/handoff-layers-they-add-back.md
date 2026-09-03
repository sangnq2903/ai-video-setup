---
name: handoff-layers-they-add-back
description: Every timeline handed over gets the same four layers added back by hand - transition, riser+dings, Epidemic music, adjustment clips - so offer them at handoff instead of waiting to be asked
metadata:
  type: feedback
---

Measured 2026-09-02 by diffing `phonetotreamdesk - EN` before and after the user
re-cut it. I delivered video + English VO only, correctly following the opt-in rule.
They then added, by hand, the same set they had on the Vietnamese version:

| Layer | What they placed |
|---|---|
| Transition | `Blur Dissolve`, **22f**, straddling the hook→body cut, exactly where my marker said |
| Riser | `popular-riser-metallic-sound-effect.mp3` on A3, f79-162 — in before the cut, out past the transition |
| Dings | `ding-sound-effect_2.mp3` ×4 on A3 (f296, 541, 754, 992), 89f each, untrimmed |
| Music | `ES_250126_Project 6.mp3` (Epidemic) on A5, spanning the **whole** timeline f0-1212 |
| Grade | 2 `Adjustment Clip`s on V2, split at the same point as the Vietnamese version |

They also widened the hook (C1170 19f→59f, C1171 76f→101f) and rippled everything
after by +65 frames — see [[hook-construction-taste]].

**Why this matters:** the opt-in rule ("no music / text / SFX unless the flag is
typed") is still their rule and still correct — but in practice they add these back
every time, by hand, which is the work the pipeline was meant to save. Silently
shipping a bare timeline is technically right and practically useless.

**How to apply:** keep obeying opt-in — do not add them uninvited. But at handoff,
**name this exact list as the remaining manual work**, with the frames I'd use, and
offer to do it in one line ("say `music sfx` and I'll place them"). Cheaper for them
to type two words than to place a riser by hand. When they do type the flags, the
placements above are the known-good template.

One asymmetry to remember: **music spans the entire timeline including the tail**,
while the VO stops well before the end — there is a ~147-frame video tail after the
last spoken line that the music carries alone.

Related: [[hook-construction-taste]], [[caption-placement-rule]],
[[resolve-frame-conventions]], [[english-vo-config]]
