"""TC-GEO-03..07 GeoJSON structure conventions after generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.conftest import VERSION
from tests.test_geojson_generate import _run_generate

ALLOWED_AREA_TYPES = {"Polygon", "MultiPolygon"}
ALLOWED_POINT_TYPES = {"Point", None}


def _load_fc(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture(scope="module")
def generated_tree(tmp_path_factory):
    out = tmp_path_factory.mktemp("geo_conv") / "generated"
    out.mkdir()
    import os

    os.environ["FR_TOOLS_REPO"] = str(Path(__file__).resolve().parents[1])
    os.environ["GEOJSON_VERSION"] = VERSION
    os.environ["GEOJSON_OUTPUT_DIR"] = str(out)
    os.environ["GEOJSON_SKIP_DB"] = "1"
    os.environ["GEOJSON_SKIP_DB_UPDATE"] = "1"
    os.environ["GEOJSON_PROTECT_EXISTING"] = "0"
    os.environ["MYSQL_PASSWORD"] = "test"
    os.environ["GEOJSON_WGS84_SUBDIR"] = str(out.parent / "wgs84")
    _run_generate()
    return out


def test_l1_base_feature_count(generated_tree):
    data = _load_fc(generated_tree / "农业基地-area.json")
    assert len(data["features"]) == 3
    names = {f["properties"]["name"] for f in data["features"]}
    assert names == {"浙江常山", "四川武胜", "广西百色"}


def test_changshan_l2_district_count(generated_tree):
    data = _load_fc(generated_tree / "农业基地" / "浙江常山-area.json")
    assert len(data["features"]) == 24


def test_wusheng_longxing_l3_plot_count(generated_tree):
    path = generated_tree / "农业基地" / "四川武胜" / "龙兴-area.json"
    assert path.is_file()
    data = _load_fc(path)
    assert len(data["features"]) == 12


def test_all_area_files_polygon_only(generated_tree):
    violations = []
    for path in generated_tree.rglob("*-area.json"):
        for feat in _load_fc(path).get("features", []):
            gtype = (feat.get("geometry") or {}).get("type")
            if gtype not in ALLOWED_AREA_TYPES:
                violations.append((path.name, gtype))
    assert not violations, violations[:5]


def test_point_files_point_or_null_geometry(generated_tree):
    violations = []
    for path in generated_tree.rglob("*-point.json"):
        for feat in _load_fc(path).get("features", []):
            geom = feat.get("geometry")
            gtype = geom.get("type") if geom else None
            if gtype not in ALLOWED_POINT_TYPES:
                violations.append((path.name, gtype))
    assert not violations, violations[:5]
