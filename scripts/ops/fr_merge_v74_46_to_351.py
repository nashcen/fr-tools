#!/usr/bin/env python3
"""
将 4.6 参考稿的 **geourl** 合并进 3.5.1 正式 FVS，保留服务器稿的片区下拉框与 Tab 交互。

⚠ 不要从 4.6 整段替换 widgetEvents / 不要 hide 下拉框 / 不要追加视图树——
  那是 4.6 设计器里的另一套 UI，会去掉「片区下拉框」并在画布显示对齐辅助线。

用法:
  python3 scripts/ops/fr_merge_v74_46_to_351.py
  python3 scripts/ops/fr_merge_v74_46_to_351.py --restore-backup   # 从最近 .bak-merge-* 恢复后再打 geourl
"""

from __future__ import annotations

import argparse
import html
import json
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
SOURCE_46 = fvs_path("Agriculture_v7.4_GCJ02_L3_SingleMap_4.6.fvs")

GEOURL_L1 = (
    "assets/map/geographic/农业基地-大疆测绘/"
    "农业基地_v7.4_GCJ02_L3_SingleMap/农业基地-area.json"
)

# 基地 Tab：仅在 3.5.1 脚本末尾追加 4.6 的 panTo（保留下拉框 setVisible）
TAB_NAMES = {f"c9-n1-t{i}-t{j}" for i in range(4) for j in range(4)}

# 4.6 各 Tab 固定 panTo（lat, lng 顺序与 4.6 一致）
TAB_PANTO = {
    "c9-n1-t0-t0": [29.0100448191025, 118.515585488198],  # 常山
    "c9-n1-t0-t1": [30.3720862, 106.1657042],  # 武胜
    "c9-n1-t0-t2": [24.2106567, 106.1106057],  # 酉阳
    "c9-n1-t0-t3": [28.9141381, 108.910525],  # 百色
    "c9-n1-t1-t0": [29.0100448191025, 118.515585488198],
    "c9-n1-t1-t1": [30.3720862, 106.1657042],
    "c9-n1-t1-t2": [24.2106567, 106.1106057],
    "c9-n1-t1-t3": [28.9141381, 108.910525],
    "c9-n1-t2-t0": [29.0100448191025, 118.515585488198],
    "c9-n1-t2-t1": [30.3720862, 106.1657042],
    "c9-n1-t2-t2": [24.2106567, 106.1106057],
    "c9-n1-t2-t3": [28.9141381, 108.910525],
    "c9-n1-t3-t0": [29.0100448191025, 118.515585488198],
    "c9-n1-t3-t1": [30.3720862, 106.1657042],
    "c9-n1-t3-t2": [24.2106567, 106.1106057],
    "c9-n1-t3-t3": [28.9141381, 108.910525],
}


def load_store_json(zip_path: Path) -> dict:
    with zipfile.ZipFile(zip_path) as z:
        if "store.json" in z.namelist():
            return json.loads(z.read("store.json"))
        tpl = z.read("editor.tpl").decode("utf-8")
        m = re.search(r'<DuchampTemplateAttr store="([^"]*)"', tpl)
        if not m:
            raise ValueError(f"no store in {zip_path}")
        return json.loads(html.unescape(m.group(1)))


def encode_store_in_tpl(tpl: str, store_text: str) -> str:
    s = tpl.find('<DuchampTemplateAttr store="')
    if s < 0:
        raise ValueError("DuchampTemplateAttr not found in editor.tpl")
    e = tpl.find('"/>', s) + 3
    enc = (
        store_text.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return tpl[:s] + '<DuchampTemplateAttr store="' + enc + '"/>' + tpl[e:]


def patch_geourl_chart(text: str) -> tuple[str, int]:
    n = 0
    if GEOURL_L1 not in text:
        text2, c = re.subn(
            r'geourl="assets/map/geographic/农业基地-大疆测绘/'
            r'农业基地_v7\.4_GCJ02_L3_SingleMap/农业基地\.json"',
            f'geourl="{GEOURL_L1}"',
            text,
        )
        if c:
            text = text2
            n += c
        else:
            text2, c = re.subn(
                r'geourl="[^"]*农业基地_v7\.4[^"]*"',
                f'geourl="{GEOURL_L1}"',
                text,
                count=1,
            )
            if c:
                text = text2
                n += c
    return text, n


def _append_panto_to_tab(store: dict) -> int:
    """在 Tab 的 JavaScript 动作末尾追加 区域地图.panTo（不改动下拉框逻辑）。"""
    n = 0
    by_name = {
        w.get("name"): w
        for w in store["stories"][0]["widgets"]
        if w.get("name")
    }
    pan_line_tpl = (
        'duchamp.getWidgetByName("区域地图").panTo([{lat}, {lng}]);'
    )
    for tab_name, coords in TAB_PANTO.items():
        w = by_name.get(tab_name)
        if not w:
            continue
        lat, lng = coords
        pan_line = pan_line_tpl.format(lat=lat, lng=lng)
        for block in w.get("widgetEvents") or []:
            for ev in block.get("events") or []:
                for act in ev.get("actions") or []:
                    if act.get("type") != "javascript":
                        continue
                    code = act.get("body", {}).get("code") or ""
                    if "getWidgetByName(\"区域地图\").panTo" in code:
                        continue
                    if "下拉框_" not in code:
                        continue
                    act["body"]["code"] = code.rstrip() + "\n\n" + pan_line + "\n"
                    n += 1
    return n


def merge_store_minimal(target: dict) -> dict:
    out = json.loads(json.dumps(target))
    out["showAlignmentLine"] = False
    removed = 0
    widgets = out["stories"][0]["widgets"]
    # 去掉误合并进来的 4.6 视图树 / 片区标题文本框（若存在）
    drop_prefixes = ("视图树1_", "标题1_", "文本框1_")
    kept = []
    for w in widgets:
        name = w.get("name") or ""
        if name.startswith(drop_prefixes):
            removed += 1
            continue
        if name.startswith("下拉框_"):
            w.pop("hide", None)
            if name == "下拉框_常山片区":
                w["hide"] = False
            elif name.endswith("片区"):
                w["hide"] = True
        kept.append(w)
    out["stories"][0]["widgets"] = kept
    panto = _append_panto_to_tab(out)
    print(
        f"store: showAlignmentLine=False, removed_46_widgets={removed}, "
        f"tab_panTo_appended={panto}"
    )
    return out


def latest_backup() -> Path | None:
    parent = TARGET.parent
    candidates = sorted(
        parent.glob(f"{TARGET.name}.bak-merge-*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def merge_fvs(*, restore_backup: bool) -> None:
    if not TARGET.is_file():
        raise SystemExit(f"target missing: {TARGET}")

    src_zip = TARGET
    if restore_backup:
        bak = latest_backup()
        if not bak:
            raise SystemExit("no .bak-merge-* backup found")
        shutil.copy2(bak, TARGET)
        print(f"restored from: {bak}")
        src_zip = TARGET

    store = load_store_json(src_zip)
    merged_store = merge_store_minimal(store)
    store_text = json.dumps(merged_store, ensure_ascii=False, separators=(",", ":"))

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup = TARGET.with_suffix(f".fvs.bak-merge-{stamp}")
    shutil.copy2(TARGET, backup)
    print(f"backup: {backup}")

    tmp = TARGET.with_suffix(".fvs.merge-tmp")
    chart_patches = 0
    with zipfile.ZipFile(TARGET, "r") as zin, zipfile.ZipFile(
        tmp, "w", zipfile.ZIP_DEFLATED
    ) as zout:
        for info in zin.infolist():
            name = info.filename
            if name.startswith("__temp__copy__/"):
                continue
            data = zin.read(name)
            if name.endswith(".chart"):
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    zout.writestr(info, data)
                    continue
                text, n = patch_geourl_chart(text)
                if n:
                    chart_patches += n
                    print(f"  chart {name}: geourl patched")
                    data = text.encode("utf-8")
            elif name == "store.json":
                data = store_text.encode("utf-8")
            elif name == "editor.tpl":
                tpl = data.decode("utf-8")
                data = encode_store_in_tpl(tpl, store_text).encode("utf-8")
            zout.writestr(info, data)

    __import__("os").replace(tmp, TARGET)
    print(f"done: {TARGET}")
    print(f"geourl: {GEOURL_L1}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--restore-backup",
        action="store_true",
        help="先从最近的 .bak-merge-* 恢复服务器 3.5.1 稿，再打 geourl",
    )
    args = ap.parse_args()
    merge_fvs(restore_backup=args.restore_backup)


if __name__ == "__main__":
    main()
