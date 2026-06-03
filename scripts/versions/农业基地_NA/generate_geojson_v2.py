#!/usr/bin/env python3
"""
Generate GeoJSON boundary files for agricultural dashboard map.
Output: 农业基地_v2.json, 农业基地_v2-area.json, 农业基地_v2-point.json
"""

import json
import math
from xml.etree import ElementTree as ET
from collections import defaultdict
import pymysql
from shapely.geometry import Polygon, MultiPolygon, Point, mapping
from shapely.ops import unary_union

# ─── Paths ───────────────────────────────────────────────────────────────────
KML_ROOT = (
    "/Users/cenl/docs/work/2025/4.项目管理/"
    "P2025-G-001-数智部-农业大屏一期  ★/"
    "5.数据设计/农业数据/6.片区边界/1.农业基地KML"
)
OUTPUT_DIR = (
    "/Applications/FineReport/webapps/webroot/"
    "WEB-INF/assets/map/geographic/world/中国"
)

KML_FILES = {
    "CS_东区":   f"{KML_ROOT}/1.常山地图KML/东区_KML导出_20260602125704.kml",
    "CS_东岸重画": f"{KML_ROOT}/1.常山地图KML/东岸重画_KML导出_20260602125609.kml",
    "CS_西1区":  f"{KML_ROOT}/1.常山地图KML/西1区_KML导出_20260602125813.kml",
    "CS_西2区":  f"{KML_ROOT}/1.常山地图KML/西2区_KML导出_20260602125842.kml",
    "CS_示范区":  f"{KML_ROOT}/1.常山地图KML/同弓示范区_KML导出_20260602125740.kml",
    "WS":        f"{KML_ROOT}/2.武胜地图KML/武胜地图KML导出_20260602130007.kml",
    "BS":        f"{KML_ROOT}/3.百色地图KML/百色地图KML导出_20260602125921.kml",
}

# ─── Color/folder discard rules ───────────────────────────────────────────────
DISCARD_COLORS = {"#b620e0", "#ffbb00", "#19be6b"}


def should_keep(path, color):
    """Return True if the polygon should be kept (测绘面积)."""
    path_has_zhong = any("种植" in p or "种面" in p for p in path)
    is_discard_color = (color is not None) and (color.lower() in DISCARD_COLORS)
    return not path_has_zhong and not is_discard_color


# ─── Folder → 片区 mappings ───────────────────────────────────────────────────
CS_DONG_FOLDER_TO_PQ = {
    "大埂基地": "大埂",
    "东乡基地": "东乡",
    "双溪口1基地": "双溪口1",
    "双溪口2基地": "双溪口2",
    "路里坑": "路里坑",
    "彭川基地KML": "彭川",
    "狮东基地": "狮东",
    # 东案基地 → SKIP (replaced by 东岸重画)
}

CS_XI1_FOLDER_TO_PQ = {
    "草坪基地": "草坪",
    "景区基地": "景区",
    "十五里基地": "十五里",
    "育苗中心": "周家园育苗中心",
}

CS_XI2_FOLDER_TO_PQ = {
    "曹会关基地": "曹会关",
    "和平基地": "和平",
    "金川基地": "金川",
    "天安基地": "天安",
    "新塘岭基地": "新塘岭",
    "新塘岭（新）": "新塘岭",
    "石坝基地": "石坝",
    "五联基地": "五联",
    "羊坳水库": "羊坳水库",
}

CS_SHIFAN_FOLDER_TO_PQ = {
    "同弓示范基地": "同弓示范基地",
    "同弓苗地": "同弓苗地",
    "同弓高换基地": "同弓高换基地",
}

WS_FOLDER_TO_PQ = {
    "三溪育苗基地": "三溪苗圃",
    "三溪西区639.8亩": "三溪西区",
    "三溪西区": "三溪西区",
    "三溪南区495.52": "三溪南区",
    "三溪南区495.52亩": "三溪南区",
    "三溪北区598.61亩": "三溪北区",
    "三溪东区596.77亩": "三溪东区",
    "金狮": "金狮",
    "幸福": "幸福",
    "干家湾": "干家湾宝箴塞",
    "穿岩洞、石门楼、五谷湾、保安": "穿岩",
    "桂花湾": "桂花湾",
    "响水": "响水滩",
    "小寨": "小寨",
    "观音塘": "观音塘",
    "嘉乐": "嘉乐",
    "龙头沟 ": "龙头沟",
    "龙头沟": "龙头沟",
    "吊井龙": "吊井龙",
    "望乡坪 266.9亩": "望乡坪",
    "望乡坪": "望乡坪",
    "沙溪": "沙溪",
    "桥亭": "桥亭1",
    "桥亭2": "桥亭2",
    "陈家寨2": "陈家寨2",
    "白果": "白果",
    "陈家寨1": "陈家寨1",
    "华家坪（新）": "华家坪",
    "华家坪": "华家坪",
    "象鼻": "象鼻",
    "涌泉": "会云",
    "会云": "会云",
    "龙兴": "龙兴",
    "九湾": "九湾",
    "方沟": "方沟",
    "天星桥": "天星桥",
    "李子坑": "李子坑",
    "应家沟": "应家沟",
    "尼姑庵": "尼姑庵",
    "花墙": "花墙",
    "飞龙3片": "飞龙3",
    "飞龙2片": "飞龙2",
    "飞龙1片": "飞龙1",
}

# ─── KML parsing ─────────────────────────────────────────────────────────────
NS = "http://www.opengis.net/kml/2.2"


def _parse_coords(coords_text):
    """Parse KML coordinates string into list of (lng, lat) tuples (drop alt)."""
    points = []
    for token in coords_text.strip().split():
        token = token.strip()
        if not token:
            continue
        parts = token.split(",")
        if len(parts) >= 2:
            lng = float(parts[0])
            lat = float(parts[1])
            points.append((lng, lat))
    return points


def _get_color(placemark_elem):
    """Extract color from a Placemark's ExtendedData."""
    for d in placemark_elem.findall(f".//{{{NS}}}Data"):
        if d.get("name") == "color":
            val = d.find(f"{{{NS}}}value")
            if val is not None:
                return val.text
    return None


def _make_polygon(coords_list):
    """Create a Shapely Polygon from [(lng, lat), ...] discarding degenerate ones."""
    if len(coords_list) < 3:
        return None
    try:
        poly = Polygon(coords_list)
        if not poly.is_valid:
            poly = poly.buffer(0)
        return poly if poly.is_valid and not poly.is_empty else None
    except Exception:
        return None


def _collect_placemarks(elem, path, callback):
    """Recursively walk KML tree calling callback(path, color, polygon_coords)."""
    tag = elem.tag.split("}")[-1]
    if tag == "Folder":
        name_el = elem.find(f"{{{NS}}}name")
        name = name_el.text if name_el is not None else ""
        for child in elem:
            _collect_placemarks(child, path + [name], callback)
    elif tag == "Placemark":
        color = _get_color(elem)
        # Handle outer boundary only (inner holes ignored — simplification)
        for poly_el in elem.findall(f".//{{{NS}}}Polygon"):
            outer = poly_el.find(
                f"{{{NS}}}outerBoundaryIs/{{{NS}}}LinearRing/{{{NS}}}coordinates"
            )
            if outer is not None:
                coords = _parse_coords(outer.text or "")
                callback(path, color, coords)
    else:
        for child in elem:
            _collect_placemarks(child, path, callback)


def parse_kml(kml_path):
    """Return list of dicts: {path, color, coords}."""
    tree = ET.parse(kml_path)
    root = tree.getroot()
    placemarks = []

    def cb(path, color, coords):
        placemarks.append({"path": path, "color": color, "coords": coords})

    _collect_placemarks(root, [], cb)
    return placemarks


# ─── DB helpers ──────────────────────────────────────────────────────────────
def load_db_districts():
    """Load all districts from DB into a nested dict keyed by (基地名称, 片区名称)."""
    conn = pymysql.connect(
        host="172.17.4.4",
        port=3310,
        user="bigdata",
        password="yxgbigdata@YXG321",
        database="yxg_bigscreen",
        charset="utf8mb4",
    )
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 片区编号, 基地名称, 区域名称, 片区编码, 片区名称, 片区经度, 片区纬度 "
        "FROM ods_ag_base_v2 "
        "WHERE 基地名称 IN ('浙江常山','四川武胜','广西百色') "
        "ORDER BY 基地名称, 片区编号"
    )
    rows = cursor.fetchall()
    conn.close()
    db = {}
    for row in rows:
        pq_num, base, region, code, name, lng, lat = row
        key = (base, name)
        db[key] = {
            "片区编号": pq_num,
            "基地名称": base,
            "区域名称": region,
            "片区编码": code,
            "片区名称": name,
            "片区经度": float(lng) if lng is not None else None,
            "片区纬度": float(lat) if lat is not None else None,
        }
    return db


# ─── Geometry helpers ─────────────────────────────────────────────────────────
def polygon_centroid(shapely_geom):
    """Return (lng, lat) centroid of any shapely geometry."""
    c = shapely_geom.centroid
    return [round(c.x, 10), round(c.y, 10)]


def geometry_to_geojson(shapely_geom):
    """Convert shapely geometry to GeoJSON-compatible dict with rounded coords."""
    raw = mapping(shapely_geom)
    return _round_coords(raw)


def _round_coords(obj):
    if isinstance(obj, dict):
        return {k: _round_coords(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        result = [_round_coords(x) for x in obj]
        return result
    if isinstance(obj, float):
        return round(obj, 10)
    return obj


# ─── Per-KML processing ──────────────────────────────────────────────────────
def process_cs_dong(placemarks, pq_polygons):
    """Process 常山 东区 KML (path[2] = base folder)."""
    for pm in placemarks:
        path = pm["path"]
        color = pm["color"]
        coords = pm["coords"]
        if not should_keep(path, color):
            continue
        if len(path) < 3:
            continue
        folder2 = path[2]
        pq_name = CS_DONG_FOLDER_TO_PQ.get(folder2)
        if pq_name is None:
            continue  # SKIP 东案基地 and unknowns
        poly = _make_polygon(coords)
        if poly is not None:
            pq_polygons[("浙江常山", pq_name)].append(poly)


def process_cs_donganzhuanghua(placemarks, pq_polygons):
    """Process 常山 东岸重画 (split by centroid lat vs 29.0)."""
    for pm in placemarks:
        path = pm["path"]
        color = pm["color"]
        coords = pm["coords"]
        if not should_keep(path, color):
            continue
        poly = _make_polygon(coords)
        if poly is None:
            continue
        clat = poly.centroid.y
        pq_name = "开向岭" if clat > 29.0 else "祠堂坑"
        pq_polygons[("浙江常山", pq_name)].append(poly)


def process_cs_xi1(placemarks, pq_polygons):
    """Process 常山 西1区 (path[2] = base folder)."""
    for pm in placemarks:
        path = pm["path"]
        color = pm["color"]
        coords = pm["coords"]
        if not should_keep(path, color):
            continue
        if len(path) < 3:
            continue
        folder2 = path[2]
        pq_name = CS_XI1_FOLDER_TO_PQ.get(folder2)
        if pq_name is None:
            continue
        poly = _make_polygon(coords)
        if poly is not None:
            pq_polygons[("浙江常山", pq_name)].append(poly)


def process_cs_xi2(placemarks, pq_polygons):
    """Process 常山 西2区 (path[2] = base folder, union for 新塘岭)."""
    for pm in placemarks:
        path = pm["path"]
        color = pm["color"]
        coords = pm["coords"]
        if not should_keep(path, color):
            continue
        if len(path) < 3:
            continue
        folder2 = path[2]
        pq_name = CS_XI2_FOLDER_TO_PQ.get(folder2)
        if pq_name is None:
            continue
        poly = _make_polygon(coords)
        if poly is not None:
            pq_polygons[("浙江常山", pq_name)].append(poly)


def process_cs_shifan(placemarks, pq_polygons):
    """Process 常山 示范区 (path[2] = base folder)."""
    for pm in placemarks:
        path = pm["path"]
        color = pm["color"]
        coords = pm["coords"]
        if not should_keep(path, color):
            continue
        if len(path) < 3:
            continue
        folder2 = path[2]
        pq_name = CS_SHIFAN_FOLDER_TO_PQ.get(folder2)
        if pq_name is None:
            continue
        poly = _make_polygon(coords)
        if poly is not None:
            pq_polygons[("浙江常山", pq_name)].append(poly)


def process_ws(placemarks, pq_polygons):
    """Process 武胜 KML (path[2] = base folder)."""
    for pm in placemarks:
        path = pm["path"]
        color = pm["color"]
        coords = pm["coords"]
        if not should_keep(path, color):
            continue
        if len(path) < 3:
            continue
        folder2 = path[2]
        pq_name = WS_FOLDER_TO_PQ.get(folder2)
        if pq_name is None:
            # Log unmapped folders
            # print(f"  [WS] unmapped path[2]={repr(folder2)}")
            continue
        poly = _make_polygon(coords)
        if poly is not None:
            pq_polygons[("四川武胜", pq_name)].append(poly)


def process_bs(placemarks, pq_polygons):
    """Process 百色 KML (path[1] = 片区名称 directly)."""
    for pm in placemarks:
        path = pm["path"]
        color = pm["color"]
        coords = pm["coords"]
        if not should_keep(path, color):
            continue
        if len(path) < 2:
            continue
        pq_name = path[1]  # 平林 or 龙细
        poly = _make_polygon(coords)
        if poly is not None:
            pq_polygons[("广西百色", pq_name)].append(poly)


# ─── Build GeoJSON features ──────────────────────────────────────────────────
def build_features(db, pq_polygons):
    """
    Return (area_features, point_features).
    area_features: only 片区 that have polygon data.
    point_features: ALL 片区 from DB.
    """
    area_features = []
    point_features = []

    # Process in DB order
    db_items = sorted(db.values(), key=lambda x: (x["基地名称"], x["片区编号"]))

    for info in db_items:
        base = info["基地名称"]
        pq_name = info["片区名称"]
        key = (base, pq_name)

        db_lng = info["片区经度"]
        db_lat = info["片区纬度"]

        polys = pq_polygons.get(key, [])

        # Union polygons
        merged_geom = None
        if polys:
            try:
                merged_geom = unary_union(polys)
                if merged_geom.is_empty:
                    merged_geom = None
            except Exception as e:
                print(f"  [WARN] union failed for {key}: {e}")
                merged_geom = None

        # Determine center
        if db_lng is not None and db_lat is not None:
            center = [round(db_lng, 10), round(db_lat, 10)]
        elif merged_geom is not None:
            center = polygon_centroid(merged_geom)
        else:
            center = None

        props = {
            "name": pq_name,
            "center": center,
            "基地名称": base,
            "区域名称": info["区域名称"],
            "片区编码": info["片区编码"],
            "片区编号": info["片区编号"],
        }

        # Area feature
        if merged_geom is not None:
            geom_geojson = geometry_to_geojson(merged_geom)
            area_features.append({
                "type": "Feature",
                "properties": props,
                "geometry": geom_geojson,
            })

        # Point feature
        if center is not None:
            point_features.append({
                "type": "Feature",
                "properties": props,
                "geometry": {
                    "type": "Point",
                    "coordinates": center,
                },
            })
        else:
            # Include even without center (null geometry)
            point_features.append({
                "type": "Feature",
                "properties": props,
                "geometry": None,
            })

    return area_features, point_features


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("Loading DB districts...")
    db = load_db_districts()
    print(f"  Loaded {len(db)} districts")

    print("\nParsing KML files...")
    # Accumulate polygons per (基地名称, 片区名称)
    pq_polygons = defaultdict(list)

    print("  Processing 常山 东区...")
    pms = parse_kml(KML_FILES["CS_东区"])
    process_cs_dong(pms, pq_polygons)

    print("  Processing 常山 东岸重画...")
    pms = parse_kml(KML_FILES["CS_东岸重画"])
    process_cs_donganzhuanghua(pms, pq_polygons)

    print("  Processing 常山 西1区...")
    pms = parse_kml(KML_FILES["CS_西1区"])
    process_cs_xi1(pms, pq_polygons)

    print("  Processing 常山 西2区...")
    pms = parse_kml(KML_FILES["CS_西2区"])
    process_cs_xi2(pms, pq_polygons)

    print("  Processing 常山 示范区...")
    pms = parse_kml(KML_FILES["CS_示范区"])
    process_cs_shifan(pms, pq_polygons)

    print("  Processing 武胜...")
    pms = parse_kml(KML_FILES["WS"])
    process_ws(pms, pq_polygons)

    print("  Processing 百色...")
    pms = parse_kml(KML_FILES["BS"])
    process_bs(pms, pq_polygons)

    # Summary of polygon counts
    print("\n  Polygon counts per 片区:")
    for (base, pq), polys in sorted(pq_polygons.items()):
        print(f"    {base} / {pq}: {len(polys)} polygons")

    print("\nBuilding GeoJSON features...")
    area_features, point_features = build_features(db, pq_polygons)

    # Summary of found/missing
    db_pq_names = {(v["基地名称"], v["片区名称"]) for v in db.values()}
    found = set(pq_polygons.keys())
    missing = db_pq_names - found
    extra = found - db_pq_names

    print(f"\n  Area features: {len(area_features)}")
    print(f"  Point features: {len(point_features)}")
    print(f"  Missing polygons (in DB but not in KML): {len(missing)}")
    for m in sorted(missing):
        print(f"    {m[0]} / {m[1]}")
    if extra:
        print(f"  Extra polygons (in KML but not in DB): {len(extra)}")
        for e in sorted(extra):
            print(f"    {e[0]} / {e[1]}")

    # Build GeoJSON objects
    area_geojson = {
        "type": "FeatureCollection",
        "name": "农业基地",
        "features": area_features,
    }
    point_geojson = {
        "type": "FeatureCollection",
        "name": "农业基地",
        "features": point_features,
    }

    # Write files
    area_path = f"{OUTPUT_DIR}/农业基地_v2.json"
    area_path2 = f"{OUTPUT_DIR}/农业基地_v2-area.json"
    point_path = f"{OUTPUT_DIR}/农业基地_v2-point.json"

    print(f"\nWriting {area_path} ...")
    with open(area_path, "w", encoding="utf-8") as f:
        json.dump(area_geojson, f, ensure_ascii=False, indent=2)

    print(f"Writing {area_path2} ...")
    with open(area_path2, "w", encoding="utf-8") as f:
        json.dump(area_geojson, f, ensure_ascii=False, indent=2)

    print(f"Writing {point_path} ...")
    with open(point_path, "w", encoding="utf-8") as f:
        json.dump(point_geojson, f, ensure_ascii=False, indent=2)

    print("\nDone!")
    print("=" * 60)


if __name__ == "__main__":
    main()
