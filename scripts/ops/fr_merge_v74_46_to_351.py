#!/usr/bin/env python3
"""
仅修改 v7.4 FVS 中 **区域地图 chart 的 geourl**（GeoJSON 路径），不改动 store / 交互 / 预警 / 下拉框。

从服务器 3.5.1 稿恢复并打补丁:
  python3 scripts/ops/fr_merge_v74_46_to_351.py --restore-backup

对当前文件只改 geourl（store 不动）:
  python3 scripts/ops/fr_merge_v74_46_to_351.py
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(_SCRIPTS.parent), str(_SCRIPTS)]

from lib.fr_paths import fvs_path

TARGET = fvs_path("Agriculture_v7.4_GCJ02_L3_SingleMap.fvs")

GEOURL_L1 = (
    "assets/map/geographic/农业基地-大疆测绘/"
    "农业基地_v7.4_GCJ02_L3_SingleMap/农业基地-area.json"
)
GEOURL_WRONG = (
    "assets/map/geographic/农业基地-大疆测绘/"
    "农业基地_v7.4_GCJ02_L3_SingleMap/农业基地.json"
)


def patch_geourl_chart(text: str) -> tuple[str, int]:
    if GEOURL_L1 in text:
        return text, 0
    old = f'geourl="{GEOURL_WRONG}"'
    new = f'geourl="{GEOURL_L1}"'
    if old in text:
        return text.replace(old, new, 1), 1
    text2, c = re.subn(
        r'geourl="[^"]*农业基地_v7\.4_GCJ02_L3_SingleMap/[^"]*"',
        f'geourl="{GEOURL_L1}"',
        text,
        count=1,
    )
    return text2, c


def latest_backup() -> Path | None:
    candidates = sorted(
        TARGET.parent.glob(f"{TARGET.name}.bak-merge-*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    # 优先最早一次合并前的备份（widgets=249 的服务器稿）
    for p in reversed(candidates):
        try:
            import json

            with zipfile.ZipFile(p) as z:
                s = json.loads(z.read("store.json"))
                if len(s["stories"][0]["widgets"]) <= 250:
                    return p
        except Exception:
            continue
    return candidates[0] if candidates else None


def patch_fvs_only_geourl(*, restore_backup: bool) -> None:
    if not TARGET.is_file():
        raise SystemExit(f"target missing: {TARGET}")

    if restore_backup:
        bak = latest_backup()
        if not bak:
            raise SystemExit("no suitable .bak-merge-* (server 3.5.1) backup")
        shutil.copy2(bak, TARGET)
        print(f"restored: {bak}")

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup = TARGET.with_suffix(f".fvs.bak-geourl-{stamp}")
    shutil.copy2(TARGET, backup)
    print(f"backup: {backup}")

    tmp = TARGET.with_suffix(".fvs.geourl-tmp")
    chart_patches = 0
    with zipfile.ZipFile(TARGET, "r") as zin, zipfile.ZipFile(
        tmp, "w", zipfile.ZIP_DEFLATED
    ) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            name = info.filename
            if name.startswith("__temp__copy__/"):
                continue
            if name.endswith(".chart"):
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    zout.writestr(info, data)
                    continue
                text, n = patch_geourl_chart(text)
                if n:
                    chart_patches += n
                    print(f"  geourl patched: {name}")
                    data = text.encode("utf-8")
            zout.writestr(info, data)

    if chart_patches == 0:
        import os

        os.remove(tmp)
        print("no geourl change (already 农业基地-area.json?)")
        return

    __import__("os").replace(tmp, TARGET)
    print(f"done: {TARGET} ({chart_patches} chart file(s), store untouched)")


def main() -> None:
    ap = argparse.ArgumentParser(description="v7.4 FVS geourl-only patch")
    ap.add_argument(
        "--restore-backup",
        action="store_true",
        help="先恢复合并前的服务器 3.5.1 稿，再只改 geourl",
    )
    args = ap.parse_args()
    patch_fvs_only_geourl(restore_backup=args.restore_backup)


if __name__ == "__main__":
    main()
