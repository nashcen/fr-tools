"""TC-KML-* KML parsing."""

from __future__ import annotations

from pathlib import Path

import pytest

from lib.geojson import kml_parser

REPO = Path(__file__).resolve().parents[1]
EAST_KML = (
    REPO
    / "data"
    / "source"
    / "1.农业基地KML"
    / "1.常山地图KML"
    / "东区_KML导出_20260602125704.kml"
)


@pytest.fixture(scope="module")
def east_placemarks():
    if not EAST_KML.is_file():
        pytest.skip(f"missing KML: {EAST_KML}")
    return kml_parser.parse_kml(str(EAST_KML))


def test_parse_changshan_east(east_placemarks):
    assert len(east_placemarks) > 100
    sample = east_placemarks[0]
    assert "coords" in sample
    assert len(sample["coords"]) >= 3


def test_should_keep_discards_seed_and_colors(east_placemarks):
    kept = [p for p in east_placemarks if kml_parser.should_keep(p)]
    assert len(kept) < len(east_placemarks)
    for pm in kept:
        assert not pm["is_seed"] or "测绘" in " ".join(pm["path"])


def test_survey_folder_kept_despite_color(east_placemarks):
    survey = [
        p
        for p in east_placemarks
        if "测绘" in " ".join(p["path"]) and p["color"] in ("#ffbb00", "#19be6b")
    ]
    if not survey:
        pytest.skip("no colored survey polygons in sample KML")
    assert any(kml_parser.should_keep(p) for p in survey)
