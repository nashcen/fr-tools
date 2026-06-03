#!/usr/bin/env python3
"""
【版本入口 农业基地_v7.1_GCJ02_MultiPolygon — 封板；实现见 lib/geojson】
扁平 L1：仅 农业基地_GCJ02_{CS,WS,BS,YY}-area.json / -point.json
"""

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_SCRIPTS.parent))
sys.path.insert(0, str(_SCRIPTS))
from lib.version_entry import run

if __name__ == "__main__":
    raise SystemExit(run("农业基地_v7.1_GCJ02_MultiPolygon"))
