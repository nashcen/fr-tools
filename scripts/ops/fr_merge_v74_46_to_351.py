#!/usr/bin/env python3
"""
将 Agriculture_v7.4_GCJ02_L3_SingleMap_4.6.fvs 的 geourl 与单图交互逻辑
合并到 3.5.1 兼容的 Agriculture_v7.4_GCJ02_L3_SingleMap.fvs（保留 templateVersion）。

用法（在 FineReport WEB-INF 下）:
  python3 scripts/ops/fr_merge_v74_46_to_351.py
"""

from __future__ import annotations

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

# 4.6 有、3.5.1 无的控件（视图树、片区标题/文本框等）
WIDGETS_ONLY_46_PREFIXES = (
    "视图树1_",
    "标题1_",
    "文本框1_",
    "表格1_天气",
    "富文本-info",
    "富文本-天气_c1",
    "北极星_总亩数",
)

# 从 4.6 复制 widgetEvents 的控件（基地 Tab 等）
COPY_EVENTS_NAMES = {
    f"c9-n1-t{i}-t{j}" for i in range(4) for j in range(4)
} | {"日常操作-轮播"}


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


def merge_store(target: dict, source: dict) -> dict:
    out = json.loads(json.dumps(target))  # deep copy
    out["templateVersion"] = target.get("templateVersion")

    widgets_t = out["stories"][0]["widgets"]
    widgets_s = source["stories"][0]["widgets"]
    by_name_t = {w.get("name"): w for w in widgets_t if w.get("name")}
    by_name_s = {w.get("name"): w for w in widgets_s if w.get("name")}

    merged_events = 0
    hidden_dropdown = 0
    added = 0

    for w in widgets_t:
        name = w.get("name") or ""
        if name in by_name_s and name in COPY_EVENTS_NAMES:
            w["widgetEvents"] = json.loads(
                json.dumps(by_name_s[name].get("widgetEvents", []))
            )
            merged_events += 1
        if name.startswith("下拉框_"):
            w["hide"] = True
            hidden_dropdown += 1

    existing = set(by_name_t)
    for w in widgets_s:
        name = w.get("name") or ""
        if not name or name in existing:
            continue
        if name.startswith(WIDGETS_ONLY_46_PREFIXES) or name in (
            "表格1_天气",
            "北极星_总亩数",
        ):
            widgets_t.append(json.loads(json.dumps(w)))
            existing.add(name)
            added += 1

    print(
        f"store merge: widgetEvents copied={merged_events}, "
        f"dropdown hide={hidden_dropdown}, widgets added={added}"
    )
    return out


def merge_fvs() -> None:
    if not TARGET.is_file():
        raise SystemExit(f"target missing: {TARGET}")
    if not SOURCE_46.is_file():
        raise SystemExit(f"source missing: {SOURCE_46}")

    store_46 = load_store_json(SOURCE_46)
    store_351 = load_store_json(TARGET)
    merged_store = merge_store(store_351, store_46)
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

    if chart_patches == 0:
        print("warning: no chart geourl changes (already correct?)")

    os_replace = __import__("os").replace
    os_replace(tmp, TARGET)
    print(f"done: {TARGET}")
    print(f"geourl: {GEOURL_L1}")


def main() -> None:
    merge_fvs()


if __name__ == "__main__":
    main()
