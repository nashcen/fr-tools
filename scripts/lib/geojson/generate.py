"""
Generate agri-base GeoJSON from KML + Excel + optional MySQL.
Version-specific output layout is controlled by GeojsonVersionProfile.
"""

from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path

from shapely.geometry import MultiPolygon as ShapelyMP
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry import shape
from shapely.ops import orient, unary_union

from lib import mysql_cli, settings
from lib.coord_convert_wgs84_to_gcj02 import transform
from lib.geojson import excel_hierarchy, kml_parser, plot_matching, writer, youyang_kml
from lib.geojson.kml_sources import BASE_SUFFIX, KML_FILES
from lib.geojson.profiles import GeojsonVersionProfile


def _active_bases() -> list[str]:
    filt = settings.geojson_bases_filter()
    if filt is None:
        return list(BASE_SUFFIX.keys())
    unknown = filt - set(BASE_SUFFIX)
    if unknown:
        raise ValueError(f"GEOJSON_BASES 未知基地: {', '.join(sorted(unknown))}")
    return [b for b in BASE_SUFFIX if b in filt]


def _bases_sql_in(bases: list[str]) -> str:
    return ", ".join(f"'{b}'" for b in bases)


def convert_coords(coords: list) -> list:
    return [list(transform(c[0], c[1])) for c in coords]


def _union_rings(rings_gcj: list) -> ShapelyPolygon | ShapelyMP | None:
    shapes = []
    for ring in rings_gcj:
        if len(ring) < 4:
            continue
        try:
            poly = shape({"type": "Polygon", "coordinates": [ring]})
            if not poly.is_valid:
                poly = poly.buffer(0)
            if poly.is_valid and not poly.is_empty:
                shapes.append(poly)
        except Exception:
            continue
    if not shapes:
        return None
    try:
        merged = unary_union(shapes)
        if not merged.is_valid:
            merged = merged.buffer(0)
        return merged
    except Exception:
        return None


def _geoms_oriented(merged) -> list:
    geoms = list(merged.geoms) if isinstance(merged, ShapelyMP) else [merged]
    return [
        orient(g, sign=1.0)
        for g in geoms
        if isinstance(g, ShapelyPolygon) and not g.is_empty
    ]


def _load_db_district_map(bases: list[str]) -> dict:
    if settings.skip_db():
        return {}
    rows = mysql_cli.query_rows(
        "SELECT 片区编号,基地名称,区域名称,片区编码,片区名称 "
        "FROM ods_ag_base_v2 "
        f"WHERE 基地名称 IN ({_bases_sql_in(bases)}) "
        "ORDER BY 片区编号",
        5,
    )
    db_map = {}
    for row in rows:
        db_map[(row[1], row[4])] = {
            "编号": int(row[0]),
            "区域名称": row[2],
            "片区编码": row[3],
        }
    return db_map


def _load_point_features(all_centroids: dict, bases: list[str]) -> list:
    if settings.skip_db():
        return []
    rows = mysql_cli.query_rows(
        "SELECT 片区编号,基地名称,区域名称,片区编码,片区名称,片区经度,片区纬度 "
        "FROM ods_ag_base_v2 "
        f"WHERE 基地名称 IN ({_bases_sql_in(bases)}) ORDER BY 片区编号",
        7,
    )
    point_features = []
    for row in rows:
        pid, base, region, pqcode, pq, lng_s, lat_s = row
        ctr = all_centroids.get((base, pq))
        if ctr:
            geom = {"type": "Point", "coordinates": ctr}
        elif lng_s != "NULL":
            geom = {"type": "Point", "coordinates": [float(lng_s), float(lat_s)]}
        else:
            geom = None
        props = {
            "name": pq,
            "center": ctr
            or (None if lng_s == "NULL" else [float(lng_s), float(lat_s)]),
            "基地名称": base,
            "区域名称": region,
            "片区编码": pqcode,
            "片区编号": int(pid),
        }
        point_features.append(
            {"type": "Feature", "properties": props, "geometry": geom}
        )
    return point_features


def _collect_kml_polygons(
    kml_dir: Path,
    excel_path: Path,
    bases: list[str],
):
    polys_by_district: dict = defaultdict(list)
    polys_by_plot_raw: dict = defaultdict(list)
    youyang_contract_map: dict[str, set[str]] | None = None
    youyang_districts: list[str] | None = None

    for label, cfg in KML_FILES.items():
        base = cfg["base"]
        if base not in bases:
            continue

        fpath = kml_dir / cfg["file"]
        if not fpath.is_file():
            print(f"  ⚠ 文件不存在，跳过: {cfg['file']}")
            continue

        placemarks = kml_parser.parse_kml(str(fpath))
        depth = cfg["depth"]
        folder_map = cfg["map"]

        if folder_map.get("__youyang__"):
            if youyang_contract_map is None:
                youyang_contract_map = excel_hierarchy.load_youyang_contract_district_map(
                    excel_path
                )
                hier = excel_hierarchy.load_excel_hierarchy(excel_path)
                youyang_districts = excel_hierarchy.youyang_district_names(hier)
            for pm in placemarks:
                if not kml_parser.should_keep(pm):
                    continue
                contract = pm["path"][2].strip() if len(pm["path"]) > 2 else ""
                district = youyang_kml.resolve_district(
                    pm["name"],
                    contract,
                    youyang_contract_map,
                    youyang_districts or [],
                )
                if not district:
                    print(f"  ⚠ 未匹配片区: {pm['name']} ({contract})")
                    continue
                polys_by_district[(base, district)].append(pm["coords"])
                polys_by_plot_raw[(base, district)].append((pm["name"], pm["coords"]))
        elif folder_map.get("__rebuild__"):
            for pm in placemarks:
                if not kml_parser.should_keep(pm):
                    continue
                mid_lat = sum(c[1] for c in pm["coords"]) / len(pm["coords"])
                district = "开向岭" if mid_lat > 29.0 else "祠堂坑"
                polys_by_district[(base, district)].append(pm["coords"])
                polys_by_plot_raw[(base, district)].append((pm["name"], pm["coords"]))
        else:
            for pm in placemarks:
                if not kml_parser.should_keep(pm):
                    continue
                folder = (
                    pm["path"][depth].strip()
                    if depth is not None and len(pm["path"]) > depth
                    else ""
                )
                district = folder_map.get(folder)
                if district:
                    polys_by_district[(base, district)].append(pm["coords"])
                    polys_by_plot_raw[(base, district)].append(
                        (pm["name"], pm["coords"])
                    )

        kept = sum(1 for pm in placemarks if kml_parser.should_keep(pm))
        print(f"  {label}: {kept}/{len(placemarks)} polygons kept")

    return polys_by_district, polys_by_plot_raw


def generate(profile: GeojsonVersionProfile) -> None:
    kml_dir = settings.kml_dir()
    excel_path = settings.excel_path()
    gcj02_dir = settings.geojson_output_dir(profile.version_dir)
    geo_v2_dir = settings.geojson_wgs84_dir()
    bases = _active_bases()

    print(f"版本: {profile.version_dir}")
    print(f"输出: {gcj02_dir}")
    if settings.geojson_bases_filter():
        print(f"基地过滤: {', '.join(bases)}（其余基地 KML/输出不处理）")

    db_map = _load_db_district_map(bases)
    polys_by_district, polys_by_plot_raw = _collect_kml_polygons(
        kml_dir, excel_path, bases
    )

    area_features = []
    all_centroids = {}

    for (base, district), polys_raw in polys_by_district.items():
        polys_gcj = [convert_coords(p) for p in polys_raw]
        merged = _union_rings(polys_gcj)
        if merged is None:
            continue
        geoms = _geoms_oriented(merged)
        if not geoms:
            continue
        centroid = merged.centroid
        c_lng, c_lat = round(centroid.x, 10), round(centroid.y, 10)
        all_centroids[(base, district)] = [c_lng, c_lat]
        db_info = db_map.get((base, district), {})
        area_features.append(
            {
                "type": "Feature",
                "properties": {
                    "name": district,
                    "center": [c_lng, c_lat],
                    "基地名称": base,
                    "区域名称": db_info.get("区域名称", ""),
                    "片区编码": db_info.get("片区编码", ""),
                    "片区编号": db_info.get("编号", 0),
                },
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        list(g.__geo_interface__["coordinates"]) for g in geoms
                    ],
                },
            }
        )

    print("\n步骤 3.5: 生成地块级 GeoJSON features...")
    excel_hier = excel_hierarchy.load_excel_hierarchy(excel_path)
    plot_features_by_pq: dict = defaultdict(list)

    for (base, district), items in polys_by_plot_raw.items():
        plots = excel_hier.get((base, district), [])
        by_plot: dict = defaultdict(list)
        for pm_name, raw_coords in items:
            plot_name = plot_matching.assign_to_plot(district, pm_name, plots)
            by_plot[plot_name].append(convert_coords(raw_coords))

        for plot_name, poly_list in by_plot.items():
            merged = _union_rings(poly_list)
            if merged is None:
                continue
            geoms = _geoms_oriented(merged)
            if not geoms:
                continue
            centroid = merged.centroid
            center = [round(centroid.x, 10), round(centroid.y, 10)]
            if len(geoms) == 1:
                feat_geom = {
                    "type": "Polygon",
                    "coordinates": list(geoms[0].__geo_interface__["coordinates"]),
                }
            else:
                feat_geom = {
                    "type": "MultiPolygon",
                    "coordinates": [
                        list(g.__geo_interface__["coordinates"]) for g in geoms
                    ],
                }
            plot_features_by_pq[(base, district)].append(
                {
                    "type": "Feature",
                    "properties": {"name": plot_name, "center": center},
                    "geometry": feat_geom,
                }
            )
        n = len(plot_features_by_pq.get((base, district), []))
        if n:
            print(f"  {base}/{district}: {n} 地块")

    print("\n步骤 3.6: 生成基地级 GeoJSON features...")
    base_features = []
    for base in bases:
        base_area = [f for f in area_features if f["properties"]["基地名称"] == base]
        if not base_area:
            continue
        shapes = []
        for feat in base_area:
            try:
                geom = shape(feat["geometry"])
                if not geom.is_valid:
                    geom = geom.buffer(0)
                if geom.is_valid and not geom.is_empty:
                    shapes.append(geom)
            except Exception:
                pass
        if not shapes:
            continue
        try:
            merged = unary_union(shapes)
            if not merged.is_valid:
                merged = merged.buffer(0)
        except Exception as exc:
            print(f"  ⚠ union 失败 {base}: {exc}")
            continue
        geoms = _geoms_oriented(merged)
        if not geoms:
            continue
        centroid = merged.centroid
        center = [round(centroid.x, 10), round(centroid.y, 10)]
        base_features.append(
            {
                "type": "Feature",
                "properties": {"name": base, "center": center},
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        list(g.__geo_interface__["coordinates"]) for g in geoms
                    ],
                },
            }
        )
        print(f"  {base}: 1 基地 feature ({len(geoms)} 个多边形)")

    point_features = _load_point_features(all_centroids, bases)

    if profile.write_l1_flat_per_base:
        print("\n步骤 5.1: 写出 v7.1 扁平 L1（*-area.json / *-point.json）...")
        for base, sfx in BASE_SUFFIX.items():
            if base not in bases:
                continue
            stem = f"农业基地_GCJ02_{sfx}"
            feats_area = [
                writer.v3_area_feature(f)
                for f in area_features
                if f["properties"]["基地名称"] == base
            ]
            feats_point = [
                writer.v3_point_feature(f)
                for f in point_features
                if f["properties"]["基地名称"] == base
            ]
            writer.write_geojson(
                gcj02_dir / f"{stem}-area.json",
                feats_area,
                top_name=base,
            )
            writer.write_geojson(
                gcj02_dir / f"{stem}-point.json",
                [x for x in feats_point if x],
            )

    if profile.write_legacy_merged:
        for base, sfx in BASE_SUFFIX.items():
            if base not in bases:
                continue
            feats_area = [
                writer.v3_area_feature(f)
                for f in area_features
                if f["properties"]["基地名称"] == base
            ]
            feats_point = [
                writer.v3_point_feature(f)
                for f in point_features
                if f["properties"]["基地名称"] == base
            ]
            writer.write_geojson(
                gcj02_dir / f"农业基地_GCJ02_{sfx}.json",
                feats_area + feats_point,
                top_name="农业基地",
            )

    if profile.write_layered_l1_l2_l3:
        print("\n步骤 5.2: 写出三层层级 GeoJSON...")
        writer.write_geojson(
            gcj02_dir / "农业基地-area.json",
            [
                writer.mk_area_feature(
                    f["properties"]["name"],
                    f["properties"]["center"],
                    f["geometry"],
                )
                for f in base_features
            ],
            top_name="农业基地",
        )
        writer.write_geojson(
            gcj02_dir / "农业基地-point.json",
            [
                x
                for x in [
                    writer.mk_point_feature(
                        f["properties"]["name"], f["properties"]["center"]
                    )
                    for f in base_features
                ]
                if x
            ],
        )

        level2_dir = gcj02_dir / "农业基地"
        for base in bases:
            pq_feats = [
                f for f in area_features if f["properties"]["基地名称"] == base
            ]
            writer.write_geojson(
                level2_dir / f"{base}-area.json",
                [
                    writer.mk_area_feature(
                        f["properties"]["name"],
                        f["properties"]["center"],
                        f["geometry"],
                    )
                    for f in pq_feats
                ],
                top_name=base,
            )
            writer.write_geojson(
                level2_dir / f"{base}-point.json",
                [
                    x
                    for x in [
                        writer.mk_point_feature(
                            f["properties"]["name"],
                            f["properties"].get("center"),
                        )
                        for f in pq_feats
                    ]
                    if x
                ],
            )

            if not pq_feats:
                continue
            level3_dir = level2_dir / base
            for pq_feat in pq_feats:
                pq_name = pq_feat["properties"]["name"]
                dk_feats = plot_features_by_pq.get((base, pq_name), [])
                if not dk_feats:
                    continue
                writer.write_geojson(
                    level3_dir / f"{pq_name}-area.json",
                    [
                        writer.mk_area_feature(
                            f["properties"]["name"],
                            f["properties"]["center"],
                            f["geometry"],
                        )
                        for f in dk_feats
                    ],
                    top_name=pq_name,
                )
                writer.write_geojson(
                    level3_dir / f"{pq_name}-point.json",
                    [
                        x
                        for x in [
                            writer.mk_point_feature(
                                f["properties"]["name"],
                                f["properties"].get("center"),
                            )
                            for f in dk_feats
                        ]
                        if x
                    ],
                )

    if profile.write_v2_wgs84_sidecar and settings.geojson_bases_filter() is None:
        writer.write_geojson(geo_v2_dir / "农业基地_v2.json", area_features)
        writer.write_geojson(geo_v2_dir / "农业基地_v2-area.json", area_features)
        writer.write_geojson(geo_v2_dir / "农业基地_v2-point.json", point_features)
        for base, sfx in BASE_SUFFIX.items():
            writer.write_geojson(
                geo_v2_dir / f"农业基地_v2_{sfx}.json",
                [f for f in area_features if f["properties"]["基地名称"] == base],
            )
            writer.write_geojson(
                geo_v2_dir / f"农业基地_v2_{sfx}-point.json",
                [f for f in point_features if f["properties"]["基地名称"] == base],
            )
    elif profile.write_v2_wgs84_sidecar:
        print("\n  ⊘ 跳过 v2 sidecar（GEOJSON_BASES 已限定基地）")

    if profile.update_db_coordinates and not settings.skip_db_update():
        lng_cases, lat_cases, ids = [], [], []
        for (base, district), (c_lng, c_lat) in all_centroids.items():
            info = db_map.get((base, district))
            if info:
                pid = info["编号"]
                lng_cases.append(f"  WHEN {pid} THEN {c_lng:.10f}")
                lat_cases.append(f"  WHEN {pid} THEN {c_lat:.10f}")
                ids.append(str(pid))
        if ids:
            sql = (
                f"UPDATE ods_ag_base_v2 SET\n"
                f"  片区经度=CASE 片区编号\n{chr(10).join(lng_cases)}\n"
                f"  ELSE 片区经度 END,\n"
                f"  片区纬度=CASE 片区编号\n{chr(10).join(lat_cases)}\n"
                f"  ELSE 片区纬度 END\n"
                f"WHERE 片区编号 IN ({','.join(ids)});"
            )
            mysql_cli.execute(sql)
            print(f"\n  DB 更新: {len(ids)} 个片区坐标 → GCJ-02 多边形重心")

    print(
        f"\n完成: {len(area_features)} 个片区（MultiPolygon）, "
        f"{len(point_features)} 个点位"
    )
