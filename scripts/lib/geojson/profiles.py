"""
Per-version GeoJSON output profiles.
Each FineReport GeoJSON directory has a dedicated entry script under scripts/versions/.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeojsonVersionProfile:
    """Controls which artifacts are written for a deployment directory."""

    version_dir: str
    write_legacy_merged: bool = True
    write_layered_l1_l2_l3: bool = True
    write_v2_wgs84_sidecar: bool = True
    update_db_coordinates: bool = True


VERSION_PROFILES: dict[str, GeojsonVersionProfile] = {
    "农业基地_v7.0_GCJ02_Polygon": GeojsonVersionProfile(
        version_dir="农业基地_v7.0_GCJ02_Polygon",
        write_legacy_merged=True,
        write_layered_l1_l2_l3=True,
    ),
    "农业基地_v7.2_GCJ02_MP_L2": GeojsonVersionProfile(
        version_dir="农业基地_v7.2_GCJ02_MP_L2",
    ),
    "农业基地_v7.3_GCJ02_L3": GeojsonVersionProfile(
        version_dir="农业基地_v7.3_GCJ02_L3",
    ),
    "农业基地_v7.4_GCJ02_L3_SingleMap": GeojsonVersionProfile(
        version_dir="农业基地_v7.4_GCJ02_L3_SingleMap",
        write_legacy_merged=False,
    ),
}


def get_profile(version_dir: str) -> GeojsonVersionProfile:
    if version_dir not in VERSION_PROFILES:
        raise KeyError(
            f"Unknown GEOJSON version {version_dir!r}. "
            f"Known: {', '.join(sorted(VERSION_PROFILES))}"
        )
    return VERSION_PROFILES[version_dir]
