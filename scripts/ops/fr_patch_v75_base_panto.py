#!/usr/bin/env python3
"""
v7.5：仅在基地 Tab 切换脚本末尾追加「区域地图.panTo」中心点（对照 v7.4 的 4.6 稿）。

只改 store.json / editor.tpl 中 16 个 c9-n1-t*-t* 的 JavaScript，其余文件与字段不动。

  python3 scripts/ops/fr_patch_v75_base_panto.py
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

MAP_WIDGET = "区域地图"
PANTO_MARKER = f'getWidgetByName("{MAP_WIDGET}").panTo'

# t0=常山 t1=武胜 t2=酉阳 t3=百色（与 v7.4 4.6 稿一致，[lat, lng]）
COL_PANTO = {
    0: [29.0100448191025, 118.515585488198],
    1: [30.3720862, 106.1657042],
    2: [24.2106567, 106.1106057],
    3: [28.9141381, 108.910525],
}

TAB_RE = re.compile(r"^c9-n1-t\d+-t(\d)$")


def load_store_from_zip(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        if "store.json" in z.namelist():
            return json.loads(z.read("store.json"))
        tpl = z.read("editor.tpl").decode("utf-8")
        m = re.search(r'<DuchampTemplateAttr store="([^"]*)"', tpl)
        if not m:
            raise ValueError(f"no store in {path}")
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


def panto_line(lat: float, lng: float) -> str:
    return f'duchamp.getWidgetByName("{MAP_WIDGET}").panTo([{lat}, {lng}]);'


def extract_panto_from_ref(ref: dict) -> dict[int, list[float]]:
    """从参考稿读取 t0..t3 的 panTo 坐标（列与基地对应）。"""
    out: dict[int, list[float]] = dict(COL_PANTO)
    by_name = {
        w.get("name"): w
        for w in ref["stories"][0]["widgets"]
        if w.get("name")
    }
    for j in range(4):
        w = by_name.get(f"c9-n1-t0-t{j}")
        if not w:
            continue
        for block in w.get("widgetEvents") or []:
            for ev in block.get("events") or []:
                for act in ev.get("actions") or []:
                    if act.get("type") != "javascript":
                        continue
                    code = act.get("body", {}).get("code") or ""
                    m = re.search(
                        r'getWidgetByName\("区域地图"\)\.panTo\(\[([^\]]+)\]\)',
                        code,
                    )
                    if m:
                        parts = [float(x.strip()) for x in m.group(1).split(",")]
                        if len(parts) == 2:
                            out[j] = parts
    return out


def append_panto_to_store(store: dict, col_panto: dict[int, list[float]]) -> int:
    n = 0
    for w in store["stories"][0]["widgets"]:
        name = w.get("name") or ""
        m = TAB_RE.match(name)
        if not m:
            continue
        col = int(m.group(1))
        coords = col_panto.get(col)
        if not coords:
            continue
        lat, lng = coords
        line = panto_line(lat, lng)
        for block in w.get("widgetEvents") or []:
            for ev in block.get("events") or []:
                for act in ev.get("actions") or []:
                    if act.get("type") != "javascript":
                        continue
                    code = act.get("body", {}).get("code") or ""
                    if "下拉框_" not in code:
                        continue
                    if PANTO_MARKER in code:
                        continue
                    act["body"]["code"] = code.rstrip() + "\n\n" + line + "\n"
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
    if not TARGET.is_file():
        raise SystemExit(f"target missing: {TARGET}")
    if not REF_46.is_file():
        raise SystemExit(f"reference missing: {REF_46}")

    ref_store = load_store_from_zip(REF_46)
    col_panto = extract_panto_from_ref(ref_store)
    store = load_store_from_zip(TARGET)
    before = json.dumps(store, ensure_ascii=False, separators=(",", ":"))
    n = append_panto_to_store(store, col_panto)
    after = json.dumps(store, ensure_ascii=False, separators=(",", ":"))
    if before == after:
        raise SystemExit("no changes — panTo already present?")

    store_text = after
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup = TARGET.with_suffix(f".fvs.bak-panto-{stamp}")
    shutil.copy2(TARGET, backup)
    print(f"backup: {backup}")
    print("panTo by column (t0..t3):", col_panto)

    tmp = TARGET.with_suffix(".fvs.panto-tmp")
    with zipfile.ZipFile(TARGET, "r") as zin, zipfile.ZipFile(
        tmp, "w", zipfile.ZIP_DEFLATED
    ) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "store.json":
                data = store_text.encode("utf-8")
            elif info.filename == "editor.tpl":
                tpl = data.decode("utf-8")
                data = encode_store_in_tpl(tpl, store_text).encode("utf-8")
            zout.writestr(info, data)

    __import__("os").replace(tmp, TARGET)
    print(f"done: {n} tab handler(s) patched in {TARGET}")


def main() -> None:
    patch_fvs()


if __name__ == "__main__":
    main()
