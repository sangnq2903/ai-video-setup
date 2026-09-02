---
name: elevenlabs-mcp-setup
description: Where the ElevenLabs MCP server lives on this Mac and how it is wired into the project
metadata:
  type: reference
---

Installed 2026-09-01. `elevenlabs-mcp` runs from its own venv at
`~/.local/share/mcp-venvs/elevenlabs` (built on pyenv 3.12.14 — there is no
`uv`/`uvx` on this Mac, and system python3 is 3.9). It is registered as the
`elevenlabs` server in `/Volumes/Data/davinci-resolve-mcp/.mcp.json`, which is
gitignored, so the API key sits there safely.

`ELEVENLABS_MCP_BASE_PATH` is set to `/Volumes/Data/share`, so `output_directory`
on any ElevenLabs tool is relative to the footage root (e.g. `0826/gear6700/vo`).
Default without it would be `~/Desktop`.

Related: [[vietnamese-voice-to-instagram-pipeline]], [[ai-edits-my-videos-project]]

Account state as of 2026-09-01: **Starter** tier, instant voice cloning enabled
(professional cloning is not), ~40k characters/month.

The user's own cloned voice already exists in the account — **"Sáng"**,
voice_id `xYGgUqVrkXAXMWJZtqgF` (category `cloned`), confirmed by the user as
their voice. Use it for the English Instagram pass in
[[vietnamese-voice-to-instagram-pipeline]].

**Correction (2026-09-02): re-cloning is NOT scarce.** Measured from
`check_subscription`: `voice_limit` 10 with only 1 slot used, and
`max_voice_add_edits` 65 with `voice_add_edit_counter` at 0. An earlier note here
said not to re-clone because it would "burn a voice slot" — that was wrong. Cloning
a second voice (e.g. an English-audio version of Sáng) costs one of nine free slots.
What IS scarce is characters: 40k/month, ~4.8k used as of 2026-09-02.

Model picks: `speech_to_text` (Scribe) for the Vietnamese transcription step,
**`eleven_turbo_v2` for the English VO** (was `eleven_multilingual_v2` — changed
2026-09-02, see the accent section below).


## `speech_to_text` returns NO timestamps — go to the HTTP API for subtitles

Confirmed 2026-09-01. The MCP tool has no timestamp parameter and writes a
plain-text file; word timings are simply not exposed. It also swallows the file
when `return_transcript_to_client_directly=True` (nothing is written), and its
success message echoes the INPUT path ("Transcription saved to .../voice.mov"),
which reads alarmingly like it overwrote the source — it did not.

For anything needing subtitle timing, skip the MCP tool and POST straight to
`https://api.elevenlabs.io/v1/speech-to-text` with `model_id=scribe_v1`,
`language_code=vie`, `timestamps_granularity=word`, reading the key out of
`.mcp.json`. Returns `words[]` with per-word `start`/`end` plus `audio_event`
entries (e.g. `[nhạc nền]`). One call instead of three.

**Why:** doing it the obvious way costs three API calls and still leaves you
unable to build subtitles.

**`speech_to_text` returns NO timestamps (measured 2026-09-02).** The tool hands back
`transcription.text` only and discards the per-word `start`/`end` the ElevenLabs API
actually provides; `format_diarized_transcript` drops them too. There is no parameter
to get them back.

Workaround, measured on a 28.5s `voice.mov`: `ffmpeg -af silencedetect=n=-32dB:d=0.35`
found **9 speech segments** against **8 transcript sentences** — close but not 1:1
(some pauses fall mid-sentence; `d=0.5` over-merges to 6). Assigning sentences to
segments takes judgement based on sentence length, so timecodes land within about
**±0.5s**.

Fine for a shot table and for markers. **Not fine for subtitles** — say so up front if
the user asks for text synced to speech.



## "Sáng" speaks English with a non-native (Indian-sounding) accent — by design

Raised by the user 2026-09-02. **ElevenLabs has no accent control for a cloned
voice.** Accent is baked in at clone time from the source audio; "Sáng" is an IVC
clone of Vietnamese speech, so English output borrows Vietnamese phonemes and reads
to the ear as South-Asian. No `text_to_speech` parameter removes this.

PVC (professional cloning), which is the proper fix because it locks a target
language, is **unavailable on Starter** (`can_use_professional_voice_cloning: false`).

Levers that exist, weakest to strongest:
- English-only models `eleven_turbo_v2` / `eleven_flash_v2` instead of
  `eleven_multilingual_v2` — English-only phoneme set.
- Lower `similarity_boost` (0.25-0.35) and `use_speaker_boost: false` — the model
  adheres less to the source's accent, at the cost of resemblance. It is a
  trade-off dial, not a fix: neutral English and "sounds like Sáng" pull opposite ways.
- **Re-clone from 1-3 min of the user speaking English.** The real fix at this tier,
  bounded by how the user's own English actually sounds.
- Use a native-English library voice for the Instagram pass — no accent problem, but
  it stops being his voice.

A/B/C/D comparison renders live in `/Volumes/Data/share/voice-tests/accent/`.

**SETTLED 2026-09-02 — the user listened and chose B:**

```
model_id=eleven_turbo_v2  stability=0.55  similarity_boost=0.35
style=0  use_speaker_boost=False
```

**The MCP tool ignores the voice's stored defaults — pass all four every time.**
These values were also written to the voice via
`POST /v1/voices/{id}/settings/edit`, but that is cosmetic for this pipeline:
`elevenlabs_mcp/server.py` (~line 260 and 303) declares `stability=0.5,
similarity_boost=0.75, use_speaker_boost=True` as *function defaults* and always
sends a full `voice_settings` block. Omit the arguments and you silently get the
old Indian-accented voice back. The stored defaults only apply on elevenlabs.io.

Prior settings, for rollback:
`/Volumes/Data/share/voice-tests/accent/sang_settings_BEFORE_20260902.json`
(stability 0.42, sim 0.75, style 0.5, speed 0.96, boost true).

`~/.claude/commands/video.md` step B4 carries all of this — edit there, not here.

**Why:** the instinct is to hunt for an accent setting in the API. There isn't one —
going straight to model choice and re-cloning saves the search.

## ROOT CAUSE of the accent: "Sáng" was cloned from only 17 seconds

Measured 2026-09-02 from `GET /v1/voices/{id}`. The voice has **2 samples totalling
16.9s** — `Ia Phi 12.mp3` (5.7s) and `Ia Phi 13.mp3` (11.2s). ElevenLabs IVC wants
60s minimum and 120-180s to be good. A 17-second clone is unstable and drifts toward
generic accents; that, not the model or the sliders, is why English output sounds
Indian. Setting B (turbo_v2 + low similarity) only masks it.

**Two fields on the voice look like accent controls and are NOT:**
- `description` — before 2026-09-02 it read *"Native English speaker… Modern
  California accent… No foreign accent. Clear American pronunciation."* That is a
  **voice-design prompt written on a cloned voice, where it does nothing.** It never
  influenced a single generation. (Prompts only build voices via `text_to_voice`.)
  It has since been overwritten with the actual config as a visible note.
- `labels.accent` is `en-british`, contradicting that text. Also inert metadata.

**What can and cannot live on the voice:** the four sliders (`stability`,
`similarity_boost`, `style`, `use_speaker_boost`, plus `speed`) persist on the voice
and show on elevenlabs.io. **`model_id` does not** — it is per-request, so on the web
the Eleven Turbo v2 dropdown must be picked by hand every time.

Backups: `sang_voice_BEFORE_20260902.json` (full metadata incl. old description) and
`sang_settings_BEFORE_20260902.json`, both in `/Volumes/Data/share/voice-tests/accent/`.

**Why:** the obvious move is to keep tuning sliders. With a 17s source there is no
slider that gets there — budget the re-clone instead.

**SUPERSEDED — setting B was tried and REJECTED (2026-09-02, same day).** The user
first said "dùng B như trước đó đã sử dụng là được", but after hearing more samples
came back with: *"vẫn accent giọng ấn"*. **B does not solve the accent.** It only
lowers `similarity_boost` so the model adheres less to a bad clone — a mask, not a
fix. Do not re-propose slider tuning as a solution.

**The user's real requirement, stated plainly:** *"tôi chỉ cần giọng của tôi, nhưng
không được có accent kiểu Ấn, phải chuẩn tiếng anh"* — their own voice, no Indian
accent. They rejected native-American library voices and Voice Design previews
because those are not their voice.

**The one path that fits: re-clone from 1-3 min of the user speaking English.**
The Indian accent is a **model artifact of the 17-second clone**, not the user's real
accent — with enough English audio the model stops inventing and reproduces the
user's actual pronunciation. Told them honestly it yields *their* English, not native
American; no tool gives "their voice + American accent".

Recording script prepared at
`/Volumes/Data/share/voice-tests/reclone/BAI-DOC-DE-CLONE.txt` (~2.4 min, sections
targeting th / r / l / final consonants / v-w, plus recording rules: same mic as their
normal VO, no processing, 90s minimum). **Waiting on the user's recording** as of
2026-09-02. When it arrives: `voice_clone` into a NEW voice, keep old "Sáng" for
Vietnamese, then A/B the same test line.

## SOLVED 2026-09-02 — render one short sentence per call, then concatenate

The accent was a **length effect**, and the user's own A/B proved it. Same voice,
same setting B, same wording: a 1.25s clip he accepted, a 9s clip of the same content
he rejected as "vẫn accent giọng ấn". The 17-second clone holds its voice for roughly
**1-2 seconds and then drifts** into the invented South-Asian accent.

So: **never send a paragraph to `text_to_speech`.** Send one short sentence per call
(1-2s, keep under ~12 words) and stitch the mp3s with ffmpeg, 0.18s of silence
between. The user listened to a stitched 9s render against the single-call 9s render
and said *"bản này oke nhất"*.

This also means **the re-clone is no longer needed** — the recording script at
`/Volumes/Data/share/voice-tests/reclone/BAI-DOC-DE-CLONE.txt` was never used. Keep
it in case the accent returns, but do not ask the user to record unless it does.

**Tool: `~/.claude/scripts/en-vo.py`** — takes a .txt with one sentence per line,
calls the API per line with voice `Sáng` + `eleven_turbo_v2` + setting B, concatenates,
and warns on any line over 12 words. Reads the key from `.mcp.json`; `--dry-run` shows
the character cost without spending it. Verified end-to-end 2026-09-02 (5 lines,
145 chars, 9.03s out). `/video` step B4 now mandates it.

The name "Sáng" must be respelled **`Sahng`** in English scripts — `eleven_turbo_v2`
is English-only and mangles the diacritic. The user picked this spelling from an A/B.

**Why:** every instinct here (slider tuning, model swapping, re-cloning) targets the
voice. The variable that actually mattered was **utterance length**, which no
ElevenLabs setting exposes.


## What the MCP server itself can and cannot be configured to do

Checked the installed package 2026-09-02. Only these env vars are actually read
(`server.py:57-69`, `utils.py:183`): `ELEVENLABS_API_KEY`, `ELEVENLABS_MCP_BASE_PATH`,
`ELEVENLABS_MCP_OUTPUT_MODE`, `ELEVENLABS_DEFAULT_VOICE_ID`, `ELEVENLABS_API_RESIDENCY`.

**`ELEVENLABS_MODEL_ID` is a trap.** The `text_to_speech` docstring says the model
"Defaults to eleven_multilingual_v2 or environment variable ELEVENLABS_MODEL_ID" —
**that env var is never read.** The code hardcodes `eleven_flash_v2_5` for hu/no/vi
and `eleven_multilingual_v2` otherwise. Setting it does nothing. Pass `model_id`
explicitly every call.

`ELEVENLABS_DEFAULT_VOICE_ID` **was** set to `xYGgUqVrkXAXMWJZtqgF` ("Sáng") in
`.mcp.json` on 2026-09-02, so a call with no voice at least lands on the user's voice
instead of a stranger's. Backup: `/Volumes/Data/share/voice-tests/mcp.json.backup-20260902`.
Takes effect only after the MCP server restarts.

**Voice settings cannot be configured at MCP level at all** — stability/similarity/
style/speaker_boost are Python function defaults with no env override. And the
one rule that matters most, *one short sentence per call*, is not a parameter in the
first place — it is about call granularity. No MCP config can express it. That is why
enforcement lives in `~/.claude/commands/video.md` and `~/.claude/scripts/en-vo.py`,
not in configuration.

### PATCHED 2026-09-02 — `ELEVENLABS_MODEL_ID` now actually works

The "trap" above was fixed rather than worked around. `server.py` (~line 291, inside
`text_to_speech`) was patched to read `ELEVENLABS_MODEL_ID`, which its own docstring
had always promised. `.mcp.json` now sets it to `eleven_turbo_v2`.

Resolution order, verified by table test: explicit `model_id` argument > env var >
package default. **Guarded:** when `language` is vi/hu/no the env var is ignored and
`eleven_flash_v2_5` is used, because English-only models cannot speak those — chosen
deliberately so the patch cannot recreate the silent-wrong-default bug it exists to
prevent.

`.mcp.json` env now: `ELEVENLABS_API_KEY`, `ELEVENLABS_MCP_BASE_PATH`,
`ELEVENLABS_DEFAULT_VOICE_ID` (Sáng), `ELEVENLABS_MODEL_ID` (eleven_turbo_v2).

**This patch lives in site-packages and is DESTROYED by any reinstall or upgrade of
`elevenlabs-mcp`.** After upgrading, re-apply it — the env var in `.mcp.json` survives
but goes inert, which looks like everything is configured while nothing is.
Backups: `server.py.backup-20260902` and `mcp.json.backup-20260902` in
`/Volumes/Data/share/voice-tests/`.

Still NOT configurable anywhere: the voice-settings defaults (stability 0.5 /
similarity 0.75 / speaker_boost True). A bare MCP call still gets those, so passing
setting B explicitly remains mandatory — as does one-short-sentence-per-call.

**Do not tune TTS parameters unasked (2026-09-02).** Leave `stability`, `style`,
`similarity_boost` and `speed` at their defaults. Offering a tweak is fine; applying
one without being asked is not — the user wants to hear the voice as it actually is,
not a version I have quietly adjusted underneath them.

**Use `eleven_multilingual_v2` for the "Sáng" voice. Never `eleven_v3`.** Tested
2026-09-02 with identical text and identical default settings, changing only the
model: v3 pulled the clone's timbre toward an **Indian accent**. The clone was built
from Vietnamese samples, and v3 reconstructs it differently.

This is a trap worth remembering because v3 *sounds* more expressive on a first
listen, so it invites being picked. On a video published under the user's own name,
a drifted accent is a far worse failure than slightly flat intonation.

**Emotion comes from the writing, not the parameters or the model.** What worked on
v2 at default settings: an opening interjection ("Okay —"), ellipses for suspense,
a rhetorical question, clipped one-line sentences for emphasis, a repeated word
before the punchline ("And nothing... nothing gets rendered"), and splitting a list
into separate sentences. Audio tags like `[excited]` do NOT work on v2 — it reads
them out loud.

