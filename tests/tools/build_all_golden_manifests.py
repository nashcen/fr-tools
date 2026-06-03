#!/usr/bin/env python3
"""Generate golden manifests for v7.0–v7.4 from offline KML generation."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
sys.path[:0] = [str(REPO), str(SCRIPTS)]

from lib.geojson.cli import main
from lib.geojson.profiles import ALL_VERSION_DIRS
from tests.tools.build_geojson_manifest import build_manifest


def main_cli() -> int:
    golden_root = REPO / "tests" / "golden" / "geojson"
    os.environ["FR_TOOLS_REPO"] = str(REPO)
    os.environ["GEOJSON_SKIP_DB"] = "1"
    os.environ["GEOJSON_SKIP_DB_UPDATE"] = "1"
    os.environ["GEOJSON_PROTECT_EXISTING"] = "0"
    os.environ["MYSQL_PASSWORD"] = "x"
    os.environ["GEOJSON_WGS84_SUBDIR"] = str(REPO / "tests" / ".tmp_wgs84")

    for version in ALL_VERSION_DIRS:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            out.mkdir()
            os.environ["GEOJSON_OUTPUT_DIR"] = str(out)
            os.environ["GEOJSON_VERSION"] = version
            print(f"Generating {version}...")
            if main(["--version", version]) != 0:
                return 1
            manifest = build_manifest(out)
            dest = golden_root / version / "manifest.json"
            dest.parent.mkdir(parents=True, exist_ok=True)
            import json

            with dest.open("w", encoding="utf-8") as handle:
                json.dump(manifest, handle, ensure_ascii=False, indent=2)
            print(f"  → {dest} ({len(manifest['files'])} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main_cli())
