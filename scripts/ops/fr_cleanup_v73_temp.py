#!/usr/bin/env python3
"""清理 v7.3 / v7.4 GeoJSON 目录中的 .DS_Store，以及 v7.3 FVS 备份文件。"""

from __future__ import annotations

import os
import glob

REPORTLETS = (
    "/Applications/FineReport/webapps/webroot/WEB-INF/reportlets/"
    "YXG-项目/5.农业大屏二期"
)
GEO_ROOT = (
    "/Applications/FineReport/webapps/webroot/WEB-INF/assets/map/geographic/"
    "农业基地-大疆测绘"
)
GEO_DIRS = [
    "农业基地_v7.3_GCJ02_L3",
    "农业基地_v7.4_GCJ02_L3_SingleMap",
]


def main() -> None:
    removed: list[str] = []

    for pattern in [
        os.path.join(REPORTLETS, "Agriculture_v7.3*.bak*"),
        os.path.join(REPORTLETS, "Agriculture_v7.3*.deprecated*"),
        *[os.path.join(GEO_ROOT, d, "**/.DS_Store") for d in GEO_DIRS],
    ]:
        for path in glob.glob(pattern, recursive=True):
            if os.path.isfile(path):
                os.remove(path)
                removed.append(path)

    if not removed:
        print("nothing to remove")
        return
    for path in removed:
        print("removed:", path)
    print(f"done: {len(removed)} file(s)")


if __name__ == "__main__":
    main()
