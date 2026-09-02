---
name: vietnamese-voice-to-instagram-pipeline
description: The 4-step pipeline the user wants — their recorded Vietnamese voice becomes the script, the cut, and finally an English Instagram version
metadata:
  type: project
---

Stated 2026-09-01. The user's target workflow for "AI Edits My Videos for Me":

1. User hands over one folder containing both the video files **and their own
   recorded voice** (no separate Notion script written by hand first).
2. ElevenLabs `speech_to_text` transcribes that voice recording to Vietnamese text.
3. Claude turns the transcript into a script, writes it into Notion, then
   davinci-resolve-mcp builds the cut from it — laying the user's real voice
   recording onto the timeline as the VO, plus subtitles and effects.
4. Once the Vietnamese cut is done, produce an English version for Instagram,
   voiced with the user's **own cloned ElevenLabs voice**.

**Why:** the voice recording is the source of truth for the edit, not a
pre-written script — so transcription runs before any editorial decision.

**How to apply:** in step 3 the VO on the timeline is the user's original
recording, not a synthesized one; only the English Instagram pass in step 4
uses ElevenLabs TTS. Note [[resolve-2033-effects-limits]] constrains what
"effects" can actually mean in step 3.

Related: [[ai-edits-my-videos-project]], [[elevenlabs-mcp-setup]]

This whole pipeline is encoded as the personal slash command **`/video <folder>`**
at `~/.claude/commands/video.md` (kept out of the repo — `.claude/` there is
git-tracked and public). It carries the checkpoints, the Resolve-project
isolation rule, and the voice-id. Edit that file rather than re-explaining the
workflow.

Long-form YouTube is a **separate** skill, `~/.claude/skills/youtube-long/SKILL.md`
(horizontal 16:9, chapters, SEO title/description, **Vietnamese only — never calls
`text_to_speech`**). `/video` stays the short-form vertical path. Don't merge them.

**The script is a timestamped SHOT TABLE, not prose (2026-09-02).** Built from the
user's own voice, split by idea, four columns per row: timecode in-out (from
`speech_to_text`, never estimated), the line as spoken, a short label for the idea,
and **the shot to use or film**.

Where the folder already holds a matching clip, name the file. Where it does not,
describe the shot concretely enough to go and film it — angle, subject, action —
never "cảnh minh hoạ". The suggestion must match what is being said *at that second*.

Segment length: **TikTok 3-8s, YouTube 15-40s**. The table goes into Notion and also
feeds the marker notes, so opening Resolve shows the shot plan in place.

**Why:** this is what makes the shots manageable — a paragraph of script is unusable
for planning a shoot.

**`voice-timecode`** (`~/.claude/skills/voice-timecode/SKILL.md`) **is steps B1+B2
split out** — voice file in, timecoded table out, script written into Notion, no
Resolve touched. The user's preferred order (2026-09-02) is to run it first, approve
the script in Notion, and only then build.

When it has already run for a folder, `/video` and `youtube-long` must **reuse that
Notion page** rather than transcribing and re-writing the script — doing it again
costs API calls and produces a second script that diverges from the approved one.
