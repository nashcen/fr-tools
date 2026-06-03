"""Parametric tests for v7.0–v7.4 generation scripts and golden manifests."""

from __future__ import annotations

from pathlib import Path

import pytest

from lib.geojson.profiles import ALL_VERSION_DIRS, get_profile
from tests.conftest import SINK_ROOT, load_manifest, sink_version_dir
from tests.tools.build_geojson_manifest import build_manifest

REPO = Path(__file__).resolve().parents[1]
VERSIONS_ROOT = REPO / "scripts" / "versions"


@pytest.mark.parametrize("version", ALL_VERSION_DIRS)
def test_version_entry_script_exists(version: str):
    script = VERSIONS_ROOT / version / "geojson_generate_from_kml.py"
    assert script.is_file(), f"missing entry: {script}"


def test_sink_has_five_version_directories(sink_all_versions: Path):
    """After pytest, data/sink/ has exactly five version directories (+ files inside)."""
    assert sink_all_versions.resolve() == SINK_ROOT.resolve()
    version_dirs = {p.name for p in sink_all_versions.iterdir() if p.is_dir()}
    assert version_dirs == set(ALL_VERSION_DIRS), (
        f"sink must contain only the five version dirs; got: {sorted(version_dirs)}"
    )
    assert not (sink_all_versions / "map").exists(), "legacy path data/sink/map must not exist"
    for version in ALL_VERSION_DIRS:
        out = sink_all_versions / version
        assert out.is_dir(), f"missing sink directory: {out}"
        expected = load_manifest(version)
        missing = [rel for rel in expected["files"] if not (out / rel).is_file()]
        assert not missing, f"{version} missing {len(missing)} files, e.g. {missing[:3]}"


@pytest.mark.parametrize("version", ALL_VERSION_DIRS)
def test_generate_matches_golden_manifest(version: str, sink_all_versions: Path):
    out_dir = sink_version_dir(sink_all_versions, version)
    generated = build_manifest(out_dir)
    expected = load_manifest(version)

    missing = set(expected["files"]) - set(generated["files"])
    extra = set(generated["files"]) - set(expected["files"])
    assert not missing, f"{version} missing: {sorted(missing)[:8]}"
    assert not extra, f"{version} extra: {sorted(extra)[:8]}"

    mismatches = [
        rel
        for rel, exp in expected["files"].items()
        if generated["files"][rel] != exp
    ]
    assert not mismatches, f"{version} structure mismatch: {mismatches[:5]}"


def test_v70_only_legacy_merged_json(sink_all_versions: Path):
    out = sink_version_dir(sink_all_versions, "农业基地_v7.0_GCJ02_Polygon")
    jsons = {p.name for p in out.glob("*.json")}
    assert jsons == {
        "农业基地_GCJ02_BS.json",
        "农业基地_GCJ02_CS.json",
        "农业基地_GCJ02_WS.json",
        "农业基地_GCJ02_YY.json",
    }
    assert not (out / "农业基地").exists()


def test_v70_youyang_legacy_has_districts(sink_all_versions: Path):
    import json

    out = sink_version_dir(sink_all_versions, "农业基地_v7.0_GCJ02_Polygon")
    data = json.loads((out / "农业基地_GCJ02_YY.json").read_text(encoding="utf-8"))
    assert len(data["features"]) == 7


def test_v71_only_flat_eight_files(sink_all_versions: Path):
    out = sink_version_dir(sink_all_versions, "农业基地_v7.1_GCJ02_MultiPolygon")
    names = sorted(p.name for p in out.glob("农业基地_GCJ02_*.json"))
    assert len(names) == 8
    assert all(n.endswith("-area.json") or n.endswith("-point.json") for n in names)
    assert not any(
        n.endswith(".json") and "-area" not in n and "-point" not in n for n in names
    )
    assert not (out / "农业基地").exists()


def test_v74_no_legacy_merged(sink_all_versions: Path):
    out = sink_version_dir(sink_all_versions, "农业基地_v7.4_GCJ02_L3_SingleMap")
    assert list(out.glob("农业基地_GCJ02_*.json")) == []


@pytest.mark.parametrize(
    "version,flag",
    [
        ("农业基地_v7.0_GCJ02_Polygon", "write_legacy_merged"),
        ("农业基地_v7.1_GCJ02_MultiPolygon", "write_l1_flat_per_base"),
        ("农业基地_v7.2_GCJ02_MP_L2", "write_layered_l1_l2_l3"),
        ("农业基地_v7.3_GCJ02_L3", "write_layered_l1_l2_l3"),
        ("农业基地_v7.4_GCJ02_L3_SingleMap", "write_layered_l1_l2_l3"),
    ],
)
def test_profile_flags(version: str, flag: str):
    profile = get_profile(version)
    assert getattr(profile, flag) is True
