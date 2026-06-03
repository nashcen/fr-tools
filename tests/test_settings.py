"""TC-CFG-* configuration and security."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def test_mysql_config_requires_password(monkeypatch):
    monkeypatch.setenv("MYSQL_PASSWORD", "")
    monkeypatch.setattr("lib.settings._load_dotenv", lambda: None)
    from lib import settings

    settings._boot.cache_clear()
    with pytest.raises(RuntimeError, match="MYSQL_PASSWORD"):
        settings.mysql_config()
    settings._boot.cache_clear()


def test_default_data_paths(monkeypatch):
    monkeypatch.setenv("FR_TOOLS_REPO", str(REPO))
    from lib import settings

    settings._boot.cache_clear()
    assert settings.kml_dir() == REPO / "data" / "source" / "1.农业基地KML"
    assert settings.excel_path() == REPO / "data" / "source" / "农业资产盘点明细.xlsx"
    settings._boot.cache_clear()


def test_geojson_output_dir_override(monkeypatch, tmp_path):
    monkeypatch.setenv("GEOJSON_OUTPUT_DIR", str(tmp_path / "custom-out"))
    from lib import settings

    settings._boot.cache_clear()
    assert settings.geojson_output_dir() == (tmp_path / "custom-out").resolve()
    settings._boot.cache_clear()


def test_no_hardcoded_mysql_password_in_scripts():
    """TC-CFG-02: scripts must not contain known production password literal."""
    needle = "yxgbigdata@YXG321"
    hits = []
    for path in (REPO / "scripts").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if needle in text:
            hits.append(str(path.relative_to(REPO)))
    assert hits == [], f"hardcoded password in: {hits}"
