"""CLI entry for GeoJSON generation."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _bootstrap_paths() -> Path:
    scripts_dir = Path(__file__).resolve().parents[2]
    repo_root = scripts_dir.parent
    for entry in (str(repo_root), str(scripts_dir)):
        if entry not in sys.path:
            sys.path.insert(0, entry)
    return repo_root


def main(argv: list[str] | None = None) -> int:
    _bootstrap_paths()
    from lib import settings
    from lib.geojson.generate import generate
    from lib.geojson.profiles import get_profile

    parser = argparse.ArgumentParser(description="从 KML 生成农业基地 GeoJSON")
    parser.add_argument(
        "--version",
        default=None,
        help="GeoJSON 目录名，如 农业基地_v7.4_GCJ02_L3_SingleMap",
    )
    parser.add_argument(
        "--bases",
        default=None,
        help="仅处理指定基地（逗号分隔），如 重庆酉阳",
    )
    args = parser.parse_args(argv)

    version = args.version or settings.geojson_version_name()
    os.environ.setdefault("GEOJSON_VERSION", version)
    if args.bases:
        os.environ["GEOJSON_BASES"] = args.bases

    try:
        profile = get_profile(version)
    except KeyError as exc:
        print(exc, file=sys.stderr)
        return 2

    print("生成农业基地片区 GeoJSON...")
    generate(profile)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
