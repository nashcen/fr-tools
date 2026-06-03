# 农业大屏 — 开发脚本

**规范全文：** `openspec/specs/scripts.md`  
**版本台账：** `openspec/release-notes-scripts.md`

## 配置（.env）

复制 `.env.example` → `.env`，填写 `MYSQL_PASSWORD` 与 `FINEREPORT_WEBINF`。**禁止**在代码中硬编码密码或机器路径。

| 变量 | 含义 |
|------|------|
| `DATA_SOURCE_DIR` | 原始数据（默认 `data/source`）|
| `DATA_SINK_ROOT` | 生成根（默认 `data/sink`，其下为五版本目录）|
| `GEOJSON_VERSION` | sink 下版本子目录名 |
| `GEOJSON_OUTPUT_DIR` | 可选覆盖（pytest 临时目录）|
| `GEOJSON_PROTECT_EXISTING` | `1` 不覆盖已有 `.json` |
| `GEOJSON_SKIP_DB` | `1` 离线生成 |

## 目录

| 路径 | 用途 |
|------|------|
| `active/` | 当前迭代入口（调用 `lib/geojson`）|
| `lib/` | 共享模块：`settings`、`mysql_cli`、`geojson/*` |
| `lib/geojson/profiles.py` | **各版本输出差异**（L3 / 是否写 legacy 合并 json 等）|
| `ops/` | FineReport 运维脚本 |
| `versions/{GeoJSON目录名}/` | **版本入口**（薄封装，逻辑在 `lib`）|

## 常用命令

```bash
# 生成 → data/sink/农业基地_v7.4_GCJ02_L3_SingleMap/
python3 scripts/active/geojson_generate_from_kml.py

# 同步至 FineReport
./scripts/ops/sync_sink_map_to_finereport.sh 农业基地_v7.4_GCJ02_L3_SingleMap

# 指定封板版本（四图 v7.3）
python3 scripts/versions/农业基地_v7.3_GCJ02_L3/geojson_generate_from_kml.py

# 离线写入临时目录
GEOJSON_OUTPUT_DIR=/tmp/geo-out GEOJSON_PROTECT_EXISTING=0 GEOJSON_SKIP_DB=1 \
  MYSQL_PASSWORD=x python3 scripts/active/geojson_generate_from_kml.py

# 测试（计划见 tests/TEST_PLAN.md，用例表 tests/cases/geojson_test_cases.yaml）
pip install -r requirements-dev.txt
pytest

# 从封板目录生成 golden manifest（只读源目录）
python3 tests/tools/build_geojson_manifest.py \
  --source "$FINEREPORT_WEBINF/assets/map/geographic/农业基地-大疆测绘/农业基地_v7.4_GCJ02_L3_SingleMap" \
  --version 农业基地_v7.4_GCJ02_L3_SingleMap
```

## 版本与 GeoJSON 生成

| 版本目录 | 入口 | 配置 |
|----------|------|------|
| `农业基地_v7.0_GCJ02_Polygon` | `versions/.../geojson_generate_from_kml.py` | `profiles.py` |
| `农业基地_v7.2_GCJ02_MP_L2` | 同上 | 同上 |
| `农业基地_v7.3_GCJ02_L3` | 同上 | 同上 |
| `农业基地_v7.4_GCJ02_L3_SingleMap` | 同上 | 不写 legacy `农业基地_GCJ02_*.json` |

实现集中在 `lib/geojson/generate.py`；封板 GeoJSON **已有文件**默认不覆盖。
