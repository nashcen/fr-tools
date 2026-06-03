#!/usr/bin/env python3
"""
Build tests/golden/geojson/{version}/manifest.json from an existing GeoJSON tree (read-only).

Example (read production v7.4 without modifying files):
  python3 tests/tools/build_geojson_manifest.py \\
    --source "/Applications/FineReport/.../农业基地_v7.4_GCJ02_L3_SingleMap" \\
    --version 农业基地_v7.4_GCJ02_L3_SingleMap
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _structure_digest(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    features = data.get("features", [])
    names = sorted(
        f.get("properties", {}).get("name", "") for f in features if f.get("properties")
    )
    geom_types = sorted(
        {f.get("geometry", {}).get("type", "") for f in features if f.get("geometry")}
    )
    coord_points = 0
    for feat in features:
        geom = feat.get("geometry") or {}
        gtype = geom.get("type")
        coords = geom.get("coordinates")
        if gtype == "Point" and coords:
            coord_points += 1
        elif gtype == "Polygon" and coords:
            coord_points += sum(len(ring) for ring in coords)
        elif gtype == "MultiPolygon" and coords:
            for poly in coords:
                coord_points += sum(len(ring) for ring in poly)
    payload = json.dumps(
        {
            "feature_count": len(features),
            "geometry_types": geom_types,
            "names": names,
            "coord_points": coord_points,
            "collection_name": data.get("name"),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return {
        "feature_count": len(features),
        "geometry_types": geom_types,
        "coord_points": coord_points,
        "structure_sha256": hashlib.sha256(payload.encode()).hexdigest(),
    }


def build_manifest(source: Path) -> dict:
    files: dict[str, dict] = {}
    for path in sorted(source.rglob("*.json")):
        rel = path.relative_to(source).as_posix()
        files[rel] = _structure_digest(path)
    return {"version_dir": source.name, "files": files}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "golden" / "geojson",
    )
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    if not source.is_dir():
        raise SystemExit(f"source not found: {source}")

    manifest = build_manifest(source)
    dest = args.out / args.version / "manifest.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
    print(f"Wrote {dest} ({len(manifest['files'])} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
