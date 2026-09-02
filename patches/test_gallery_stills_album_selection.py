"""`gallery_stills` must be able to reach PowerGrade albums, and by name.

A colourist's reusable looks live in **PowerGrade** albums — a list Resolve keeps
separate from still albums. `gallery.get_power_grade_albums()` listed them fine,
but every `gallery_stills` action resolved its album through
`GetGalleryStillAlbums()` alone, so asking for the second album when only one
still album existed answered "Album index out of range" — the look was visible in
the Gallery and unreachable through the API. Resolve's own `album.GetStills()`
works on either kind of album; only the selector was missing.

Name beats index here on purpose: a user says "the Sony album", and an album's
position shifts the moment another album is created.
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest import mock

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import src.server as server  # noqa: E402


class _Album:
    def __init__(self, name, still_count):
        self.name = name
        self._stills = [f"{name}-still-{i}" for i in range(still_count)]

    def GetStills(self):
        return list(self._stills)

    def GetLabel(self, still):
        return f"label::{still}"


class _Gallery:
    """Two independent album lists, the way Resolve keeps them."""

    def __init__(self, still_albums, power_albums):
        self._still = still_albums
        self._power = power_albums

    def GetGalleryStillAlbums(self):
        return list(self._still)

    def GetGalleryPowerGradeAlbums(self):
        return list(self._power)

    def GetCurrentStillAlbum(self):
        return self._still[0] if self._still else None

    def GetAlbumName(self, album):
        return album.name


def _run(action, params, *, still=None, power=None):
    still = still if still is not None else [_Album("Stills 1", 2)]
    power = power if power is not None else [
        _Album("Iphone", 3), _Album("Sony", 7), _Album("DJI", 5)
    ]
    project = mock.Mock()
    project.GetGallery.return_value = _Gallery(still, power)
    with mock.patch.object(server, "_check", return_value=(mock.Mock(), project, None)):
        return server.gallery_stills(action=action, params=params)


class PowerGradeAlbumSelectionTests(unittest.TestCase):
    def test_power_grade_album_is_reachable_by_name(self) -> None:
        """The reported gap: "the Sony PowerGrade album" must resolve."""
        result = _run("get_stills", {"album_type": "power_grade", "album_name": "Sony"})
        self.assertNotIn("error", result, result)
        self.assertEqual(result["count"], 7)

    def test_power_grade_album_is_reachable_by_index(self) -> None:
        result = _run("get_stills", {"album_type": "power_grade", "album_index": 2})
        self.assertEqual(result["count"], 5)

    def test_power_grade_defaults_to_the_first_album(self) -> None:
        """Resolve exposes no *current* PowerGrade album, so the first one stands
        in — silently falling back to a still album would hand back the wrong
        stills under a name the caller never asked for."""
        result = _run("get_stills", {"album_type": "power_grade"})
        self.assertEqual(result["count"], 3)

    def test_labels_come_from_the_named_power_grade_album(self) -> None:
        result = _run("get_label", {"album_type": "power_grade",
                                    "album_name": "Sony", "still_index": 0})
        self.assertEqual(result["label"], "label::Sony-still-0")

    def test_index_beyond_the_list_names_what_is_available(self) -> None:
        """An out-of-range index is usually a caller reaching for a PowerGrade
        album through the still list — the error has to say so."""
        result = _run("get_stills", {"album_type": "power_grade", "album_index": 9})
        self.assertIn("error", result)
        self.assertIn("Sony", result["error"]["remediation"])

    def test_unknown_name_lists_the_real_names(self) -> None:
        result = _run("get_stills", {"album_type": "power_grade", "album_name": "Canon"})
        self.assertIn("error", result)
        self.assertIn("Iphone", result["error"]["remediation"])

    def test_unknown_album_type_is_refused(self) -> None:
        result = _run("get_stills", {"album_type": "powergrade"})
        self.assertIn("error", result)
        self.assertIn("power_grade", result["error"]["remediation"])


class StillAlbumRegressionTests(unittest.TestCase):
    """The still-album path has to behave exactly as it did before."""

    def test_default_still_album_is_unchanged(self) -> None:
        result = _run("get_stills", {})
        self.assertEqual(result["count"], 2)

    def test_still_album_by_index_is_unchanged(self) -> None:
        result = _run("get_stills", {"album_index": 0})
        self.assertEqual(result["count"], 2)

    def test_power_grade_albums_do_not_leak_into_the_still_list(self) -> None:
        """Indexing past the still albums must still fail, not silently spill
        over into the PowerGrade albums."""
        result = _run("get_stills", {"album_index": 1})
        self.assertIn("error", result)

    def test_still_album_is_reachable_by_name(self) -> None:
        result = _run("get_stills", {"album_name": "Stills 1"})
        self.assertEqual(result["count"], 2)

    def test_no_albums_at_all_reports_the_requested_kind(self) -> None:
        result = _run("get_stills", {"album_type": "power_grade"}, power=[])
        self.assertIn("error", result)
        self.assertIn("power_grade", result["error"]["message"])


if __name__ == "__main__":
    unittest.main()
