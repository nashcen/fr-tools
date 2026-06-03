#!/usr/bin/env python3
"""
【版本入口 农业基地_v7.3_GCJ02_L3 — 封板四图；实现见 lib/geojson】
"""

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_SCRIPTS.parent))
sys.path.insert(0, str(_SCRIPTS))
from lib.version_entry import run

if __name__ == "__main__":
    raise SystemExit(run("农业基地_v7.3_GCJ02_L3"))
