---
name: elevenlabs-stt-timestamps
description: Calling the ElevenLabs speech-to-text REST endpoint directly returns real word-level timestamps, so the ±0.5s silencedetect workaround is only needed when the MCP tool is the only option
metadata:
  type: reference
---

The "ElevenLabs gives no timestamps" rule is a limitation of the **MCP tool**, not of
ElevenLabs. `speech_to_text` in the MCP server returns only `transcription.text` and
throws away each word's `start`/`end`. The **REST API keeps them.**

`POST https://api.elevenlabs.io/v1/speech-to-text`, multipart, with
`model_id=scribe_v1`, `language_code=vie`, `timestamps_granularity=word` returns a
`words[]` array where every entry carries `start` and `end`. Measured 2026-09-02 on
the phonetotreamdesk cut: 153 words over 31.54s, split cleanly into 12 sentences with
exact in/out points — no `silencedetect` guessing, no ±0.5s error bar.

**How to apply:** when the MCP server is not loaded (or when subtitles need to track
speech per line), call the endpoint directly and read the key at run time from the
`mcpServers.elevenlabs.env.ELEVENLABS_API_KEY` entry of
`/Volumes/Data/davinci-resolve-mcp/.mcp.json` — the same source `en-vo.py` uses. Fall
back to `ffmpeg -af silencedetect` only when neither path is available.

This matters most for the caption/subtitle case, where the skill otherwise warns the
user that word-synced text is not achievable.

Related: [[english-vo-config]], [[elevenlabs-mcp-setup]]
