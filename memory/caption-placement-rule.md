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
