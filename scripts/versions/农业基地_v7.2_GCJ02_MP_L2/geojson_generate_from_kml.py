"""
【版本快照 农业基地_v7.2_GCJ02_MP_L2 — 验证中，勿改】
农业基地片区边界 GeoJSON 生成脚本
===================================
功能：
  从 DJI 测绘 KML 文件中提取测绘面积边界，生成帆软大屏所需的 GeoJSON 文件。

三层层级（对照 FineReport 省/市内置地图规范）：
  基地（省）→ 片区（市）→ 地块（县）
  层级关系严格参照「农业资产盘点明细.xlsx」；片区 ID 参照 ods_ag_base_v2

输出（至 FineReport 地图资源目录）：

v7.2 L2 两层级（农业基地_v7.2_GCJ02_MP_L2/，对照 world/中国 → 中国/浙江省）：
  农业基地-area.json           层级1：基地（省）
  农业基地-point.json
  农业基地/
    {基地名}-area.json         层级2：片区（市）
    {基地名}-point.json

v3 三层层级（历史路径，现输出至 v7.2 目录，含 L3 地块子目录）：
  农业基地-area.json           基地级（4基地 MultiPolygon）
  农业基地-point.json
  农业基地/
    {基地名}-area.json         片区级（MultiPolygon，每片区一个）
    {基地名}-point.json
    {基地名}/
      {片区名}-area.json       地块级（Polygon/MultiPolygon）
      {片区名}-point.json

v3 GCJ-02 旧格式（兼容当前大屏 geourl，合并 area+point）：
  农业基地_GCJ02_CS/WS/BS/YY.json

v2 完整属性格式（农业基地_v2_WGS84/，DB 对账用）：
  农业基地_v2_{CS,WS,BS,YY}.json / -point.json

依赖：
  pip install shapely openpyxl
"""

import json
import math
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import defaultdict
from shapely.geometry import shape, MultiPolygon as MP, Polygon as SP
from shapely.ops import unary_union, orient

# ─── 配置 ─────────────────────────────────────────────────────────────────────

KML_DIR = (
    '/Users/cenl/docs/work/2025/4.项目管理/P2025-G-001-数智部-农业大屏一期  ★'
    '/5.数据设计/农业数据/6.片区边界/1.农业基地KML'
)
GEO_DIR = (
    '/Applications/FineReport/webapps/webroot/WEB-INF'
    '/assets/map/geographic/world/农业基地-大疆测绘/农业基地_v2_WGS84'
)
GCJ02_DIR = (
    '/Applications/FineReport/webapps/webroot/WEB-INF'
    '/assets/map/geographic/农业基地-大疆测绘/农业基地_v7.2_GCJ02_MP_L2'
)
# 历史路径（勿用）：.../world/农业基地-大疆测绘/农业基地_v3_GCJ02
EXCEL_PATH = (
    '/Users/cenl/docs/work/2025/4.项目管理/P2025-G-001-数智部-农业大屏一期  ★'
    '/5.数据设计/农业数据/6.片区边界/农业资产盘点明细.xlsx'
)
DB = dict(host='172.17.4.4', port=3310, user='bigdata',
          pwd='yxgbigdata@YXG321', db='yxg_bigscreen')

NS = 'http://www.opengis.net/kml/2.2'
Q = lambda t: f'{{{NS}}}{t}'

DISCARD_COLORS = {'#b620e0', '#ffbb00', '#19be6b'}

# KML 文件 → (基地名称, 文件夹层级, path[n] → 片区名称 映射)
KML_FILES = {
    '浙江常山_东区': {
        'file': '1.常山地图KML/东区_KML导出_20260602125704.kml',
        'base': '浙江常山',
        'depth': 2,
        'map': {
            '大埂基地': '大埂', '东乡基地': '东乡',
            '双溪口1基地': '双溪口1', '双溪口2基地': '双溪口2',
            '路里坑': '路里坑', '彭川基地KML': '彭川', '狮东基地': '狮东',
            # 东案基地 → 由东岸重画覆盖，此处跳过
        },
    },
    '浙江常山_东岸重画': {
        'file': '1.常山地图KML/东岸重画_KML导出_20260602125609.kml',
        'base': '浙江常山',
        'depth': None,   # 特殊处理：按纬度分配给 开向岭/祠堂坑
        'map': {'__rebuild__': True},
    },
    '浙江常山_西1区': {
        'file': '1.常山地图KML/西1区_KML导出_20260602125813.kml',
        'base': '浙江常山',
        'depth': 2,
        'map': {
            '草坪基地': '草坪', '景区基地': '景区',
            '十五里基地': '十五里', '育苗中心': '育苗中心',
        },
    },
    '浙江常山_西2区': {
        'file': '1.常山地图KML/西2区_KML导出_20260602125842.kml',
        'base': '浙江常山',
        'depth': 2,
        'map': {
            '曹会关基地': '曹会关', '和平基地': '和平', '金川基地': '金川',
            '天安基地': '天安', '新塘岭基地': '新塘岭', '新塘岭（新）': '新塘岭',
            '石坝基地': '石坝', '五联基地': '五联', '羊坳水库': '羊坳水库',
        },
    },
    '浙江常山_示范区': {
        'file': '1.常山地图KML/同弓示范区_KML导出_20260602125740.kml',
        'base': '浙江常山',
        'depth': 2,
        'map': {
            '同弓示范基地': '同弓示范基地',
            '同弓苗地': '同弓苗地',
            '同弓高换基地': '同弓高换基地',
        },
    },
    '四川武胜': {
        'file': '2.武胜地图KML/武胜地图KML导出_20260602130007.kml',
        'base': '四川武胜',
        'depth': 2,
        'map': {
            '三溪育苗基地': '三溪苗圃',
            '三溪西区639.8亩': '三溪西区', '三溪西区': '三溪西区',
            '三溪南区495.52': '三溪南区', '三溪南区495.52亩': '三溪南区',
            '三溪北区598.61亩': '三溪北区',
            '三溪东区596.77亩': '三溪东区',
            '金狮': '金狮', '幸福': '幸福', '干家湾': '干家湾宝箴塞',
            '穿岩洞、石门楼、五谷湾、保安': '穿岩', '桂花湾': '桂花湾',
            '响水': '响水滩', '小寨': '小寨', '观音塘': '观音塘',
            '嘉乐': '嘉乐', '龙头沟 ': '龙头沟', '龙头沟': '龙头沟',
            '吊井龙': '吊井龙', '望乡坪 266.9亩': '望乡坪', '望乡坪': '望乡坪',
            '沙溪': '沙溪', '桥亭': '桥亭1', '桥亭2': '桥亭2',
            '陈家寨2': '陈家寨2', '白果': '白果', '陈家寨1': '陈家寨1',
            '华家坪（新）': '华家坪', '华家坪': '华家坪',
            '象鼻': '象鼻', '涌泉': '会云', '会云': '会云',
            '龙兴': '龙兴', '九湾': '九湾', '方沟': '方沟',
            '天星桥': '天星桥', '李子坑': '李子坑', '应家沟': '应家沟',
            '尼姑庵': '尼姑庵', '花墙': '花墙',
            '飞龙3片': '飞龙3', '飞龙2片': '飞龙2', '飞龙1片': '飞龙1',
        },
    },
    '广西百色': {
        'file': '3.百色地图KML/百色地图KML导出_20260602125921.kml',
        'base': '广西百色',
        'depth': 1,   # 直接用 path[1] 作为片区名
        'map': {'平林': '平林', '龙细': '龙细'},
    },
}

BASE_SUFFIX = {
    '浙江常山': 'CS', '四川武胜': 'WS', '广西百色': 'BS', '重庆酉阳': 'YY'
}


# ─── KML 解析 ─────────────────────────────────────────────────────────────────

def kml2hex(c: str) -> str:
    c = c.lstrip('#')
    return f'#{c[6:8]}{c[4:6]}{c[2:4]}'.lower() if len(c) == 8 else c


def parse_kml(fpath: str) -> list[dict]:
    """解析 KML，返回 [{name, path, color, coords}] （仅 Polygon）"""
    tree = ET.parse(fpath)
    root = tree.getroot()

    styles = {}
    for s in root.iter(Q('Style')):
        sid = s.get('id', '')
        p = s.find(Q('PolyStyle'))
        if p is not None:
            c = p.find(Q('color'))
            if c is not None and c.text:
                styles[f'#{sid}'] = kml2hex(c.text)

    results = []

    def walk(el, path):
        for ch in el:
            t = ch.tag.replace(f'{{{NS}}}', '')
            if t in ('Folder', 'Document'):
                n = ch.find(Q('name'))
                fn = n.text.strip() if n is not None and n.text else ''
                walk(ch, path + ([fn] if fn else []))
            elif t == 'Placemark':
                n = ch.find(Q('name'))
                nm = n.text.strip() if n is not None and n.text else ''
                su = ch.find(Q('styleUrl'))
                color = (styles.get(su.text.strip(), '') if su is not None and su.text else '')
                poly_el = ch.find(Q('Polygon'))
                if poly_el is not None:
                    outer = poly_el.find(f'.//{Q("outerBoundaryIs")}/{Q("LinearRing")}/{Q("coordinates")}')
                    if outer is not None and outer.text:
                        coords = []
                        for pt in outer.text.strip().split():
                            parts = pt.split(',')
                            try:
                                coords.append([float(parts[0]), float(parts[1])])
                            except (ValueError, IndexError):
                                continue
                        if len(coords) >= 3:
                            ps = ' '.join(path).lower()
                            results.append({
                                'name': nm, 'path': list(path), 'color': color,
                                'is_seed': any(k in ps for k in ['种植', '种面']),
                                'coords': coords,
                            })
    walk(root, [])
    return results


def should_keep(pm: dict) -> bool:
    # 若 KML 文件夹路径含"测绘"，强制保留（忽略颜色）— 用于处理育苗中心等例外
    if '测绘' in ' '.join(pm['path']):
        return not pm['is_seed']
    return not pm['is_seed'] and pm['color'] not in DISCARD_COLORS


# ─── 坐标转换（天地图 → 高德，同 coord_convert.py）────────────────────────────

def _tl(x, y):
    r = -100+2*x+3*y+0.2*y*y+0.1*x*y+0.2*math.sqrt(abs(x))
    r += (20*math.sin(6*x*math.pi)+20*math.sin(2*x*math.pi))*2/3
    r += (20*math.sin(y*math.pi)+40*math.sin(y/3*math.pi))*2/3
    r += (160*math.sin(y/12*math.pi)+320*math.sin(y*math.pi/30))*2/3
    return r


def _tlg(x, y):
    r = 300+x+2*y+0.1*x*x+0.1*x*y+0.1*math.sqrt(abs(x))
    r += (20*math.sin(6*x*math.pi)+20*math.sin(2*x*math.pi))*2/3
    r += (20*math.sin(x*math.pi)+40*math.sin(x/3*math.pi))*2/3
    r += (150*math.sin(x/12*math.pi)+300*math.sin(x/30*math.pi))*2/3
    return r


def transform(lng, lat):
    a = 6378245.0; ee = 0.00669342162296594323
    if (lng < 72.004 or lng > 137.8347) or (lat < 0.8293 or lat > 55.8271):
        return lng, lat
    dlat = _tl(lng-105, lat-35); dlng = _tlg(lng-105, lat-35)
    rad = lat/180*math.pi; mg = math.sin(rad); mg = 1-ee*mg*mg; sq = math.sqrt(mg)
    dlat = dlat*180/((a*(1-ee))/(mg*sq)*math.pi)
    dlng = dlng*180/(a/sq*math.cos(rad)*math.pi)
    return lng+dlng, lat+dlat


def convert_coords(coords):
    return [list(transform(c[0], c[1])) for c in coords]


# ─── Excel 层级 + 地块名匹配 ──────────────────────────────────────────────────

def load_excel_hierarchy() -> dict:
    """从农业资产盘点明细.xlsx 读取 (基地,片区)→[地块名] 映射.
    地块名称严格参照此表，作为地块级 GeoJSON features 的 name 来源。
    """
    try:
        import openpyxl
    except ImportError:
        print('  ⚠ openpyxl 未安装（pip install openpyxl），跳过 Excel 层级')
        return {}
    wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    header = rows[0]
    h = {v: i for i, v in enumerate(header) if v}
    result: dict = defaultdict(list)
    seen: set = set()
    for row in rows[1:]:
        base = row[h['基地名称']] if '基地名称' in h else None
        pq = row[h['片区名称']] if '片区名称' in h else None
        dk = row[h['地块名称']] if '地块名称' in h else None
        if base and pq and dk:
            key = (base, pq, dk)
            if key not in seen:
                result[(base, pq)].append(dk)
                seen.add(key)
    return dict(result)


def normalize_for_match(raw: str) -> str:
    """归一化 KML Placemark 名称，用于匹配 Excel 地块名称.
    规则：去掉面积数字后缀，保留作为地块编号的数字（如平林9、三溪西区1）。
    """
    name = re.sub(r'-+\d+\.?\d*亩?$', '', raw)        # {n}-20.5亩 → {n}（带横线面积）
    name = re.sub(r'\d+\.?\d*亩$', '', name)            # {n}1.38亩 → {n}（无横线+有亩字）
    name = re.sub(r'地块\d+\.?\d*亩?$', '地块', name)   # {n}地块51 → {n}地块
    name = re.sub(r'（[\d\.]+亩?）$', '', name)          # （数字亩）
    name = re.sub(r'T\d+$', '', name)                   # Txxx 测绘编码
    name = re.sub(r'^（(.+)）$', r'\1', name)            # （名称）→ 名称
    name = re.sub(r'地块$', '', name)                    # {n}地块 → {n}
    name = re.sub(r'村$', '', name)                      # 弄坞村 → 弄坞
    return name.strip()


def assign_to_plot(pq: str, pm_name: str, plots: list) -> str:
    """将 KML 多边形分配到对应的地块名称.
    优先级：无 Excel 数据 → 以片区名整体 > 单地块 → 直接归入 > 精确 > 子串 > 归一化名称
    """
    if not plots:
        # 无 Excel 地块数据时，将整个片区作为单一地块（如九湾）
        return pq
    if len(plots) == 1:
        return plots[0]
    normalized = normalize_for_match(pm_name)
    if normalized in plots:
        return normalized
    for plot in plots:
        if plot in normalized or normalized in plot:
            return plot
    return normalized or pm_name


# ─── DB 查询 ──────────────────────────────────────────────────────────────────

def mysql(sql: str) -> list:
    r = subprocess.run(
        ['mysql', f'-h{DB["host"]}', f'-P{DB["port"]}', f'-u{DB["user"]}',
         f'-p{DB["pwd"]}', DB['db'], '--batch', '--skip-column-names', '-e', sql],
        capture_output=True, text=True, env=os.environ
    )
    return [l.split('\t') for l in r.stdout.strip().split('\n') if l]


# ─── 主生成逻辑 ───────────────────────────────────────────────────────────────

def generate():
    # 1. 从 DB 加载片区信息
    db_rows = mysql(
        "SELECT 片区编号,基地名称,区域名称,片区编码,片区名称 "
        "FROM ods_ag_base_v2 "
        "WHERE 基地名称 IN ('浙江常山','四川武胜','广西百色') "
        "ORDER BY 片区编号"
    )
    db_map = {}  # (基地名称, 片区名称) → {编号, 区域名称, 片区编码}
    for r in db_rows:
        if len(r) < 5: continue
        db_map[(r[1], r[4])] = {'编号': int(r[0]), '区域名称': r[2], '片区编码': r[3]}

    # 2. 按片区收集 polygon 坐标（CGCS2000）
    polys_by_district = defaultdict(list)   # (基地, 片区) → [coords_wgs84]
    polys_by_plot_raw = defaultdict(list)   # (基地, 片区) → [(pm_name, coords_wgs84)]

    for label, cfg in KML_FILES.items():
        fpath = os.path.join(KML_DIR, cfg['file'])
        if not os.path.exists(fpath):
            print(f'  ⚠ 文件不存在，跳过: {cfg["file"]}')
            continue

        pms = parse_kml(fpath)
        base = cfg['base']
        depth = cfg['depth']
        folder_map = cfg['map']

        if folder_map.get('__rebuild__'):
            # 东岸重画：按纬度分配
            for pm in pms:
                if not should_keep(pm): continue
                mid_lat = sum(c[1] for c in pm['coords']) / len(pm['coords'])
                pq = '开向岭' if mid_lat > 29.0 else '祠堂坑'
                polys_by_district[(base, pq)].append(pm['coords'])
                polys_by_plot_raw[(base, pq)].append((pm['name'], pm['coords']))
        else:
            for pm in pms:
                if not should_keep(pm): continue
                folder = pm['path'][depth].strip() if depth is not None and len(pm['path']) > depth else ''
                pq = folder_map.get(folder)
                if pq:
                    polys_by_district[(base, pq)].append(pm['coords'])
                    polys_by_plot_raw[(base, pq)].append((pm['name'], pm['coords']))

        n_kept = sum(1 for pm in pms if should_keep(pm))
        print(f'  {label}: {n_kept}/{len(pms)} polygons kept')

    # 3. 对每个片区做 union，转换坐标，计算重心
    area_features = []
    all_centroids = {}  # (基地, 片区) → [gcj_lng, gcj_lat]

    for (base, pq), polys_raw in polys_by_district.items():
        # 转换 CGCS2000 → GCJ-02
        polys_gcj = [convert_coords(p) for p in polys_raw]

        # 构建 shapely 多边形并 union（buffer(0) 修复无效几何）
        shapes = []
        for ring in polys_gcj:
            if len(ring) >= 4:
                try:
                    poly = shape({'type': 'Polygon', 'coordinates': [ring]})
                    if not poly.is_valid:
                        poly = poly.buffer(0)
                    if poly.is_valid and not poly.is_empty:
                        shapes.append(poly)
                except Exception:
                    pass
        if not shapes:
            continue

        try:
            merged = unary_union(shapes)
            if not merged.is_valid:
                merged = merged.buffer(0)
        except Exception as e:
            print(f'  ⚠ union 失败 {pq}: {e}')
            continue

        centroid = merged.centroid
        c_lng, c_lat = round(centroid.x, 10), round(centroid.y, 10)
        all_centroids[(base, pq)] = [c_lng, c_lat]

        db_info = db_map.get((base, pq), {})
        props = {
            'name': pq,
            'center': [c_lng, c_lat],
            '基地名称': base,
            '区域名称': db_info.get('区域名称', ''),
            '片区编码': db_info.get('片区编码', ''),
            '片区编号': db_info.get('编号', 0),
        }

        # 每个片区输出一个 MultiPolygon feature（RFC 7946，外环 CCW）
        geoms = list(merged.geoms) if isinstance(merged, MP) else [merged]
        geoms = [orient(g, sign=1.0) for g in geoms if isinstance(g, SP) and not g.is_empty]
        if not geoms:
            continue
        multi_coords = [list(g.__geo_interface__['coordinates']) for g in geoms]
        area_features.append({
            'type': 'Feature',
            'properties': props,
            'geometry': {'type': 'MultiPolygon', 'coordinates': multi_coords},
        })

    # 3.5. 生成地块级 features（Polygon/MultiPolygon，按地块名归并）
    # 地块名称严格参照 农业资产盘点明细.xlsx，片区 ID 参照 ods_ag_base_v2
    print('\n步骤 3.5: 生成地块级 GeoJSON features...')
    excel_hier = load_excel_hierarchy()
    plot_features_by_pq: dict = defaultdict(list)  # (base, pq) → [地块 features]

    for (base, pq), items in polys_by_plot_raw.items():
        plots = excel_hier.get((base, pq), [])
        by_dk: dict = defaultdict(list)
        for pm_name, raw_coords in items:
            dk_name = assign_to_plot(pq, pm_name, plots)
            by_dk[dk_name].append(convert_coords(raw_coords))

        for dk_name, poly_list in by_dk.items():
            shapes = []
            for ring in poly_list:
                if len(ring) >= 4:
                    try:
                        poly = shape({'type': 'Polygon', 'coordinates': [ring]})
                        if not poly.is_valid:
                            poly = poly.buffer(0)
                        if poly.is_valid and not poly.is_empty:
                            shapes.append(poly)
                    except Exception:
                        pass
            if not shapes:
                continue
            try:
                merged = unary_union(shapes)
                if not merged.is_valid:
                    merged = merged.buffer(0)
            except Exception as e:
                print(f'  ⚠ union 失败 {pq}/{dk_name}: {e}')
                continue

            centroid = merged.centroid
            center = [round(centroid.x, 10), round(centroid.y, 10)]
            geoms = list(merged.geoms) if isinstance(merged, MP) else [merged]
            geoms = [orient(g, sign=1.0) for g in geoms if isinstance(g, SP) and not g.is_empty]
            if not geoms:
                continue

            if len(geoms) == 1:
                feat_geom = {
                    'type': 'Polygon',
                    'coordinates': list(geoms[0].__geo_interface__['coordinates']),
                }
            else:
                feat_geom = {
                    'type': 'MultiPolygon',
                    'coordinates': [list(g.__geo_interface__['coordinates']) for g in geoms],
                }
            plot_features_by_pq[(base, pq)].append({
                'type': 'Feature',
                'properties': {'name': dk_name, 'center': center},
                'geometry': feat_geom,
            })

        n = len(plot_features_by_pq.get((base, pq), []))
        if n:
            print(f'  {base}/{pq}: {n} 地块')

    # 3.6. 生成基地级 features（各基地所有片区 union）
    print('\n步骤 3.6: 生成基地级 GeoJSON features...')
    base_features = []
    for base, sfx in BASE_SUFFIX.items():
        base_area_feats = [f for f in area_features if f['properties']['基地名称'] == base]
        if not base_area_feats:
            continue
        shapes = []
        for feat in base_area_feats:
            try:
                s = shape(feat['geometry'])
                if not s.is_valid:
                    s = s.buffer(0)
                if s.is_valid and not s.is_empty:
                    shapes.append(s)
            except Exception:
                pass
        if not shapes:
            continue
        try:
            merged = unary_union(shapes)
            if not merged.is_valid:
                merged = merged.buffer(0)
        except Exception as e:
            print(f'  ⚠ union 失败 {base}: {e}')
            continue
        centroid = merged.centroid
        center = [round(centroid.x, 10), round(centroid.y, 10)]
        geoms = list(merged.geoms) if isinstance(merged, MP) else [merged]
        geoms = [orient(g, sign=1.0) for g in geoms if isinstance(g, SP) and not g.is_empty]
        if not geoms:
            continue
        base_features.append({
            'type': 'Feature',
            'properties': {'name': base, 'center': center},
            'geometry': {
                'type': 'MultiPolygon',
                'coordinates': [list(g.__geo_interface__['coordinates']) for g in geoms],
            },
        })
        print(f'  {base}: 1 基地 feature ({len(geoms)} 个多边形)')

    # 4. 加载所有 DB 片区（含无边界）作为 point features
    all_db = mysql(
        "SELECT 片区编号,基地名称,区域名称,片区编码,片区名称,片区经度,片区纬度 "
        "FROM ods_ag_base_v2 "
        "WHERE 基地名称 IN ('浙江常山','四川武胜','广西百色') ORDER BY 片区编号"
    )
    point_features = []
    for r in all_db:
        if len(r) < 7: continue
        pid, base, region, pqcode, pq, lng_s, lat_s = r
        ctr = all_centroids.get((base, pq))
        if ctr:
            geom = {'type': 'Point', 'coordinates': ctr}
        elif lng_s != 'NULL':
            geom = {'type': 'Point', 'coordinates': [float(lng_s), float(lat_s)]}
        else:
            geom = None
        props = {
            'name': pq, 'center': ctr or (None if lng_s == 'NULL' else [float(lng_s), float(lat_s)]),
            '基地名称': base, '区域名称': region, '片区编码': pqcode, '片区编号': int(pid),
        }
        point_features.append({'type': 'Feature', 'properties': props, 'geometry': geom})

    # 5. 写出文件
    def write_geo(path, feats, top_name=None):
        fc = {'type': 'FeatureCollection', 'features': feats}
        if top_name:
            fc['name'] = top_name
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(fc, f, ensure_ascii=False)
        print(f'  → {os.path.basename(path)}: {len(feats)} features')

    def v3_area_feat(feat):
        return {
            'type': 'Feature',
            'properties': {
                'name': feat['properties']['name'],
                'center': feat['properties']['center'],
            },
            'geometry': feat['geometry'],
        }

    def v3_point_feat(feat):
        center = feat['properties']['center']
        return {
            'type': 'Feature',
            'properties': {
                'name': feat['properties']['name'],
                'center': center,
            },
            'geometry': {'type': 'Point', 'coordinates': center} if center else None,
        }

    # v3 GCJ-02 格式（大屏 geourl 使用）
    # 区域（MultiPolygon）+ 点（Point）合并在同一文件，FineReport 分别在「区域」和「点」tab 显示
    os.makedirs(GCJ02_DIR, exist_ok=True)
    for base, sfx in BASE_SUFFIX.items():
        feats_area = [v3_area_feat(f) for f in area_features if f['properties']['基地名称'] == base]
        feats_point = [v3_point_feat(f) for f in point_features if f['properties']['基地名称'] == base]
        write_geo(os.path.join(GCJ02_DIR, f'农业基地_GCJ02_{sfx}.json'),
                  feats_area + feats_point, top_name='农业基地')

    # v3 GCJ-02 三层层级输出（FR 标准 area.json/point.json 分离格式）
    # 层级：基地（省）→ 片区（市）→ 地块（县）
    print('\n步骤 5.2: 写出三层层级 GeoJSON...')

    def mk_area_feat(name, center, geometry):
        return {'type': 'Feature', 'properties': {'name': name, 'center': center},
                'geometry': geometry}

    def mk_point_feat(name, center):
        if not center:
            return None
        return {'type': 'Feature', 'properties': {'name': name},
                'geometry': {'type': 'Point', 'coordinates': center}}

    # 层级1：基地级（4个基地 MultiPolygon）
    write_geo(os.path.join(GCJ02_DIR, '农业基地-area.json'),
              [mk_area_feat(f['properties']['name'], f['properties']['center'], f['geometry'])
               for f in base_features],
              top_name='农业基地')
    pt_base = [mk_point_feat(f['properties']['name'], f['properties']['center'])
               for f in base_features]
    write_geo(os.path.join(GCJ02_DIR, '农业基地-point.json'),
              [x for x in pt_base if x])

    # 层级2：片区级（各基地的片区 MultiPolygon）
    level2_dir = os.path.join(GCJ02_DIR, '农业基地')
    os.makedirs(level2_dir, exist_ok=True)
    for base, sfx in BASE_SUFFIX.items():
        pq_feats = [f for f in area_features if f['properties']['基地名称'] == base]
        write_geo(os.path.join(level2_dir, f'{base}-area.json'),
                  [mk_area_feat(f['properties']['name'], f['properties']['center'],
                                f['geometry']) for f in pq_feats],
                  top_name=base)
        write_geo(os.path.join(level2_dir, f'{base}-point.json'),
                  [x for x in [mk_point_feat(f['properties']['name'],
                                              f['properties'].get('center'))
                                for f in pq_feats] if x])

    # 层级3：地块级（各片区的地块 Polygon/MultiPolygon）
    for base, sfx in BASE_SUFFIX.items():
        pq_feats = [f for f in area_features if f['properties']['基地名称'] == base]
        if not pq_feats:
            continue
        level3_dir = os.path.join(level2_dir, base)
        os.makedirs(level3_dir, exist_ok=True)
        for pq_feat in pq_feats:
            pq_name = pq_feat['properties']['name']
            dk_feats = plot_features_by_pq.get((base, pq_name), [])
            if not dk_feats:
                continue
            write_geo(os.path.join(level3_dir, f'{pq_name}-area.json'),
                      [mk_area_feat(f['properties']['name'], f['properties']['center'],
                                    f['geometry']) for f in dk_feats],
                      top_name=pq_name)
            write_geo(os.path.join(level3_dir, f'{pq_name}-point.json'),
                      [x for x in [mk_point_feat(f['properties']['name'],
                                                  f['properties'].get('center'))
                                    for f in dk_feats] if x])

    # v2 完整属性格式（DB 对账用）
    os.makedirs(GEO_DIR, exist_ok=True)
    write_geo(os.path.join(GEO_DIR, '农业基地_v2.json'), area_features)
    write_geo(os.path.join(GEO_DIR, '农业基地_v2-area.json'), area_features)
    write_geo(os.path.join(GEO_DIR, '农业基地_v2-point.json'), point_features)

    for base, sfx in BASE_SUFFIX.items():
        write_geo(os.path.join(GEO_DIR, f'农业基地_v2_{sfx}.json'),
                  [f for f in area_features if f['properties']['基地名称'] == base])
        write_geo(os.path.join(GEO_DIR, f'农业基地_v2_{sfx}-point.json'),
                  [f for f in point_features if f['properties']['基地名称'] == base])

    # 6. 更新 DB 坐标
    lng_cases, lat_cases, ids = [], [], []
    for (base, pq), (c_lng, c_lat) in all_centroids.items():
        info = db_map.get((base, pq))
        if info:
            pid = info['编号']
            lng_cases.append(f'  WHEN {pid} THEN {c_lng:.10f}')
            lat_cases.append(f'  WHEN {pid} THEN {c_lat:.10f}')
            ids.append(str(pid))

    if ids:
        sql = (f"UPDATE ods_ag_base_v2 SET\n"
               f"  片区经度=CASE 片区编号\n{chr(10).join(lng_cases)}\n  ELSE 片区经度 END,\n"
               f"  片区纬度=CASE 片区编号\n{chr(10).join(lat_cases)}\n  ELSE 片区纬度 END\n"
               f"WHERE 片区编号 IN ({','.join(ids)});")
        result = subprocess.run(
            ['mysql', f'-h{DB["host"]}', f'-P{DB["port"]}', f'-u{DB["user"]}',
             f'-p{DB["pwd"]}', DB['db']],
            input=sql, capture_output=True, text=True, env=os.environ
        )
        if result.returncode == 0:
            print(f'\n  DB 更新: {len(ids)} 个片区坐标 → GCJ-02 多边形重心')
        else:
            print(f'  DB 更新失败: {result.stderr[:200]}')

    print(f'\n完成: {len(area_features)} 个片区（MultiPolygon）, {len(point_features)} 个点位')


if __name__ == '__main__':
    print('生成农业基地片区 GeoJSON...')
    generate()
