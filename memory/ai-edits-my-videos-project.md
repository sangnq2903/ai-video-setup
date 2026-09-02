---
name: ai-edits-my-videos-project
description: "The \"AI Edits My Videos for Me\" project — how footage, script, and Notion come in, and where the human reference cuts live"
metadata: 
  node_type: memory
  type: project
  originSessionId: d9ad892e-9bcc-4ada-b1ec-6a95ce068696
  modified: 2026-08-25T12:56:14.269Z
---

Started 2026-08-25: an ongoing project called "AI Edits My Videos for Me". The
user supplies a footage folder path plus a Notion page holding the script, and
asks for the edit to be cut in DaVinci Resolve.

First job was the "Gear A6700" TikTok — footage at `/Volumes/Data/share/0826/gear6700`,
script on the Notion page "Gear A6700" (a top-5 gear list, in Vietnamese).

**Why:** the value is comparing an AI-built cut against the user's own edit of
the same material, so the human version is the benchmark, not clutter to clean up.

**How to apply:** before building, check `project_manager list` for an existing
Resolve project for the same shoot (`geara6700` held one). These projects often
already contain the finished human edit, recorded VO takes, and purchased SFX.
Never modify or delete the pre-existing timeline — build a separate,
clearly-named timeline alongside it. The Notion task being marked *Hoàn thành*
means the video already shipped; that is expected, not a reason to stop.

**Build the AI cut in its own Resolve project**, not inside the user's project
for the same shoot. Corrected on 2026-08-25: reusing their project and media
pool counts as leaning on their work even when the editorial is independent.
The AI version of the Gear A6700 cut lives in the project `AI Edits - Gear A6700`.

Tool trap worth remembering: `gallery_stills grab_and_export` **deletes the
grabbed still after exporting** unless `delete_after: false` is passed, so the
Gallery ends up empty while the files on disk look like proof it worked. Verify
with `get_stills` before claiming a still was saved, and never set a label by
guessing an index — the still you think is yours may be the user's.

Related: [[gear-a6700-footage-facts]], [[dark-cinematic-cdl-look]]
