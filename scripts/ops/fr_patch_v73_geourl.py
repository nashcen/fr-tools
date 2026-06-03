#!/usr/bin/env python3
"""
修复 Agriculture_v7.3_GCJ02_L3.fvs 中四张区域地图的 geourl。

问题：仍指向已废弃的
  assets/map/geographic/world/农业基地-大疆测绘/农业基地_v3_GCJ02/农业基地_GCJ02_XX.json

修复：对齐 v7.3 L3 GeoJSON 目录（L2 绑基地，L3 地块在子目录），与 v7.2 大屏四图一致：
  assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/农业基地/{基地名}-area.json
"""

from __future__ import annotations

import os
import shutil
import zipfile
from datetime import datetime

FVS_PATH = (
    "/Applications/FineReport/webapps/webroot/WEB-INF/reportlets/"
    "YXG-项目/5.农业大屏二期/Agriculture_v7.3_GCJ02_L3.fvs"
)

REPLACEMENTS = {
    "assets/map/geographic/world/农业基地-大疆测绘/农业基地_v3_GCJ02/农业基地_GCJ02_CS.json": (
        "assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/农业基地/浙江常山-area.json"
    ),
    "assets/map/geographic/world/农业基地-大疆测绘/农业基地_v3_GCJ02/农业基地_GCJ02_WS.json": (
        "assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/农业基地/四川武胜-area.json"
    ),
    "assets/map/geographic/world/农业基地-大疆测绘/农业基地_v3_GCJ02/农业基地_GCJ02_BS.json": (
        "assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/农业基地/广西百色-area.json"
    ),
    "assets/map/geographic/world/农业基地-大疆测绘/农业基地_v3_GCJ02/农业基地_GCJ02_YY.json": (
        "assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/农业基地/重庆酉阳-area.json"
    ),
}


def patch_text(text: str) -> tuple[str, int]:
    n = 0
    for old, new in REPLACEMENTS.items():
        c = text.count(old)
        if c:
            text = text.replace(old, new)
            n += c
    return text, n


def main() -> None:
    if not os.path.isfile(FVS_PATH):
        raise SystemExit(f"FVS not found: {FVS_PATH}")

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup = f"{FVS_PATH}.bak-{stamp}"
    shutil.copy2(FVS_PATH, backup)
    print(f"backup: {backup}")

    tmp = f"{FVS_PATH}.patch-tmp"
    total = 0
    with zipfile.ZipFile(FVS_PATH, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.endswith((".chart", "store.json", "editor.tpl")):
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    zout.writestr(info, data)
                    continue
                new_text, n = patch_text(text)
                if n:
                    print(f"  {info.filename}: {n} replacement(s)")
                    total += n
                    data = new_text.encode("utf-8")
            zout.writestr(info, data)

    if total == 0:
        os.remove(tmp)
        raise SystemExit("no geourl patterns replaced — already patched?")

    os.replace(tmp, FVS_PATH)
    print(f"done: {total} replacement(s) in {FVS_PATH}")


if __name__ == "__main__":
    main()
