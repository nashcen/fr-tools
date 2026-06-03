#!/usr/bin/env python3
"""
【版本入口 农业基地_v7.4_GCJ02_L3_SingleMap — 封板；实现见 lib/geojson】
"""

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_SCRIPTS.parent))
sys.path.insert(0, str(_SCRIPTS))
from lib.version_entry import run

_VERSION = "农业基地_v7.4_GCJ02_L3_SingleMap"

if __name__ == "__main__":
    raise SystemExit(run(_VERSION))
