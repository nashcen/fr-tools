"""Verify generated GeoJSON tree matches golden structure manifest."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tests.conftest import GOLDEN_ROOT, VERSION, load_manifest
from tests.tools.build_geojson_manifest import build_manifest

REPO = Path(__file__).resolve().parents[1]


def _run_generate() -> None:
    os.environ.setdefault("FR_TOOLS_REPO", str(REPO))
    from lib.geojson.cli import main

    assert main(["--version", VERSION]) == 0


def test_generate_matches_golden_manifest(geojson_out_dir: Path):
    _run_generate()
    generated = build_manifest(geojson_out_dir)
    expected = load_manifest(VERSION)
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
    _run_generate()
    with target.open(encoding="utf-8") as handle:
        assert json.load(handle)["features"] == []
