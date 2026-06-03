"""GeoJSON file writer with optional protection for existing frozen files."""

from __future__ import annotations

import json
import os
from pathlib import Path

from lib import settings


def _may_write(path: Path) -> bool:
    if not path.exists():
        return True
    if not settings.protect_existing_geojson():
        return True
    print(f"  ⊘ 跳过（已有文件，GEOJSON_PROTECT_EXISTING=1）: {path.name}")
    return False


def write_geojson(
    path: str | Path,
    features: list,
    *,
    top_name: str | None = None,
) -> bool:
    target = Path(path)
    if not _may_write(target):
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    collection = {"type": "FeatureCollection", "features": features}
    if top_name:
        collection["name"] = top_name
    with target.open("w", encoding="utf-8") as handle:
        json.dump(collection, handle, ensure_ascii=False)
    print(f"  → {target.name}: {len(features)} features")
    return True


def v3_area_feature(feature: dict) -> dict:
    props = feature["properties"]
    return {
        "type": "Feature",
        "properties": {"name": props["name"], "center": props["center"]},
        "geometry": feature["geometry"],
    }


def v3_point_feature(feature: dict) -> dict | None:
    center = feature["properties"].get("center")
    return {
        "type": "Feature",
        "properties": {"name": feature["properties"]["name"], "center": center},
        "geometry": {"type": "Point", "coordinates": center} if center else None,
    }


def mk_area_feature(name: str, center, geometry: dict) -> dict:
    return {
        "type": "Feature",
        "properties": {"name": name, "center": center},
        "geometry": geometry,
    }


def mk_point_feature(name: str, center) -> dict | None:
    if not center:
        return None
    return {
        "type": "Feature",
        "properties": {"name": name},
        "geometry": {"type": "Point", "coordinates": center},
    }
