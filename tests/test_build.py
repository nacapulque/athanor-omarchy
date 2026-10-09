"""End-to-end build at a small size. Needs ImageMagick 7, so it's skipped where `magick` is missing."""

import shutil
import tomllib

import pytest

from athanor_omarchy.build import build_theme
from athanor_omarchy.images import plate_names

pytestmark = pytest.mark.skipif(shutil.which("magick") is None, reason="needs ImageMagick 7")


def test_build_writes_a_complete_theme(tmp_path):
    build_theme("umber", tmp_path, width=192, height=108, pixel=2)
    d = tmp_path / "athanor-umber"
    expected = {"colors.toml", "icons.theme", "LICENSE", "README.md", "unlock.png", "preview.png", "preview-unlock.png", "shell.bar.toml"}
    assert expected <= {p.name for p in d.iterdir()}
    assert sorted(p.name for p in (d / "backgrounds").iterdir()) == sorted([*plate_names(), "omarchy.png"])
    tomllib.loads((d / "colors.toml").read_text())
