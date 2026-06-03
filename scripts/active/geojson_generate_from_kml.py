#!/usr/bin/env python3
"""
【活跃开发 active/ — 日常只改 lib/geojson，本文件为入口】
从 KML 生成农业基地 GeoJSON。配置见仓库根目录 .env（模板 .env.example）。

默认版本：GEOJSON_VERSION=农业基地_v7.4_GCJ02_L3_SingleMap

用法：
  python3 scripts/active/geojson_generate_from_kml.py
  python3 scripts/active/geojson_generate_from_kml.py --version 农业基地_v7.3_GCJ02_L3
  GEOJSON_OUTPUT_DIR=/tmp/geo-out GEOJSON_PROTECT_EXISTING=0 python3 ...
"""

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
_REPO = _SCRIPTS.parent
sys.path[:0] = [str(_REPO), str(_SCRIPTS)]

from lib.geojson.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
