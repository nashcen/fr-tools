"""Pytest fixtures — offline GeoJSON generation."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
GOLDEN_ROOT = REPO_ROOT / "tests" / "golden" / "geojson"
VERSION = "农业基地_v7.4_GCJ02_L3_SingleMap"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture()
def geojson_out_dir(tmp_path, monkeypatch) -> Path:
    """Isolated output directory; never touches frozen FineReport GeoJSON."""
    out = tmp_path / "generated"
    out.mkdir()
    monkeypatch.setenv("FR_TOOLS_REPO", str(REPO_ROOT))
    monkeypatch.setenv("GEOJSON_VERSION", VERSION)
    monkeypatch.setenv("GEOJSON_OUTPUT_DIR", str(out))
    monkeypatch.setenv("GEOJSON_SKIP_DB", "1")
    monkeypatch.setenv("GEOJSON_SKIP_DB_UPDATE", "1")
    monkeypatch.setenv("GEOJSON_PROTECT_EXISTING", "0")
    monkeypatch.setenv("MYSQL_PASSWORD", "test-not-used")
    monkeypatch.setenv("GEOJSON_WGS84_SUBDIR", str(tmp_path / "wgs84_sidecar"))
    monkeypatch.delenv("GEOJSON_MAP_SUBDIR", raising=False)
    return out


def load_manifest(version: str) -> dict:
    path = GOLDEN_ROOT / version / "manifest.json"
    if not path.is_file():
        pytest.skip(f"golden manifest missing: {path}")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)
