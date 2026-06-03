"""Launch geojson generation for a fixed version directory name."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def run(version_dir: str) -> int:
    scripts_dir = Path(__file__).resolve().parent.parent
    repo_root = scripts_dir.parent
    sys.path[:0] = [str(repo_root), str(scripts_dir)]
    os.environ.setdefault("GEOJSON_VERSION", version_dir)
    from lib.geojson.cli import main

    return main(["--version", version_dir])
