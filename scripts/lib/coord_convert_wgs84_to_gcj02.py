"""
坐标转换工具：天地图(CGCS2000) → 高德地图(GCJ-02)
======================================================
背景：
  - DJI 大疆无人机测绘数据默认输出天地图坐标系（CGCS2000，近似等于 WGS-84）
  - 帆软 FineReport 卫星底图使用高德坐标系（GCJ-02，即"火星坐标系"）
  - 两者在中国境内存在约 200-500m 偏移，需转换后才能对齐

用法：
  python lib/coord_convert_wgs84_to_gcj02.py

输出：
  将源 GeoJSON 文件中的所有坐标点从 CGCS2000 转为 GCJ-02
  同时转换 properties.center 属性
"""

import json
import math
import os
import sys


# ─── 核心转换算法 ────────────────────────────────────────────────────────────

def _transform_lat(lng: float, lat: float) -> float:
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 *
            math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * math.pi) + 40.0 *
            math.sin(lat / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * math.pi) + 320 *
            math.sin(lat * math.pi / 30.0)) * 2.0 / 3.0
    return ret


def _transform_lng(lng: float, lat: float) -> float:
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 *
            math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * math.pi) + 40.0 *
            math.sin(lng / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * math.pi) + 300.0 *
            math.sin(lng / 30.0 * math.pi)) * 2.0 / 3.0
    return ret


def transform(lng: float, lat: float) -> tuple[float, float]:
    """CGCS2000(≈WGS-84) → GCJ-02，中国境外原样返回"""
    a = 6378245.0
    ee = 0.00669342162296594323

    if (lng < 72.004 or lng > 137.8347) or (lat < 0.8293 or lat > 55.8271):
        return lng, lat

    dlat = _transform_lat(lng - 105.0, lat - 35.0)
    dlng = _transform_lng(lng - 105.0, lat - 35.0)

    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)

    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * math.pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * math.pi)

    return lng + dlng, lat + dlat


# ─── GeoJSON 批量转换 ────────────────────────────────────────────────────────

def _convert_coord(coord: list) -> list:
    g, l = transform(coord[0], coord[1])
    return [g, l] + list(coord[2:]) if len(coord) > 2 else [g, l]


def convert_geojson(geojson: dict) -> dict:
    """转换 GeoJSON FeatureCollection 中所有坐标，同时转换 center 属性"""
    for feat in geojson.get('features', []):
        geom = feat.get('geometry')
        if not geom:
            continue
        t = geom['type']
        if t == 'Polygon':
            geom['coordinates'] = [
                [_convert_coord(c) for c in ring]
                for ring in geom['coordinates']
            ]
        elif t == 'MultiPolygon':
            geom['coordinates'] = [
                [[_convert_coord(c) for c in ring] for ring in poly]
                for poly in geom['coordinates']
            ]
        elif t == 'Point':
            geom['coordinates'] = _convert_coord(geom['coordinates'])

        ctr = feat.get('properties', {}).get('center')
        if ctr and len(ctr) >= 2:
            feat['properties']['center'] = list(transform(ctr[0], ctr[1]))

    return geojson


# ─── 主函数 ──────────────────────────────────────────────────────────────────

def convert_file(src: str, dst: str) -> None:
    with open(src, encoding='utf-8') as f:
        data = json.load(f)
    converted = convert_geojson(data)
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(converted, f, ensure_ascii=False)
    n = len(converted.get('features', []))
    print(f'  {os.path.basename(src)} → {os.path.basename(dst)}: {n} features')


if __name__ == '__main__':
    # 默认转换项目 GeoJSON 目录中的 农业基地.json
    GEO_DIR = '/Applications/FineReport/webapps/webroot/WEB-INF/assets/map/geographic/world/农业基地-大疆测绘/农业基地_v2_WGS84'
    src = os.path.join(GEO_DIR, '农业基地_v2_raw.json')   # 原始 CGCS2000 文件
    dst = os.path.join(GEO_DIR, '农业基地_v2.json')        # 输出 GCJ-02 文件

    if not os.path.exists(src):
        print(f'源文件不存在: {src}')
        sys.exit(1)

    print('开始转换 CGCS2000 → GCJ-02...')
    convert_file(src, dst)

    # 验证：路里坑偏移
    test_lng, test_lat = 118.5174286, 28.99795452
    g_lng, g_lat = transform(test_lng, test_lat)
    d_e = (g_lng - test_lng) * 111320 * math.cos(test_lat * math.pi / 180)
    d_n = (g_lat - test_lat) * 111320
    print(f'\n[验证] 路里坑 CGCS2000→GCJ02: Δ东={d_e:.0f}m, Δ北={d_n:.0f}m')
    print('转换完成')
