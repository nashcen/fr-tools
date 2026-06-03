"""Pytest fixtures — offline GeoJSON generation."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from lib.geojson.profiles import ALL_VERSION_DIRS

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_ROOT = REPO_ROOT / "tests" / "golden" / "geojson"
DEFAULT_VERSION = "农业基地_v7.4_GCJ02_L3_SingleMap"
SINK_ROOT = REPO_ROOT / "data" / "sink"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def sink_all_versions() -> Path:
    """
    Generate v7.0–v7.4 into data/sink/{版本}/.
    Leaves artifacts on disk after pytest (required for sink acceptance).
    """
    from lib import settings
    from lib.geojson.cli import main

    os.environ.setdefault("FR_TOOLS_REPO", str(REPO_ROOT))
    os.environ["GEOJSON_SKIP_DB"] = "1"
    os.environ["GEOJSON_SKIP_DB_UPDATE"] = "1"
    os.environ["GEOJSON_PROTECT_EXISTING"] = "0"
    os.environ.setdefault("MYSQL_PASSWORD", "test")

    settings._boot.cache_clear()
    root = settings.data_sink_root()
    root.mkdir(parents=True, exist_ok=True)
    wgs84 = settings.geojson_wgs84_dir()
    wgs84.mkdir(parents=True, exist_ok=True)
    os.environ["GEOJSON_WGS84_SUBDIR"] = str(wgs84)

    for version in ALL_VERSION_DIRS:
        out = root / version
        out.mkdir(parents=True, exist_ok=True)
        os.environ["GEOJSON_VERSION"] = version
        os.environ["GEOJSON_OUTPUT_DIR"] = str(out)
        assert main(["--version", version]) == 0, version

    return root


@pytest.fixture()
def geojson_out_dir(tmp_path, monkeypatch) -> Path:
    """Isolated output for tests that must not touch sink (e.g. protect_existing)."""
    out = tmp_path / "generated"
    out.mkdir()
    monkeypatch.setenv("FR_TOOLS_REPO", str(REPO_ROOT))
    monkeypatch.setenv("GEOJSON_VERSION", DEFAULT_VERSION)
    monkeypatch.setenv("GEOJSON_OUTPUT_DIR", str(out))
    monkeypatch.setenv("GEOJSON_SKIP_DB", "1")
    monkeypatch.setenv("GEOJSON_SKIP_DB_UPDATE", "1")
    monkeypatch.setenv("GEOJSON_PROTECT_EXISTING", "0")
    monkeypatch.setenv("MYSQL_PASSWORD", "test-not-used")
    monkeypatch.setenv("GEOJSON_WGS84_SUBDIR", str(tmp_path / "wgs84_sidecar"))
    return out


def sink_version_dir(sink_all_versions: Path, version: str) -> Path:
    path = sink_all_versions / version
    assert path.is_dir(), f"sink missing after generation: {path}"
    return path


def load_manifest(version: str) -> dict:
    path = GOLDEN_ROOT / version / "manifest.json"
    if not path.is_file():
        pytest.fail(f"golden manifest missing: {path} — run tests/tools/build_all_golden_manifests.py")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def run_generate(version: str) -> None:
    os.environ["GEOJSON_VERSION"] = version
    from lib.geojson.cli import main

    assert main(["--version", version]) == 0
