#!/usr/bin/env python3
"""
v7.5：常山基地灾害天气改为数据集展示（对照 v7.4 4.6 稿），并关闭设计器对齐线。

- 从 4.6 补入 C3 下：表格1_天气、富文本-天气_c1、富文本-info天气（绑定 C3T1_实时预警）
- 常山 Tab：隐藏 天气-轮播，显示上述三组件
- 其他基地 Tab：显示 天气-轮播，隐藏上述三组件
- showAlignmentLine = false

不修改 geourl、不删下拉框、不替换整段 Tab 脚本（仅在原有「下拉框」JavaScript 末尾追加几行）。

  python3 scripts/ops/fr_patch_v75_c3_disaster_weather.py
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

TARGET = fvs_path("Agriculture_v7.5_GCJ02_L3_3.5.fvs")
REF_46 = fvs_path("Agriculture_v7.4_GCJ02_L3_4.6.fvs")

C3_PARENT = "f1157c65-ba89-44cc-be8d-2ca2741b773c"
WEATHER_FROM_46 = ("表格1_天气", "富文本-天气_c1", "富文本-info天气")
CAROUSEL = "天气-轮播"
TAB_RE = re.compile(r"^c9-n1-t\d+-t(\d)$")

SHOW_TABLE_JS = """
duchamp.getWidgetByName("天气-轮播").setVisible(false);
duchamp.getWidgetByName("表格1_天气").setVisible(true);
duchamp.getWidgetByName("富文本-天气_c1").setVisible(true);
duchamp.getWidgetByName("富文本-info天气").setVisible(true);
""".strip()

SHOW_CAROUSEL_JS = """
duchamp.getWidgetByName("天气-轮播").setVisible(true);
duchamp.getWidgetByName("表格1_天气").setVisible(false);
duchamp.getWidgetByName("富文本-天气_c1").setVisible(false);
duchamp.getWidgetByName("富文本-info天气").setVisible(false);
""".strip()


def load_store(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        if "store.json" in z.namelist():
            return json.loads(z.read("store.json"))
        tpl = z.read("editor.tpl").decode("utf-8")
        m = re.search(r'<DuchampTemplateAttr store="([^"]*)"', tpl)
        return json.loads(html.unescape(m.group(1)))


def encode_store_in_tpl(tpl: str, store_text: str) -> str:
    s = tpl.find('<DuchampTemplateAttr store="')
    e = tpl.find('"/>', s) + 3
    enc = (
        store_text.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return tpl[:s] + '<DuchampTemplateAttr store="' + enc + '"/>' + tpl[e:]


def copy_weather_widgets_from_46(store: dict, ref: dict) -> int:
    by_name = {w.get("name"): w for w in store["stories"][0]["widgets"] if w.get("name")}
    ref_by = {w.get("name"): w for w in ref["stories"][0]["widgets"] if w.get("name")}
    added = 0
    for name in WEATHER_FROM_46:
        if name in by_name:
            continue
        w = json.loads(json.dumps(ref_by[name]))
        w["parent"] = C3_PARENT
        w["hide"] = False
        store["stories"][0]["widgets"].append(w)
        by_name[name] = w
        added += 1
    return added


def set_initial_visibility(store: dict) -> None:
    by_name = {w.get("name"): w for w in store["stories"][0]["widgets"] if w.get("name")}
    if CAROUSEL in by_name:
        by_name[CAROUSEL]["hide"] = True
    for name in WEATHER_FROM_46:
        if name in by_name:
            by_name[name]["hide"] = False


def append_weather_toggle_js(store: dict) -> int:
    n = 0
    for w in store["stories"][0]["widgets"]:
        name = w.get("name") or ""
        m = TAB_RE.match(name)
        if not m:
            continue
        col = int(m.group(1))
        extra = SHOW_TABLE_JS if col == 0 else SHOW_CAROUSEL_JS
        marker = '表格1_天气").setVisible'
        for block in w.get("widgetEvents") or []:
            for ev in block.get("events") or []:
                for act in ev.get("actions") or []:
                    if act.get("type") != "javascript":
                        continue
                    code = act.get("body", {}).get("code") or ""
                    if "下拉框_" not in code:
                        continue
                    if marker in code:
                        continue
                    act["body"]["code"] = code.rstrip() + "\n\n" + extra + "\n"
                    n += 1
                    break
                else:
                    continue
                break
            else:
                continue
            break
    return n


def patch_fvs() -> None:
    if not TARGET.is_file() or not REF_46.is_file():
        raise SystemExit("target or reference FVS missing")

    ref = load_store(REF_46)
    store = load_store(TARGET)
    store["showAlignmentLine"] = False
    added = copy_weather_widgets_from_46(store, ref)
    set_initial_visibility(store)
    js_n = append_weather_toggle_js(store)
    store_text = json.dumps(store, ensure_ascii=False, separators=(",", ":"))

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup = TARGET.with_suffix(f".fvs.bak-c3weather-{stamp}")
    shutil.copy2(TARGET, backup)
    print(f"backup: {backup}")
    print(f"widgets added from 4.6: {added}, tab JS patched: {js_n}")

    tmp = TARGET.with_suffix(".fvs.c3-tmp")
    with zipfile.ZipFile(TARGET, "r") as zin, zipfile.ZipFile(
        tmp, "w", zipfile.ZIP_DEFLATED
    ) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.startswith("__temp__copy__/"):
                continue
            if info.filename == "store.json":
                data = store_text.encode("utf-8")
            elif info.filename == "editor.tpl":
                data = encode_store_in_tpl(data.decode("utf-8"), store_text).encode("utf-8")
            zout.writestr(info, data)

    __import__("os").replace(tmp, TARGET)
    print(f"done: {TARGET}")


def main() -> None:
    patch_fvs()


if __name__ == "__main__":
    main()
