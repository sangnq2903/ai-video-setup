"""`capture` must be able to hand back a FILE, not only an inline image.

Dialling exposure or white balance is a measuring job: render the frame, read
`YMAX` / `UAVG` / `VAVG` out of `ffmpeg -vf signalstats`, nudge, measure again.
That needs the rendered pixels on disk. `capture` already renders to a temp folder
and then deletes it, and the only other route to a file —
`gallery_stills.grab_and_export` — fails outright unless a human has the Gallery
panel open on the Color page, which no API call can do.

`out_path` keeps the frame the render already produced.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import src.server as server  # noqa: E402

FRAME_BYTES = b"\x89PNG\r\n\x1a\n-pretend-this-is-a-rendered-frame"


class _Project:
    """Resolve's single-frame render, reduced to what the capture path touches.

    `StartRendering` is where the file appears, because that is when Resolve
    writes it.
    """

    def __init__(self, folder):
        self.folder = folder
        self.name = None

    def IsRenderingInProgress(self):
        return False

    def GetRenderCodecs(self, _fmt):
        return {"PNG": "png"}

    def SetCurrentRenderFormatAndCodec(self, *_):
        return True

    def SetRenderSettings(self, settings):
        self.name = settings["CustomName"]
        return True

    def AddRenderJob(self):
        return "job-1"

    def StartRendering(self, _jobs, isInteractiveMode=False):
        os.makedirs(self.folder, exist_ok=True)
        with open(os.path.join(self.folder, f"{self.name}0001.png"), "wb") as fh:
            fh.write(FRAME_BYTES)
        return True

    def GetRenderJobStatus(self, _job):
        return {"JobStatus": "Complete"}

    def DeleteRenderJob(self, _job):
        return True


class _Timeline:
    def GetSetting(self, key):
        return "24" if key == "timelineFrameRate" else ""

    def GetStartFrame(self):
        return 0

    def GetCurrentTimecode(self):
        return "01:00:00:00"

    def SetCurrentTimecode(self, _tc):
        return True


class CaptureOutPathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.render_dir = os.path.join(self.tmp.name, "renders")

    def _capture(self, params):
        proj = _Project(self.render_dir)
        with mock.patch.object(server, "_resolve_safe_dir", side_effect=lambda _p: self.render_dir), \
                mock.patch.object(server.time, "sleep", lambda *_: None):
            return server._playhead_frame_render(proj, _Timeline(), dict(params))

    def test_out_path_returns_the_saved_file_instead_of_an_image(self) -> None:
        dest = os.path.join(self.tmp.name, "frame.png")
        result = self._capture({"format": "png", "out_path": dest})

        self.assertNotIn("error", result, result)
        self.assertEqual(result["saved"], dest)
        with open(dest, "rb") as fh:
            self.assertEqual(fh.read(), FRAME_BYTES,
                             "the saved file must be the rendered frame, byte for byte")

    def test_missing_parent_directories_are_created(self) -> None:
        """A caller measuring a batch names a subfolder it has not made yet."""
        dest = os.path.join(self.tmp.name, "deep", "nested", "frame.png")
        result = self._capture({"format": "png", "out_path": dest})
        self.assertNotIn("error", result, result)
        self.assertTrue(os.path.exists(dest))

    def test_tilde_is_expanded(self) -> None:
        dest = os.path.join(self.tmp.name, "tilde.png")
        with mock.patch.object(server.os.path, "expanduser", return_value=dest) as expand:
            result = self._capture({"format": "png", "out_path": "~/tilde.png"})
        expand.assert_called_once_with("~/tilde.png")
        self.assertEqual(result["saved"], dest)

    def test_an_unwritable_destination_explains_itself(self) -> None:
        dest = os.path.join(self.tmp.name, "frame.png")
        with mock.patch.object(server.shutil, "copyfile", side_effect=OSError("read-only")):
            result = self._capture({"format": "png", "out_path": dest})
        self.assertIn("error", result)
        self.assertIn("read-only", result["error"]["message"])
        self.assertIn("out_path", result["error"]["remediation"])

    def test_without_out_path_the_frame_still_comes_back_inline(self) -> None:
        """The default path must not change — this is an addition, not a swap."""
        result = self._capture({"format": "png"})
        self.assertFalse(isinstance(result, dict) and "saved" in result,
                         "no out_path must still return inline image content")


if __name__ == "__main__":
    unittest.main()
