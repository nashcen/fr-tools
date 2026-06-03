"""TC-DATA-* source/sink layout (SDD data-layout_delta)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def test_source_kml_exists():
    kml = REPO / "data" / "source" / "1.农业基地KML"
    assert kml.is_dir()
    assert list(kml.rglob("*.kml")), "expected KML under data/source"


def test_source_excel_exists():
    xlsx = REPO / "data" / "source" / "农业资产盘点明细.xlsx"
    assert xlsx.is_file()


def test_sink_map_root_exists():
    root = REPO / "data" / "sink" / "map" / "农业基地-大疆测绘"
    assert root.is_dir()


def test_settings_default_paths(monkeypatch):
    monkeypatch.setenv("FR_TOOLS_REPO", str(REPO))
    monkeypatch.setattr("lib.settings._load_dotenv", lambda: None)
    from lib import settings

    settings._boot.cache_clear()
    assert settings.kml_dir() == REPO / "data" / "source" / "1.农业基地KML"
    assert settings.excel_path() == REPO / "data" / "source" / "农业资产盘点明细.xlsx"
    assert settings.data_sink_map_root() == REPO / "data" / "sink" / "map" / "农业基地-大疆测绘"
    v = "农业基地_v7.4_GCJ02_L3_SingleMap"
    assert settings.geojson_output_dir(v) == settings.data_sink_map_root() / v
    assert settings.geojson_wgs84_dir() == settings.data_sink_map_root() / "农业基地_v2_WGS84"
    settings._boot.cache_clear()
