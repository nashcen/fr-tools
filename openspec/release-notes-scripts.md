# 脚本版本台账

**文件：** `openspec/release-notes-scripts.md`  
**规范：** `openspec/specs/scripts.md`  
**最后更新：** 2026-06-03  
**活跃开发：** `scripts/active/`（fr-tools 仓根目录）  
**版本快照：** `scripts/versions/`

脚本版本目录名与 **GeoJSON 部署目录名** 完全一致。

> **2026-06-03：** 脚本已迁入 `fr-tools` 仓库；活跃路径为 `scripts/active/`，KML/Excel 输入为 `data/`。`versions/` 下历史快照若仍含旧绝对路径，以 `active/` 为准复跑。

---

## 目录结构（v1.0）

```
scripts/
  active/geojson_generate_from_kml.py
  lib/coord_convert_wgs84_to_gcj02.py
  ops/fr_*.sh
  versions/
    _shared/
    _archive/
    农业基地_v7.0_GCJ02_Polygon/
    农业基地_v7.1_GCJ02_MultiPolygon/
    农业基地_v7.2_GCJ02_MP_L2/
    农业基地_v7.3_GCJ02_L3/
    农业基地_v7.4_GCJ02_L3_SingleMap/
```

**命名：** `{领域}_{动作}.py`（废除 `01_`~`05_` 数字前缀）

---

## 版本总览

| 快照目录 | 对应 GeoJSON | 对应 FVS | 封板 | 脚本 |
|----------|--------------|----------|------|------|
| `_shared/` | （通用）| — | — | 坐标/补丁/DB/运维 |
| `_archive/` | `v2_WGS84` 等 | — | — | 旧 FR 兼容 |
| `农业基地_v7.0_GCJ02_Polygon/` | 同名 | `Agriculture_v7.0_GCJ02_Polygon.fvs` | ✅ | `geojson_generate_from_kml.py` |
| `农业基地_v7.1_GCJ02_MultiPolygon/` | 同名 | `Agriculture_v7.1_GCJ02_MultiPolygon.fvs` | ✅ | `geojson_fix_area_point_split.py` |
| `农业基地_v7.2_GCJ02_MP_L2/` | 同名 | `Agriculture_v7.2_GCJ02_MP_L2.fvs` | ✅ | `geojson_generate_from_kml.py` |
| `农业基地_v7.3_GCJ02_L3/` | 同名 | `Agriculture_v7.3_GCJ02_L3.fvs` | ✅ | `geojson_generate_from_kml.py` |
| `农业基地_v7.4_GCJ02_L3_SingleMap/` | 同名 | `Agriculture_v7.4_GCJ02_L3_SingleMap.fvs` | — | `geojson_generate_from_kml.py` |

---

## `_shared/` — 跨版本

| 脚本 | 作用 |
|------|------|
| `lib/coord_convert_wgs84_to_gcj02.py` | CGCS2000/WGS84 → GCJ-02 |
| `geojson_patch_missing_from_kml.py` | 补全缺失片区（import `lib/`）|
| `db_update_ods_ag_base_v2.py` | 回写 `ods_ag_base_v2` |
| `geojson_fix_area_point_split.py` | v7.1 area/point 分离（与 v7.1 快照相同）|
| `ops/fr_close_preview_tabs.sh` | 关闭 FR 预览 Tab |
| `ops/fr_kill_wait_port_8075.sh` | 重启 FR 调试 |

---

## `_archive/`

| 脚本 | 说明 |
|------|------|
| `geojson_explode_multipolygon_compat.py` | 旧 `v2_WGS84` MultiPolygon 展开；v7.0+ 不再使用 |

---

## `农业基地_v7.0_GCJ02_Polygon/` — 封板

| 项 | 值 |
|----|-----|
| `GCJ02_DIR` | `.../农业基地_v7.0_GCJ02_Polygon` |
| 输出 | 扁平 `农业基地_GCJ02_{CS,WS,BS,YY}.json` |

```bash
python3 scripts/versions/农业基地_v7.0_GCJ02_Polygon/geojson_generate_from_kml.py
```

---

## `农业基地_v7.1_GCJ02_MultiPolygon/` — 封板

| 项 | 值 |
|----|-----|
| 作用 | area/point 分离；删除无后缀 `.json` |

```bash
python3 scripts/versions/农业基地_v7.1_GCJ02_MultiPolygon/geojson_fix_area_point_split.py
```

---

## `农业基地_v7.2_GCJ02_MP_L2/` — 封板

| 项 | 值 |
|----|-----|
| `GCJ02_DIR` | `.../农业基地_v7.2_GCJ02_MP_L2` |
| 活跃副本 | `scripts/active/geojson_generate_from_kml.py`（同配置）|

```bash
python3 scripts/active/geojson_generate_from_kml.py
# 或快照：
python3 scripts/versions/农业基地_v7.2_GCJ02_MP_L2/geojson_generate_from_kml.py
```

---

## `农业基地_v7.3_GCJ02_L3/` — 封板（生产四图）

| 项 | 值 |
|----|-----|
| `GCJ02_DIR` | `.../农业基地_v7.3_GCJ02_L3` |
| 目标 | L3 基地 → 片区 → 地块 |

```bash
python3 scripts/versions/农业基地_v7.3_GCJ02_L3/geojson_generate_from_kml.py
```

---

## `农业基地_v7.4_GCJ02_L3_SingleMap/` — 单图试验

| 项 | 值 |
|----|-----|
| `GCJ02_DIR` | `.../农业基地_v7.4_GCJ02_L3_SingleMap` |
| 活跃 `active/` | 当前指向本目录 |
| FVS 运维 | `ops/fr_patch_v74_single_map.py` |

```bash
python3 scripts/active/geojson_generate_from_kml.py
```

---

## 旧名对照（迁移）

| 旧文件 | 新路径 |
|--------|--------|
| `01_coord_convert.py` | `lib/coord_convert_wgs84_to_gcj02.py` |
| `02_geojson_generate.py` | `active/geojson_generate_from_kml.py` |
| `03_geojson_patch_missing.py` | `versions/_shared/geojson_patch_missing_from_kml.py` |
| `03_db_update_ods_ag_base_v2.py` | `versions/_shared/db_update_ods_ag_base_v2.py` |
| `04_geojson_fix_finereport_compat.py` | `versions/_archive/geojson_explode_multipolygon_compat.py` |
| `05_geojson_fix_v71_finereport.py` | `versions/农业基地_v7.1_…/geojson_fix_area_point_split.py` |
| `versions/v7.x_*/` | `versions/农业基地_v7.x_*/` |
| `versions/common/` | `lib/` + `versions/_shared/` + `ops/` |

---

## 变更历史

| 日期 | 事件 |
|------|------|
| 2026-06-03 | 建立 `scripts/versions/` 分版本快照 |
| 2026-06-03 | v1.0 规范：`active/lib/ops/versions`；废除数字前缀；版本目录与 GeoJSON 同名 |
