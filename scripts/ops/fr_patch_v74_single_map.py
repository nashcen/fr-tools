#!/usr/bin/env python3
"""
完成 Agriculture_v7.4_GCJ02_L3_SingleMap.fvs 单图配置：

1. 主图 geourl → v7.4 L1：农业基地-area.json（三层下钻入口）
2. store.json / editor.tpl：去掉四图 setVisible，统一 getWidgetByName(\"区域地图\")
3. 树视图 / 基地切换：panTo 等均指向单组件「区域地图」
"""

from __future__ import annotations

import os
import re
import shutil
import zipfile
from datetime import datetime

FVS_PATH = (
    "/Applications/FineReport/webapps/webroot/WEB-INF/reportlets/"
    "YXG-项目/5.农业大屏二期/Agriculture_v7.4_GCJ02_L3_SingleMap.fvs"
)

CHART_MAIN = "bf4df8fc-b8bf-4855-8bf0-778a72e46bff.chart"

GEOURL_L1 = (
    "assets/map/geographic/农业基地-大疆测绘/"
    "农业基地_v7.4_GCJ02_L3_SingleMap/农业基地-area.json"
)

# 旧 geourl 前缀（v7.3 L2 等）→ 统一改为 v7.4 L1
GEOURL_OLD_PATTERNS = [
    re.compile(
        r'geourl="assets/map/geographic/农业基地-大疆测绘/'
        r'农业基地_v7\.3_GCJ02_L3/[^"]+"'
    ),
    re.compile(
        r'geourl="assets/map/geographic/world/农业基地-大疆测绘/'
        r'农业基地_v3_GCJ02/[^"]+"'
    ),
]

MAP_SETVISIBLE = re.compile(
    r'duchamp\.getWidgetByName\(\\"区域地图_(?:CS|WS|BS|YY)\\"\)'
    r'\.setVisible\((?:true|false)\);\n?'
)
MAP_WIDGET_OLD = re.compile(
    r'duchamp\.getWidgetByName\(\\"区域地图_(?:CS|WS|BS|YY)\\"\)'
)
MAP_WIDGET_NEW = r'duchamp.getWidgetByName(\\"区域地图\\")'


def patch_geourl_in_chart(text: str, force_l1: bool) -> tuple[str, int]:
    n = 0
    for pat in GEOURL_OLD_PATTERNS:
        text, c = pat.subn(f'geourl="{GEOURL_L1}"', text)
        n += c
    if force_l1 and f'geourl="{GEOURL_L1}"' not in text:
        text2, c = re.subn(
            r'geourl="[^"]*农业基地[^"]*"',
            f'geourl="{GEOURL_L1}"',
            text,
            count=1,
        )
        if c:
            text = text2
            n += c
    return text, n


def patch_store_text(text: str) -> tuple[str, int]:
    n = 0
    text2, c1 = MAP_SETVISIBLE.subn("", text)
    n += c1
    text3, c2 = MAP_WIDGET_OLD.subn(MAP_WIDGET_NEW, text2)
    n += c2
    return text3, n


def patch_fvs() -> None:
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
            if not info.filename.endswith((".chart", "store.json", "editor.tpl")):
                zout.writestr(info, data)
                continue
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                zout.writestr(info, data)
                continue

            n = 0
            if info.filename.endswith(".chart"):
                force = info.filename == CHART_MAIN
                text, n = patch_geourl_in_chart(text, force_l1=force)
            elif info.filename in ("store.json", "editor.tpl"):
                text, n = patch_store_text(text)

            if n:
                print(f"  {info.filename}: {n} change(s)")
                total += n
                data = text.encode("utf-8")
            zout.writestr(info, data)

    if total == 0:
        os.remove(tmp)
        raise SystemExit("no changes applied — already patched?")

    os.replace(tmp, FVS_PATH)
    print(f"done: {total} change(s) in {FVS_PATH}")
    print(f"geourl (L1): {GEOURL_L1}")


def main() -> None:
    patch_fvs()


if __name__ == "__main__":
    main()
