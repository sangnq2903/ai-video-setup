---
name: english-vo-config
description: The English VO settings that survived listening tests (eleven_v3 "E2"), and the hard rule to get the script approved before any TTS call
metadata:
  type: feedback
---

**Show the English script before calling ElevenLabs (2026-09-02, their rule).**
Print every line verbatim, numbered per segment, audio tags included — no summary,
no paraphrase. Wait for approval, then generate. This checkpoint holds **even under
`auto`**, unlike the transcript and script checkpoints.

**Why:** it is *their* voice saying those words. A bad translation only surfaces on
listening, by which point quota is spent — and since English runs a different length
than Vietnamese, fixing one line forces a full re-cut of the timeline. Thirty seconds
of reading against a whole rebuild.

**Config "E2", chosen after they listened to 13 takes the same day:**

```
model eleven_v3 · stability 0.5 · similarity_boost 0.20 · language_code "en"
[British accent] on every line
```

This **replaces `eleven_turbo_v2`**, which was the settled answer earlier the same
day. turbo_v2 has a clean accent but they rejected it as having **no emotion**. v3
brings two things turbo_v2 lacks: `language_code` (pins English phonemes — the real
lever against the Indian-accent drift) and audio tags (emotion).

Measured, don't re-measure:

- `language_code` accepts only `"en"`; `"en-GB"` returns HTTP 400 from the API.
- v3 `stability` takes only 0.0 / 0.5 / 1.0.
- `similarity_boost` **0.20**. At 0.35 the Indian accent is still audible. Lower is
  cleaner but **less like them** — 0.20 is the line they accepted. Never raise it to
  make the voice "more similar"; that is what brings the accent back.
- v3 reads **~20% slower** than turbo_v2 (27.9s vs 23.1s for the same ten lines), so
  switching models means re-cutting every edit point, not swapping the audio file.
- v3 is **non-deterministic** — same text and settings give different takes. Re-roll
  the single bad line rather than rebuilding.

Emotion tags follow the caption rule: only on lines that actually carry emotion,
instruction lines stay bare. Stick to tags already heard (`[curious]`, `[pleased]`) —
unproven tags risk being spoken aloud.

Still short sentences, still one call per line then concat — the clone is built from
17 seconds of Vietnamese and drifts after 1-2 seconds. That has not changed.

Related: [[caption-placement-rule]], [[hook-construction-taste]],
[[vietnamese-voice-to-instagram-pipeline]], [[elevenlabs-mcp-setup]]
