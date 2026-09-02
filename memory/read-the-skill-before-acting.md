---
name: read-the-skill-before-acting
description: Load the project skill before performing a step it already covers — the answer is often already written down
metadata:
  type: feedback
---

2026-09-02: asked to generate an English VO, I called `text_to_speech` directly with
`eleven_multilingual_v2`, MCP default parameters, and one long paragraph. All three
were wrong, and **all three were already documented** in
`~/.claude/commands/video.md` — written at 15:34 that same day, with a working
`~/.claude/scripts/en-vo.py` beside it. I generated at 15:41 without reading it.

The user had even said *"phiên khác nhờ gắn vào mcp rồi"*; I went looking for a new
MCP server instead of for a rule already recorded in the file I had been editing all
session.

**Why:** the whole point of writing these skills down is that they get read. A rule
discovered by measurement and then ignored costs the measurement twice — and here it
also burned quota producing four unusable takes.

**How to apply:** before performing any step `/video`, `youtube-long` or
`voice-timecode` covers — TTS, grading, titles, markers, music — **read that section
first**. Especially when the user says something was settled in another session:
search the skill files before searching the machine.

Also: "don't change the settings" can mean *use the settings we agreed*, not *use the
tool's defaults*. When a documented parameter set exists, defaults are a choice, and
the wrong one.

Related: [[elevenlabs-mcp-setup]]
