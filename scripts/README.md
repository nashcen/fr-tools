# 农业大屏 — 开发脚本

**规范全文：** `openspec/specs/scripts.md`  
**版本台账：** `openspec/release-notes-scripts.md`  
**仓库：** `fr-tools`（自 P2025-G-001 全量目录迁移，路径已扁平化）

## 目录

| 路径 | 用途 |
|------|------|
| `active/` | 当前迭代唯一入口（日常只改这里）|
| `lib/` | 共享 Python 模块（被 import）|
| `ops/` | FineReport 本地运维 Shell |
| `versions/` | 与 GeoJSON 目录同名的版本快照 |

## 数据输入（本仓）

| 常量 / 用途 | 路径 |
|-------------|------|
| `KML_DIR` | `data/1.农业基地KML/` |
| `EXCEL_PATH` | `data/农业资产盘点明细.xlsx` |
| `GCJ02_DIR` | FineReport 部署目录（见 `active/geojson_generate_from_kml.py`）|

## 常用命令

```bash
# 生成 GeoJSON（活跃；输出至脚本内 GCJ02_DIR，当前为 v7.2）
python3 scripts/active/geojson_generate_from_kml.py

# 封板 v7.1 修复（勿改 FineReport 封板目录，仅复跑快照脚本）
python3 scripts/versions/农业基地_v7.1_GCJ02_MultiPolygon/geojson_fix_area_point_split.py

# 坐标转换（lib 模块，可被其他脚本加载）
python3 scripts/lib/coord_convert_wgs84_to_gcj02.py
```

## 命名约定（摘要）

- **脚本文件：** `{领域}_{动作}.py`（如 `geojson_generate_from_kml.py`），**禁止** `01_` 数字前缀
- **版本目录：** 与部署 GeoJSON 目录名一致，如 `农业基地_v7.2_GCJ02_MP_L2/`
- **共享/归档：** `versions/_shared/`、`versions/_archive/`
- **Shell：** `ops/fr_{动作}.sh`

> `versions/` 下各版本快照可能仍含旧项目绝对路径，复跑前请对照 `active/` 或 README 路径对照表。
