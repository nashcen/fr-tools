"""TC-VER-* version profile output differences."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from lib.geojson.cli import main
from lib.geojson.profiles import get_profile

REPO = Path(__file__).resolve().parents[1]
V74 = "农业基地_v7.4_GCJ02_L3_SingleMap"
V73 = "农业基地_v7.3_GCJ02_L3"


@pytest.fixture()
def offline_env(tmp_path, monkeypatch):
    monkeypatch.setenv("FR_TOOLS_REPO", str(REPO))
    monkeypatch.setenv("GEOJSON_OUTPUT_DIR", str(tmp_path / "out"))
    monkeypatch.setenv("GEOJSON_SKIP_DB", "1")
    monkeypatch.setenv("GEOJSON_SKIP_DB_UPDATE", "1")
    monkeypatch.setenv("GEOJSON_PROTECT_EXISTING", "0")
    monkeypatch.setenv("MYSQL_PASSWORD", "test")
    monkeypatch.setenv("GEOJSON_WGS84_SUBDIR", str(tmp_path / "wgs84"))
    return tmp_path / "out"


def test_v74_no_legacy_merged(offline_env):
    os.environ["GEOJSON_VERSION"] = V74
    assert main(["--version", V74]) == 0
    legacy = list(offline_env.glob("农业基地_GCJ02_*.json"))
    assert legacy == [], f"unexpected legacy files: {legacy}"


def test_v73_writes_legacy_merged(offline_env):
    os.environ["GEOJSON_VERSION"] = V73
    assert main(["--version", V73]) == 0
    assert (offline_env / "农业基地_GCJ02_CS.json").is_file()
    assert (offline_env / "农业基地_GCJ02_WS.json").is_file()


def test_unknown_version_raises():
    with pytest.raises(KeyError, match="Unknown"):
        get_profile("农业基地_v9.9_unknown")


def test_profile_flags():
    p74 = get_profile(V74)
    assert p74.write_legacy_merged is False
    p73 = get_profile(V73)
    assert p73.write_legacy_merged is True
