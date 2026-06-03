#!/usr/bin/env python3
"""
精准补丁：为 KML 可提取但 GeoJSON/DB 缺失坐标的片区补充边界与中心点。

当前处理：
  - 育苗中心 (片区编号=13)：西1区 KML，测绘面积多边形颜色 #FFBB00 被过滤
  - 羊坳水库 (片区编号=19)：西2区 KML，测绘面积多边形颜色 #19BE6B 被过滤

不可提取（KML 无对应数据，跳过）：
  - 姜盘石 (41)、水田 (76)、鱼水村 (77)、杉岭 (80)

坐标：KML 为 CGCS2000，输出 GeoJSON 与 DB 均为 GCJ-02（复用 lib/coord_convert_wgs84_to_gcj02.transform）
"""

import importlib.util
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union

# ─── 路径 ────────────────────────────────────────────────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
KML_ROOT = os.path.join(ROOT, 'data', '1.农业基地KML')
GEO_DIR = (
    '/Applications/FineReport/webapps/webroot/WEB-INF'
    '/assets/map/geographic/world/农业基地-大疆测绘/农业基地_v2_WGS84'
)
COORD_SCRIPT = os.path.join(os.path.dirname(__file__), '..', '..', 'lib', 'coord_convert_wgs84_to_gcj02.py')

DB = dict(host='172.17.4.4', port=3310, user='bigdata',
          pwd='yxgbigdata@YXG321', db='yxg_bigscreen')

NS = 'http://www.opengis.net/kml/2.2'

# 片区编号 → (KML 相对路径, 文件夹关键字)
PATCH_TARGETS = {
    13: ('1.常山地图KML/西1区_KML导出_20260602125813.kml', '育苗中心'),
    19: ('1.常山地图KML/西2区_KML导出_20260602125842.kml', '羊坳水库'),
}

GEO_FILES = [
    '农业基地_v2.json',
    '农业基地_v2-area.json',
    '农业基地_v2-point.json',
    '农业基地_v2_CS.json',
    '农业基地_v2_CS-point.json',
]


def load_transform():
    spec = importlib.util.spec_from_file_location('coord_convert', COORD_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.transform


def mysql_query(sql: str) -> list[list[str]]:
    r = subprocess.run(
        ['mysql', f'-h{DB["host"]}', f'-P{DB["port"]}', f'-u{DB["user"]}',
         f'-p{DB["pwd"]}', DB['db'], '--batch', '--skip-column-names', '-e', sql],
        capture_output=True, text=True, env=os.environ,
    )
    if r.returncode != 0:
        print(f'MySQL error: {r.stderr}', file=sys.stderr)
        sys.exit(1)
    return [line.split('\t') for line in r.stdout.strip().split('\n') if line]


def parse_coords(text: str) -> list[tuple[float, float]]:
    pts = []
    for token in (text or '').strip().split():
        parts = token.split(',')
        if len(parts) >= 2:
            pts.append((float(parts[0]), float(parts[1])))
    return pts


def collect_placemarks(elem, path, out):
    tag = elem.tag.split('}')[-1]
    if tag == 'Folder':
        name_el = elem.find(f'{{{NS}}}name')
        name = name_el.text if name_el is not None else ''
        for child in elem:
            collect_placemarks(child, path + [name], out)
    elif tag == 'Placemark':
        for poly_el in elem.findall(f'.//{{{NS}}}Polygon'):
            outer = poly_el.find(
                f'{{{NS}}}outerBoundaryIs/{{{NS}}}LinearRing/{{{NS}}}coordinates'
            )
            if outer is not None:
                out.append({'path': path, 'coords': parse_coords(outer.text)})
    else:
        for child in elem:
            collect_placemarks(child, path, out)


def extract_survey_polygon(kml_path: str, folder_keyword: str) -> Polygon | None:
    """从 KML 提取测绘面积多边形（绕过颜色过滤，排除种植面积文件夹）。"""
    tree = ET.parse(kml_path)
    placemarks = []
    collect_placemarks(tree.getroot(), [], placemarks)

    polys = []
    for pm in placemarks:
        path = pm['path']
        if not any(folder_keyword in p for p in path):
            continue
        if not any('测绘' in p for p in path):
            continue
        if any('种植' in p or '种面' in p for p in path):
            continue
        coords = pm['coords']
        if len(coords) < 3:
            continue
        poly = Polygon(coords)
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_valid and not poly.is_empty:
            polys.append(poly)
            print(f'    polygon: {" / ".join(path)}, verts={len(coords)}')

    if not polys:
        return None
    merged = unary_union(polys)
    return merged if not merged.is_empty else None


def convert_polygon(raw_poly: Polygon, transform_fn) -> tuple[dict, list[float]]:
    """CGCS2000 多边形 → GCJ-02 GeoJSON geometry + 重心。"""
    gcj = transform_fn(raw_poly.centroid.x, raw_poly.centroid.y)
    center = [round(gcj[0], 10), round(gcj[1], 10)]

    def conv_ring(ring):
        return [list(transform_fn(x, y)) for x, y in ring.coords]

    if raw_poly.geom_type == 'Polygon':
        geom = {'type': 'Polygon', 'coordinates': [conv_ring(raw_poly.exterior)]}
    else:
        geom = {
            'type': 'MultiPolygon',
            'coordinates': [[conv_ring(p.exterior)] for p in raw_poly.geoms],
        }
    return geom, center


def load_db_info(pq_ids: list[int]) -> dict[int, dict]:
    ids = ','.join(str(i) for i in pq_ids)
    rows = mysql_query(
        f"SELECT 片区编号,基地名称,区域名称,片区编码,片区名称 "
        f"FROM ods_ag_base_v2 WHERE 片区编号 IN ({ids})"
    )
    info = {}
    for r in rows:
        if len(r) < 5:
            continue
        info[int(r[0])] = {
            '片区编号': int(r[0]),
            '基地名称': r[1],
            '区域名称': r[2],
            '片区编码': r[3],
            '片区名称': r[4],
        }
    return info


def patch_area_file(path: str, new_area_features: list[dict]) -> None:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    by_id = {feat['properties']['片区编号']: i for i, feat in enumerate(data['features'])}
    added, updated = 0, 0

    for feat in new_area_features:
        pid = feat['properties']['片区编号']
        if pid in by_id:
            data['features'][by_id[pid]] = feat
            updated += 1
        else:
            data['features'].append(feat)
            added += 1

    data['features'].sort(key=lambda f: f['properties'].get('片区编号', 0))

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    print(f'  {os.path.basename(path)}: +{added} updated={updated}, total={len(data["features"])}')


def patch_point_file(path: str, point_updates: dict[int, dict]) -> None:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    updated = 0
    for feat in data['features']:
        pid = feat['properties'].get('片区编号')
        if pid not in point_updates:
            continue
        upd = point_updates[pid]
        feat['properties']['center'] = upd['center']
        feat['geometry'] = upd['geometry']
        updated += 1

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    print(f'  {os.path.basename(path)}: updated {updated} point(s)')


def update_db_coords(coords: dict[int, list[float]]) -> None:
    if not coords:
        return
    lng_cases, lat_cases, ids = [], [], []
    for pid, (lng, lat) in sorted(coords.items()):
        lng_cases.append(f'  WHEN {pid} THEN {lng:.10f}')
        lat_cases.append(f'  WHEN {pid} THEN {lat:.10f}')
        ids.append(str(pid))

    sql = (
        f"UPDATE ods_ag_base_v2 SET\n"
        f"  片区经度=CASE 片区编号\n{chr(10).join(lng_cases)}\n  ELSE 片区经度 END,\n"
        f"  片区纬度=CASE 片区编号\n{chr(10).join(lat_cases)}\n  ELSE 片区纬度 END\n"
        f"WHERE 片区编号 IN ({','.join(ids)});"
    )
    r = subprocess.run(
        ['mysql', f'-h{DB["host"]}', f'-P{DB["port"]}', f'-u{DB["user"]}',
         f'-p{DB["pwd"]}', DB['db']],
        input=sql, capture_output=True, text=True, env=os.environ,
    )
    if r.returncode == 0:
        print(f'\n  DB 更新: {len(ids)} 个片区 → GCJ-02 重心')
    else:
        print(f'  DB 更新失败: {r.stderr}', file=sys.stderr)
        sys.exit(1)


def main():
    transform_fn = load_transform()
    db_info = load_db_info(list(PATCH_TARGETS.keys()))

    area_features = []
    point_updates = {}
    db_coords = {}

    for pq_id, (kml_rel, folder_kw) in PATCH_TARGETS.items():
        info = db_info.get(pq_id)
        if not info:
            print(f'  ⚠ DB 无片区编号 {pq_id}，跳过')
            continue

        kml_path = os.path.join(KML_ROOT, kml_rel)
        print(f'\n[{pq_id}] {info["片区名称"]} ← {folder_kw}')
        raw_poly = extract_survey_polygon(kml_path, folder_kw)
        if raw_poly is None:
            print(f'  ✗ KML 未找到测绘多边形')
            continue

        geom, center = convert_polygon(raw_poly, transform_fn)
        print(f'  GCJ-02 center: {center[0]:.8f}, {center[1]:.8f}')

        props = {
            'name': info['片区名称'],
            'center': center,
            '基地名称': info['基地名称'],
            '区域名称': info['区域名称'],
            '片区编码': info['片区编码'],
            '片区编号': pq_id,
        }
        area_features.append({'type': 'Feature', 'properties': props, 'geometry': geom})
        point_updates[pq_id] = {
            'center': center,
            'geometry': {'type': 'Point', 'coordinates': center},
        }
        db_coords[pq_id] = center

    if not area_features:
        print('\n无可补丁数据，退出')
        sys.exit(1)

    print('\n更新 GeoJSON:')
    for fname in GEO_FILES:
        path = os.path.join(GEO_DIR, fname)
        if not os.path.exists(path):
            print(f'  ⚠ 跳过不存在: {fname}')
            continue
        if 'point' in fname:
            patch_point_file(path, point_updates)
        else:
            patch_area_file(path, area_features)

    update_db_coords(db_coords)

    # 验证
    print('\n验证 DB:')
    rows = mysql_query(
        'SELECT 片区编号,片区名称,片区经度,片区纬度 FROM ods_ag_base_v2 '
        f'WHERE 片区编号 IN ({",".join(str(i) for i in PATCH_TARGETS)})'
    )
    for r in rows:
        print(f'  #{r[0]} {r[1]}: {r[2]}, {r[3]}')

    # 仍 NULL 的记录
    null_rows = mysql_query(
        'SELECT 片区编号,片区名称 FROM ods_ag_base_v2 '
        'WHERE 片区经度 IS NULL OR 片区纬度 IS NULL ORDER BY 片区编号'
    )
    if null_rows:
        print('\n仍无坐标（KML 不可提取）:')
        for r in null_rows:
            print(f'  #{r[0]} {r[1]}')


if __name__ == '__main__':
    print('精准补丁：缺失片区 GeoJSON + DB 坐标')
    print('=' * 50)
    main()
    print('\n完成')
