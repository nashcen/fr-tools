#!/usr/bin/env python3
"""
将 v2 GeoJSON 转为帆软区域地图兼容格式：
  1. FeatureCollection 增加 name=农业基地（与 GCJ02 一致）
  2. MultiPolygon 拆成多个 Polygon feature（同名，与 GCJ02 结构一致）

帆软 VanChart AREA_MAP 对 MultiPolygon 支持不完整，会导致片区边界不显示。
"""

import json
import os
import sys

GEO_DIR = (
    '/Applications/FineReport/webapps/webroot/WEB-INF'
    '/assets/map/geographic/world/农业基地-大疆测绘/农业基地_v2_WGS84'
)

TARGET_FILES = [
    '农业基地_v2.json',
    '农业基地_v2-area.json',
    '农业基地_v2_CS.json',
    '农业基地_v2_WS.json',
    '农业基地_v2_BS.json',
]


def explode_feature(feat: dict) -> list[dict]:
    """MultiPolygon → 多个 Polygon feature；Polygon 原样返回。"""
    geom = feat.get('geometry')
    if not geom:
        return [feat]

    props = feat['properties']
    gtype = geom['type']

    if gtype == 'Polygon':
        return [feat]

    if gtype == 'MultiPolygon':
        out = []
        for poly_coords in geom['coordinates']:
            out.append({
                'type': 'Feature',
                'properties': dict(props),
                'geometry': {'type': 'Polygon', 'coordinates': poly_coords},
            })
        return out

    return [feat]


def convert_file(path: str) -> None:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    new_features = []
    mp_count = 0
    poly_count = 0

    for feat in data.get('features', []):
        exploded = explode_feature(feat)
        for f2 in exploded:
            if f2['geometry']['type'] == 'Polygon':
                poly_count += 1
            new_features.append(f2)
        if feat.get('geometry', {}).get('type') == 'MultiPolygon':
            mp_count += 1

    data['type'] = 'FeatureCollection'
    data['name'] = '农业基地'
    data['features'] = new_features

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    print(f'  {os.path.basename(path)}: {mp_count} MultiPolygon → {poly_count} Polygon features')


def main():
    print('帆软兼容：MultiPolygon → Polygon + 添加 name 字段')
    print('=' * 50)
    for fname in TARGET_FILES:
        path = os.path.join(GEO_DIR, fname)
        if not os.path.exists(path):
            print(f'  ⚠ 跳过: {fname}')
            continue
        convert_file(path)
    print('\n完成。请刷新大屏（必要时重启 FineReport 或清浏览器缓存）。')


if __name__ == '__main__':
    main()
