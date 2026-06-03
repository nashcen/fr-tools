"""FineReport WEB-INF path helpers."""

from __future__ import annotations

from pathlib import Path

from lib import settings


def reportlets_dir() -> Path:
    return settings.finereport_webinf() / "reportlets"


def bigscreen_phase2_dir() -> Path:
    return reportlets_dir() / "YXG-项目" / "5.农业大屏二期"


def fvs_path(filename: str) -> Path:
    return bigscreen_phase2_dir() / filename


def geojson_asset_path(version_dir: str, *parts: str) -> str:
    """Relative geourl under WEB-INF (no leading slash)."""
    base = settings.geojson_map_root() / version_dir
    return str(Path("assets/map/geographic/农业基地-大疆测绘") / version_dir / Path(*parts))
