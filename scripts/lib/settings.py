"""
Load configuration from environment / .env at repository root.
No secrets or machine-specific paths in source code.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

# 与 FineReport / geourl 一致的地图资源根名
MAP_COLLECTION_NAME = "农业基地-大疆测绘"


def repo_root() -> Path:
    return Path(os.environ.get("FR_TOOLS_REPO", _REPO_ROOT)).resolve()


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = repo_root() / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


@lru_cache(maxsize=1)
def _boot() -> None:
    _load_dotenv()


def data_source_dir() -> Path:
    _boot()
    raw = os.environ.get("DATA_SOURCE_DIR")
    if raw:
        return Path(raw).expanduser().resolve()
    return repo_root() / "data" / "source"


def data_sink_map_root() -> Path:
    _boot()
    raw = os.environ.get("DATA_SINK_MAP_ROOT")
    if raw:
        return Path(raw).expanduser().resolve()
    return repo_root() / "data" / "sink" / "map" / MAP_COLLECTION_NAME


def kml_dir() -> Path:
    _boot()
    raw = os.environ.get("KML_DIR")
    if raw:
        return Path(raw).expanduser().resolve()
    return data_source_dir() / "1.农业基地KML"


def excel_path() -> Path:
    _boot()
    raw = os.environ.get("EXCEL_PATH")
    if raw:
        return Path(raw).expanduser().resolve()
    return data_source_dir() / "农业资产盘点明细.xlsx"


def finereport_webinf() -> Path:
    _boot()
    return Path(
        os.environ.get(
            "FINEREPORT_WEBINF",
            "/Applications/FineReport/webapps/webroot/WEB-INF",
        )
    ).expanduser().resolve()


def finereport_geojson_map_root() -> Path:
    """FineReport 部署目录（同步 sink 目标，非生成默认输出）。"""
    _boot()
    sub = os.environ.get(
        "GEOJSON_MAP_SUBDIR",
        f"assets/map/geographic/{MAP_COLLECTION_NAME}",
    )
    return finereport_webinf() / sub


def geojson_wgs84_dir() -> Path:
    _boot()
    raw = os.environ.get("GEOJSON_WGS84_DIR")
    if raw:
        return Path(raw).expanduser().resolve()
    return data_sink_map_root() / "农业基地_v2_WGS84"


def geojson_version_name() -> str:
    _boot()
    return os.environ.get("GEOJSON_VERSION", "农业基地_v7.4_GCJ02_L3_SingleMap")


def geojson_output_dir(version: str | None = None) -> Path:
    """生成输出目录：默认 data/sink/map/农业基地-大疆测绘/{版本}。"""
    _boot()
    override = os.environ.get("GEOJSON_OUTPUT_DIR")
    if override:
        return Path(override).expanduser().resolve()
    name = version or geojson_version_name()
    return data_sink_map_root() / name


def skip_db() -> bool:
    _boot()
    return _env_bool("GEOJSON_SKIP_DB", False)


def skip_db_update() -> bool:
    _boot()
    if skip_db():
        return True
    return _env_bool("GEOJSON_SKIP_DB_UPDATE", False)


def protect_existing_geojson() -> bool:
    _boot()
    return _env_bool("GEOJSON_PROTECT_EXISTING", True)


FROZEN_GEOJSON_VERSION_DIRS: frozenset[str] = frozenset(
    {
        "农业基地_v6.0_TEST",
        "农业基地_v7.0_GCJ02_Polygon",
        "农业基地_v7.1_GCJ02_MultiPolygon",
        "农业基地_v7.2_GCJ02_MP_L2",
        "农业基地_v7.3_GCJ02_L3",
        "农业基地_v7.4_GCJ02_L3_SingleMap",
    }
)


def mysql_config() -> dict[str, str | int]:
    _boot()
    password = os.environ.get("MYSQL_PASSWORD", "")
    if not password:
        raise RuntimeError(
            "MYSQL_PASSWORD is not set. Copy .env.example to .env and configure MySQL."
        )
    return {
        "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", "bigdata"),
        "password": password,
        "database": os.environ.get("MYSQL_DATABASE", "yxg_bigscreen"),
    }


# 兼容旧代码引用
def geojson_map_root() -> Path:
    return data_sink_map_root()
