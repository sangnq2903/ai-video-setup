---
name: epidemic-sound-mcp
description: Epidemic Sound MCP server — how it is wired in, and why it replaced ElevenLabs music generation for this user's videos
metadata:
  type: reference
---

Added 2026-09-02. Epidemic Sound ships a **remote HTTP** MCP server (beta):
`https://www.epidemicsound.com/a/mcp-service/mcp`, registered as `epidemic-sound`
in `/Volumes/Data/davinci-resolve-mcp/.mcp.json` (gitignored).

Auth is either **OAuth** (browser, needs an interactive session — `/mcp` or
`claude mcp`) or an **API key** as `Authorization: Bearer …`, generated at
`epidemicsound.com/account/api-keys`. **API keys expire after one year.** Either
way an active Epidemic Sound subscription is required.

**Verified live 2026-09-02** with real calls. The tool names in Epidemic's own
docs are WRONG — the server exposes GraphQL-style names: `SearchRecordings`,
`SearchSoundEffects`, `SearchSimilarToRecording`, `SearchSimilarToSoundEffect`,
`EditRecording` + `PollEditRecordingJob`, `DownloadRecording`,
`DownloadRecordingEdit`, `DownloadSoundEffect`, plus voiceover tools.

Two things worth knowing: every search result carries `audioFile.lqmp3Url`, a
low-quality preview — send those to the user to choose from before spending a
download. And tracks expose `stems` (BASS/MELODY/INSTRUMENTS/VOCALS), so when
music fights the voice, swap to the instrumental stem instead of just pulling the
gain down. Results are verbose: keep `first` at 3-5.

**This replaced ElevenLabs `compose_music` in both video skills.** Reason: the
Epidemic catalogue carries an all-inclusive sync/mechanical/performance licence
for YouTube and Instagram; AI-generated music does not, and the user publishes
commercially.

Downloads go to `<folder>/music/`, never into the source footage directory.

Related: [[vietnamese-voice-to-instagram-pipeline]], [[elevenlabs-mcp-setup]]
