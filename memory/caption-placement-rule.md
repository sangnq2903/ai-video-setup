---
name: caption-placement-rule
description: With `text` on, captions go only on product/spec/emphasis beats — never wall-to-wall
metadata:
  type: feedback
---

Stated 2026-09-02: *"text chỉ cần hiển thị khi nhắc đến sản phẩm, thông số, hay các
điểm nhấn nhá thôi."*

The `text` flag decides **whether** there are captions, not **where**. Caption a
section only when its line does one of three things:

- names a **product or tool** — `Nano double-sided tape`, `Made with ChatGPT`
- states a **spec, method, or number** — `Fixed wall mount`, `CRI 97 · 1200 lumens`
- is an **emphasis beat** — hook, CTA, closing line — `Try it yourself`

Narration, context, and feeling lines get nothing. Rough density: 3-5 captions in a
25-30s Reel; about one per 45-60s in long-form.

Wording follows from this: a caption **names the thing** (`Nano double-sided tape`),
it does not summarise the section (`Small: nano tape`).

**Why:** on the English `tranhtreotuong` cut I captioned all 9 sections and the user
cut it to 4. Wall-to-wall text reads as noise — the viewer ends up reading the words
they are already hearing, so nothing stands out as emphasis.

**How to apply:** pick the beats before building any title timeline, and say in the
final report how many captions were kept, how many dropped, and which sections — so
it reads as a choice, not as missing work.

Written into `commands/video.md` and `skills/youtube-long/SKILL.md` (section
"Đặt chữ Ở ĐÂU") in the `ai-video-setup` repo, so the rule survives without me.

Related: [[editing-deliverable-preferences]], [[vietnamese-voice-to-instagram-pipeline]]

## Anchor to the spoken WORD, not the segment (2026-09-04)

The user re-placed 2 of my 4 captions by hand on the tranhtreotuong VN cut. I had
anchored each to `segment start + 10 frames`. That breaks whenever a segment carries
**two** keyword phrases: the "large ones use a wall mount, small ones use Nano tape"
segment runs 168 frames with keywords at frame 509 and 556, and my second caption
landed at 596 — **40 frames (1.3s) AFTER the words had already been said**.

Correct method: pull the keyword's own frame from the REST STT `words[]`, then place
the caption **8-30 frames EARLIER**, so the text finishes animating as the word
arrives. Measured, as the user accepted them:

| Caption | keyword frame | placed | lead |
|---|---|---|---|
| Tao hinh bang ChatGPT | 281 | 271 | 10f |
| Gia treo co dinh | 509 | 478 | 31f |
| Bang keo Nano 2 mat | 556 | 548 | 8f |
| Thu cho goc cua ban | 731 | 726 | 5f |

**Never place a caption after its keyword.** Early reads as natural — the viewer reads,
then hears it. Late reads as a mistake.

**Self-check before reporting done:** `caption_frame - keyword_frame` must be negative
for every caption.

## CORRECTED again 2026-09-04: allow for the animation, not just the word

Anchoring the caption's START to the keyword is still late. The text animates in over
roughly **character count x Delay + ramp** — with Delay 1 and the default 20-frame
ramp, a 20-character caption needs **40 frames** before it is fully readable. Placing
it 8 frames early leaves it a third-formed when the word lands.

`place_frame = keyword_frame - (chars x Delay + ramp)`

| Caption | chars | anim | keyword | placed |
|---|---|---|---|---|
| Tao hinh bang ChatGPT | 21 | 41f | 281 | 240 |
| Gia treo co dinh | 16 | 36f | 509 | 473 |
| Bang keo Nano 2 mat | 19 | 39f | 556 | 517 |
| Thu cho goc cua ban | 19 | 27f | 731 | 704 |

The user had already dragged caption 2 to **478** before I computed **473** — the two
agreeing is the confirmation the formula is right.

Hold the caption until the phrase ends plus ~15 frames (`end` of the last word).

**When two keyword phrases sit closer than the animation length** (these were 47
frames apart against 36-39 frames of animation) there is no room for both to play in
full — compress the ramp to 8, or let the earlier caption exit early. Never overlap
two items on one track.

**Self-check:** `placed + anim <= keyword_frame`.

## MEASURE the animation length, do not compute it (2026-09-04)

`chars + ramp` was my estimate and it is **nearly double the truth**. Measured on
`Word Slide Up + Fade`, Delay 1, a 21-character caption placed at frame 240: frame 258
still fading in, frame 265 fully formed -> **~23 frames**, not the 41 I had calculated.

Usable approximation: **anim = chars + 3** at the default ramp. But presets differ.

The right method: place the first caption, **capture two frames to find where the text
has just finished**, and use that measured number for the rest of the cut. One
measurement instead of four guesses — this took four correction rounds from the user
before I stopped estimating.

## Every caption carries a sound effect (2026-09-04)

`text` now implies SFX — no separate `sfx` flag needed for captions. A caption that
appears silently is incomplete, not minimal.

One effect per caption, placed at the frame the caption **starts animating** (not
where it finishes), on its own audio track, used at full file length. Short
`pop`/`whoosh`/`tick` for ordinary captions; something fuller for the CTA or closing
line. **Never the same file twice in one cut** — rotate them the way the text presets
rotate.

Source: Epidemic `SearchSoundEffects` first; the user's own `~/Downloads` library
(`whoosh-*`, `pop_*`, `*-riser-*`) is allowed, but say in the report which was used.

