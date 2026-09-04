---
name: sony-powergrade-exp-workflow
description: How the user asks for a colour look — "lấy 1.5.1" means a PowerGrade still, then the EXP node is tuned so the waveform sits just under 896
metadata:
  type: project
---

Stated 2026-09-02. The user grades by **naming a PowerGrade still**: *"lấy 1.5.1"*
means still labelled `1.5.1` in the **PowerGrade album `Sony`**. Their Gallery holds
three PowerGrade albums — `Iphone`, `Sony`, `DJI` — pick the one matching the camera
the footage came from.

**Applying the grade is only half the job.** Afterwards the node named **`EXP`** must
be adjusted so the **waveform peak sits just under 896** on the 10-bit scale. That
number is their standard: bright enough, highlights not clipped.

**CORRECTED 2026-09-02:** an earlier version of this note said to "adjust
gain/offset on the EXP node". That is not possible — the API cannot read or write
primary grade values at all (`api_truth`: "Color node graph editing and primary
grade values"). The only writable control is **CDL**, and `safe_set_cdl` takes a
**1-based `NodeIndex`**, so a named node is still reachable: read
`graph get_num_nodes`, loop `graph get_node_label(i)` to find the index of the node
labelled `EXP` (or `WB`), then write CDL to that index. If no node carries the name,
stop and say so rather than guessing an index.

**Two nodes, in this order — `WB` first, then `EXP`,** because a colour change moves
luma and would invalidate an exposure pass done first.

- **`WB`**: read `UAVG` / `VAVG` from `signalstats`; neutral is 128. UAVG high =
  blue (lower Slope[2]); VAVG high = red (lower Slope[0]). Steps of ±0.02, done when
  both land in 126-130.
- **`EXP`**: read `YMAX`, move Slope uniformly across all three channels until it
  sits just under 896 (10-bit) ≈ 223 (8-bit). Re-measure after WB.

**Do not "correct" a scene that is genuinely coloured.** UAVG/VAVG average the whole
frame, so a red wall or a full-frame green reads as a cast. Crop to a neutral
reference if the shot has one; otherwise skip WB and say why. Run `dry_run` before
each `safe_set_cdl`, and re-measure. Cap at 4-5 iterations; if it will not converge, stop and report the
measurement rather than nudging blindly. Measure the **brightest frame of the
shot**, not the first one. Report the real YMAX.

**Blocker as of 2026-09-02:** this server's `gallery_stills` resolves albums only
through `GetGalleryStillAlbums()`, so a PowerGrade album returns
"Album index out of range" — even though `gallery.get_power_grade_albums()` lists
all three, and Resolve's own `album.GetStills()` works on either album type. The gap
is in `src/server.py` (~line 26189), not in Resolve. Until it is patched, grades have
to come from a `.drx` on disk via
`timeline_item_color apply_grade_from_drx(path)`.

Related: [[dark-cinematic-cdl-look]], [[timeline-and-render-defaults]]

**Confirmed 2026-09-02: `Sony` / `1.5.1` is the DEFAULT look.** Apply it and tune
`EXP` on every job without being asked; only a named alternative (`lấy 1.4.2`,
`lấy Iphone 1.2.1`) overrides it, and only an explicit "không grade" skips it.
This is the one optional-looking step that is NOT opt-in — unlike music and text,
see [[editing-deliverable-preferences]].

The user also decided the English Instagram pass **stays on by default**; they type
`vn-only` when they don't want it. Do not flip that to opt-in.

## PROVEN END TO END 2026-09-02 (after the MCP patch)

`gallery_stills get_stills album_type=power_grade album_name=Sony` -> 5 stills. The
patch works.

**Labels are almost all empty** — only one still carries a label ("Final"), so
`get_label` cannot find "1.5.1". The number lives **only in the exported filename**.
The working sequence:

1. `export_stills` (album_type power_grade, album_name Sony, format `drx`) into a
   scratch dir that **already exists** — a missing dir returns a bare
   `success: false` with no reason.
2. Filenames come back as `pg_1.1.1.drx`, `pg_1.1.2.drx`, `pg_1.43.1.drx`,
   `pg_1.5.1.drx`, `pg_1.9.1.drx`. **The numbering is NOT sequential** — guessing
   "1.5.1 is the fifth still" picks `1.9.1` instead. Match the filename.
3. `add_version` first (its parameter is **`name`**, not `version_name`).
4. `safe_apply_drx` — returns a `confirm_token` on the first call, applies on the
   second. Verified live on clip C0805.MP4: the cutting mat went grey -> green,
   the frame warmer and less contrasty.

**`safe_apply_drx` REPLACES the entire node graph** ("no append mode"), so creating
a grade version first is not optional — without it the user's existing grade on that
clip is gone.

**Still blocked, needs a human:** `grab_and_export` (the route to a measurable frame
file for the WB/EXP numbers) fails with "ensure the Gallery panel is open on the
Color page". `resolve_control open_page color` switches the page but cannot open the
panel. Ask the user to open Workspace > Gallery once.

**Second MCP patch, 2026-09-02: `timeline_frame capture` now takes `out_path`.**
It saves the frame the render already produced and returns
`{saved, frame, format}` instead of inline image content — the measurable file the
WB/EXP loop needs. `capture` was already doing a single-frame render into a temp
folder and deleting it afterwards; `out_path` just keeps a copy.

This replaces `gallery_stills grab_and_export` for measurement. That route is a dead
end for automation: it fails with "ensure the Gallery panel is open on the Color
page" and **a fresh project does not help — the panel is app-level UI state**, and
`resolve_control open_page color` switches the page but cannot open the panel.

Covered by `tests/test_timeline_frame_out_path.py` (5 tests); full suite 2914 tests,
only the 5 pre-existing `requests`-import errors.

**PowerGrade album CONTENTS are not fully portable between projects (2026-09-02).**
The three album names (`Iphone`, `Sony`, `DJI`) show up in a brand-new project, but
`Sony` reported **5 stills in "AI Edits - Tranh Treo Tuong"** and only **1 in the
fresh `_mcp_wb_test` project**. So "lấy 1.5.1" cannot be assumed to resolve in an
empty project.

The robust route is the exported `.drx`: export the album once from the project that
holds the looks, keep the files, and `safe_apply_drx` them anywhere. The exports from
this session live in the session scratchpad as `pg_1.1.1.drx` … `pg_1.9.1.drx`.

## DROPPED 2026-09-02: no automatic WB/EXP tuning

The user cancelled the measure-and-tune loop before it ever ran — too much machinery
for the value. **Apply the look and stop.** No `signalstats`, no `WB`/`EXP` node
adjustment, no iteration. They tune by hand in Resolve, which is the part of the job
they want to keep.

Everything above about `UAVG`/`VAVG`/`YMAX` is retained as reference only, in case
they ask again. **Do not re-enable it without asking.**

What stays in use: apply the PowerGrade look from an exported `.drx`, on a fresh
grade version, and cut by scene as usual.

**REVERSED 2026-09-02 (same day): there is no default look either.** Do not apply
any grade unless the user names one. The `lấy <mã>` mechanism stays and works; it is
simply never triggered on its own.

## FINAL 2026-09-04: colour measurement is the user's job, not mine

They asked me once to check `EXP` against 896 and `WB` for neutrality, I measured it,
and then they closed it: *"thôi không cần skill này tôi tự đo và chỉnh"*.

**Do not measure grades. Do not offer to.** Not the waveform, not UAVG/VAVG, not
percentiles. They read their own scopes and adjust by hand — that is the part of the
craft they keep.

The measurement technique is kept below purely as reference in case they ever ask
again for a one-off. It is not a step in any workflow, and it never appears in a
report unsolicited.

One honest limit worth remembering if they do ask: `UAVG`/`VAVG` average the whole
frame, so a shot with skin or a coloured subject reads as a cast when the white
balance is fine. A number is not a verdict without a neutral reference in frame.

