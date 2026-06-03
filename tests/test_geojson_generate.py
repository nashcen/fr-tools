"""Verify generated GeoJSON tree matches golden structure manifest."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.conftest import DEFAULT_VERSION, load_manifest, sink_version_dir
from tests.tools.build_geojson_manifest import build_manifest


def test_generate_matches_golden_manifest(sink_all_versions: Path):
    out_dir = sink_version_dir(sink_all_versions, DEFAULT_VERSION)
    generated = build_manifest(out_dir)
    expected = load_manifest(DEFAULT_VERSION)
    assert generated["files"], "generator produced no files"

    missing = set(expected["files"]) - set(generated["files"])
    extra = set(generated["files"]) - set(expected["files"])
    assert not missing, f"missing outputs: {sorted(missing)[:5]}"
    assert not extra, f"unexpected outputs: {sorted(extra)[:5]}"

    mismatches = []
    for rel, exp in expected["files"].items():
        got = generated["files"][rel]
        if got != exp:
            mismatches.append((rel, exp, got))
    assert not mismatches, _format_mismatch(mismatches[:3])


def _format_mismatch(items: list) -> str:
    lines = ["structure mismatch (showing up to 3):"]
    for rel, exp, got in items:
        lines.append(f"  {rel}")
        lines.append(f"    expected: {exp}")
        lines.append(f"    got:      {got}")
    return "\n".join(lines)


def test_protect_existing_skips_writes(geojson_out_dir: Path, monkeypatch):
    target = geojson_out_dir / "农业基地-area.json"
    target.write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")
    monkeypatch.setenv("GEOJSON_PROTECT_EXISTING", "1")
    import os

    os.environ["GEOJSON_VERSION"] = DEFAULT_VERSION
    os.environ["GEOJSON_OUTPUT_DIR"] = str(geojson_out_dir)
    from lib.geojson.cli import main

    assert main(["--version", DEFAULT_VERSION]) == 0
    with target.open(encoding="utf-8") as handle:
        assert json.load(handle)["features"] == []
