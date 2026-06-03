#!/usr/bin/env python3
"""
【版本快照 农业基地_v7.1_GCJ02_MultiPolygon — 封板，勿改】
修复 农业基地_v7.1_GCJ02_MultiPolygon 目录下的 GeoJSON，使其符合 FineReport 地理信息规范。

根因：area（Polygon/MultiPolygon）与 point（Point）混写在同一 .json 中，
      FR「地图配置」区域 Tab 无法解析，区域列表为空。

规范（对照 world/中国）：
  - {名}-area.json  : 仅 Polygon/MultiPolygon，顶层 name = 区域显示名
  - {名}-point.json : 仅 Point，顶层无 name（properties 仅含 name）
  - ⛔ 禁止 {名}.json（无后缀）：会导致点地图显示异常，勿为 FVS 再生成合并文件

FVS geourl 必须指向 -area.json，例如：
  .../农业基地_v7.1_GCJ02_MultiPolygon/农业基地_GCJ02_CS-area.json

用法：
  python3 geojson_fix_area_point_split.py
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

V71_DIR = Path(
    '/Applications/FineReport/webapps/webroot/WEB-INF'
    '/assets/map/geographic/农业基地-大疆测绘/农业基地_v7.1_GCJ02_MultiPolygon'
)

BASE_META = {
    'CS': ('农业基地_GCJ02_CS', '浙江常山'),
    'WS': ('农业基地_GCJ02_WS', '四川武胜'),
    'BS': ('农业基地_GCJ02_BS', '广西百色'),
    'YY': ('农业基地_GCJ02_YY', '重庆酉阳'),
}

AREA_TYPES = frozenset({'Polygon', 'MultiPolygon'})


def load_fc(path: Path) -> dict:
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def save_fc(path: Path, data: dict) -> None:
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def is_valid_area(feat: dict) -> bool:
    geom = feat.get('geometry')
    if not geom or not geom.get('type'):
        return False
    return geom['type'] in AREA_TYPES and bool(geom.get('coordinates'))


def is_valid_point(feat: dict) -> bool:
    geom = feat.get('geometry')
    if not geom or geom.get('type') != 'Point':
        return False
    coords = geom.get('coordinates')
    return isinstance(coords, (list, tuple)) and len(coords) >= 2


def normalize_area_feature(feat: dict) -> dict:
    props = feat.get('properties') or {}
    name = props.get('name')
    center = props.get('center')
    out_props = {'name': name}
    if center and len(center) >= 2:
        out_props['center'] = [float(center[0]), float(center[1])]
    return {
        'type': 'Feature',
        'properties': out_props,
        'geometry': feat['geometry'],
    }


def normalize_point_feature(feat: dict) -> dict | None:
    props = feat.get('properties') or {}
    name = props.get('name')
    if not name:
        return None
    geom = feat.get('geometry')
    if not geom or geom.get('type') != 'Point':
        center = props.get('center')
        if center and len(center) >= 2:
            geom = {'type': 'Point', 'coordinates': [float(center[0]), float(center[1])]}
        else:
            return None
    coords = geom['coordinates']
    if not coords or len(coords) < 2:
        return None
    return {
        'type': 'Feature',
        'properties': {'name': name},
        'geometry': {'type': 'Point', 'coordinates': [float(coords[0]), float(coords[1])]},
    }


def split_mixed_fc(data: dict) -> tuple[list[dict], list[dict]]:
    area_feats: list[dict] = []
    point_feats: list[dict] = []
    for feat in data.get('features', []):
        geom = feat.get('geometry')
        if geom and geom.get('type') in AREA_TYPES:
            if is_valid_area(feat):
                area_feats.append(normalize_area_feature(feat))
        elif geom and geom.get('type') == 'Point':
            pt = normalize_point_feature(feat)
            if pt:
                point_feats.append(pt)
        elif not geom:
            pt = normalize_point_feature(feat)
            if pt:
                point_feats.append(pt)
    return area_feats, point_feats


def merge_points(primary: list[dict], extra: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for feat in primary:
        seen[feat['properties']['name']] = feat
    for feat in extra:
        n = feat['properties']['name']
        if n not in seen:
            seen[n] = feat
    return list(seen.values())


def remove_bare_json_files() -> list[str]:
    """删除无 -area/-point 后缀的合并文件（会导致点地图异常）。"""
    removed = []
    for p in V71_DIR.glob('农业基地_GCJ02_*.json'):
        if p.name.endswith('-area.json') or p.name.endswith('-point.json'):
            continue
        p.unlink()
        removed.append(p.name)
    return removed


def backup_dir(target: Path) -> Path:
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = target.parent / f'{target.name}.bak_{stamp}'
    shutil.copytree(target, bak)
    return bak


def fix_base(suffix: str, display_name: str, stem: str) -> dict:
    area_path = V71_DIR / f'{stem}-area.json'
    point_path = V71_DIR / f'{stem}-point.json'
    mixed_path = V71_DIR / f'{stem}.json'

    if area_path.exists() and point_path.exists():
        area_data = load_fc(area_path)
        point_data = load_fc(point_path)
        return {
            'suffix': suffix,
            'display_name': display_name,
            'area': len(area_data.get('features', [])),
            'point': len(point_data.get('features', [])),
            'skipped': True,
            'reason': 'already split',
        }

    source_path = mixed_path if mixed_path.exists() else area_path
    if not source_path.exists():
        return {'suffix': suffix, 'skipped': True, 'reason': 'no source json'}

    data = load_fc(source_path)
    area_feats, point_from_mixed = split_mixed_fc(data)

    extra_points: list[dict] = []
    if point_path.exists():
        for feat in load_fc(point_path).get('features', []):
            pt = normalize_point_feature(feat)
            if pt:
                extra_points.append(pt)

    point_feats = merge_points(point_from_mixed, extra_points)

    save_fc(area_path, {'type': 'FeatureCollection', 'name': display_name, 'features': area_feats})
    save_fc(point_path, {'type': 'FeatureCollection', 'features': point_feats})

    if mixed_path.exists():
        mixed_path.unlink()

    return {
        'suffix': suffix,
        'display_name': display_name,
        'area': len(area_feats),
        'point': len(point_feats),
    }


def main() -> None:
    if not V71_DIR.is_dir():
        raise SystemExit(f'目录不存在: {V71_DIR}')

    print('备份 v7.1 目录...')
    bak = backup_dir(V71_DIR)
    print(f'  → {bak}')

    print('\n修复 GeoJSON（仅保留 -area.json / -point.json）')
    print('=' * 60)
    for suffix, (stem, display_name) in BASE_META.items():
        r = fix_base(suffix, display_name, stem)
        if r.get('skipped'):
            print(f'  {suffix}: {r.get("reason")} area={r.get("area")} point={r.get("point")}')
        else:
            print(f'  {suffix} ({display_name}): area={r["area"]} point={r["point"]}')

    removed = remove_bare_json_files()
    if removed:
        print(f'\n已删除禁止的合并文件: {removed}')

    print('\n目录文件:')
    for p in sorted(V71_DIR.glob('农业基地_GCJ02_*.json')):
        print(f'  {p.name}')

    print('\n完成。FVS geourl 须指向 *-area.json；请在 FR「地图配置」同步地理文件。')


if __name__ == '__main__':
    main()
