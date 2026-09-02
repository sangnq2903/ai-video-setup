---
name: dark-cinematic-cdl-look
description: The dark/cinematic CDL the user asked for on the Gear A6700 cut — exact values and why they work on this flat phone footage
metadata:
  type: feedback
---

Asked on 2026-08-25 for "tông màu tối, cinematic". What landed, applied as an
ASC CDL on node 1 of every clip:

    Slope       1.03  1.00  0.96
    Offset     -0.028 -0.022 -0.010
    Power       1.22  1.22  1.22
    Saturation  0.90

**Why:** iPhone HEVC arrives flat with milky, lifted blacks and near-clipping
practical highlights (monitors, lamps). Negative offset drops the blacks where
the milkiness lives; power >1 darkens the mids for the "tối" read; slope kept at
~1 means highlights barely move, so blown monitors do not clip further. Slope
R up / B down with the opposite bias on offset gives cool shadows and warm
highlights — teal-orange separation without a split-tone tool.

**How to apply:** a first pass at Power 1.15 / Sat 0.92 read as too timid on the
hero shots; the values above were the second, accepted pass. Test on both a
highlight-critical shot and a dark hero before committing to all clips — the
timid version looked fine on the easy shot and flat on the hero.

Do not put colour preferences in the repo's `house-style` skill; that file is
committed and travels with the project.

Related: [[ai-edits-my-videos-project]], [[gear-a6700-footage-facts]]
