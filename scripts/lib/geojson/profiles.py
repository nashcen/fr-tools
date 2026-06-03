"""
Per-version GeoJSON output profiles (v7.0–v7.4).
Each version has an entry script under scripts/versions/{version_dir}/.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeojsonVersionProfile:
    """Controls which artifacts are written under data/sink/{version}/."""

    version_dir: str
    write_legacy_merged: bool = False
    write_layered_l1_l2_l3: bool = False
    write_l1_flat_per_base: bool = False
    write_v2_wgs84_sidecar: bool = True
    update_db_coordinates: bool = True


VERSION_PROFILES: dict[str, GeojsonVersionProfile] = {
    # v7.0：仅无后缀合并 json（geourl 用 农业基地_GCJ02_CS.json）
    "农业基地_v7.0_GCJ02_Polygon": GeojsonVersionProfile(
        version_dir="农业基地_v7.0_GCJ02_Polygon",
        write_legacy_merged=True,
        write_v2_wgs84_sidecar=True,
    ),
    # v7.1：仅扁平 L1（8 个 *-area.json / *-point.json，禁止无后缀 .json）
    "农业基地_v7.1_GCJ02_MultiPolygon": GeojsonVersionProfile(
        version_dir="农业基地_v7.1_GCJ02_MultiPolygon",
        write_l1_flat_per_base=True,
        write_v2_wgs84_sidecar=False,
    ),
    # v7.2 / v7.3：legacy 合并 + L1/L2/L3 树
    "农业基地_v7.2_GCJ02_MP_L2": GeojsonVersionProfile(
        version_dir="农业基地_v7.2_GCJ02_MP_L2",
        write_legacy_merged=True,
        write_layered_l1_l2_l3=True,
    ),
    "农业基地_v7.3_GCJ02_L3": GeojsonVersionProfile(
        version_dir="农业基地_v7.3_GCJ02_L3",
        write_legacy_merged=True,
        write_layered_l1_l2_l3=True,
    ),
    # v7.4：L3 树，无 legacy 合并 json
    "农业基地_v7.4_GCJ02_L3_SingleMap": GeojsonVersionProfile(
        version_dir="农业基地_v7.4_GCJ02_L3_SingleMap",
        write_layered_l1_l2_l3=True,
        write_v2_wgs84_sidecar=True,
    ),
}

ALL_VERSION_DIRS: tuple[str, ...] = tuple(VERSION_PROFILES.keys())


def get_profile(version_dir: str) -> GeojsonVersionProfile:
    if version_dir not in VERSION_PROFILES:
        raise KeyError(
            f"Unknown GEOJSON version {version_dir!r}. "
            f"Known: {', '.join(sorted(VERSION_PROFILES))}"
        )
    return VERSION_PROFILES[version_dir]
