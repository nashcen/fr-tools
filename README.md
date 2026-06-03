# fr-tools — P2025-G-001 农业大屏（精简仓）

**项目编号：** `P2025-G-001`（数智部 · 农业大屏一期）  
**本仓库：** 自原项目管理目录 **迁移** 后的迭代专用仓，仅保留日常开发所需的核心资产。

**当前生产基线（封板）：** `v7.4` 单图 — `Agriculture_v7.4_GCJ02_L3_SingleMap.fvs` + `农业基地_v7.4_GCJ02_L3_SingleMap/`（组件 `区域地图`，L1 geourl）。  
**可回退：** `v7.3` 四图、`v7.2` L2、`v7.1` L1、`v7.0` Polygon（见 `CLAUDE.md` **12** 项 FROZEN）。  
**验收（2026-06-03）：** v7.0–v7.4 已在 FineReport 手工验证；重庆酉阳 7 片区可正常展示（9 片区待 KML，见 `openspec/specs/geojson.md`）。

---

## 为何迁移

原目录 `P2025-G-001-数智部-农业大屏一期 ★/` 按「项目全生命周期」展开（规划、跟踪、调研、原型、数据设计、开发实现等），积累大量 **一次性文档、历史脚本编号、重复说明**，与 `openspec/` 规范并存，难以判断「哪份有效、改哪里」，严重拖慢 v7 及后续版本迭代。

**本仓原则：**

| 保留在本仓 | 不纳入本仓（仍在 FineReport / 原项目盘） |
|------------|------------------------------------------|
| `openspec/` 规范与版本台账 | FVS 模板（`WEB-INF/reportlets/.../5.农业大屏二期/`） |
| `scripts/` 活跃脚本 + 版本快照 | 生产 GeoJSON（`WEB-INF/assets/map/geographic/农业基地-大疆测绘/`） |
| `data/source/` 原始 KML、Excel；`data/sink/` 生成 GeoJSON（五版本目录） | 蓝图、会议纪要、UI 切图、DB DDL 归档等 |

规范与封板规则仍以 **`openspec/` + `CLAUDE.md`** 为唯一真相源；运行时大屏资源在 **FineReport 安装目录**，不在 Git 中。

---

## 目录结构

```
fr-tools/
├── README.md                 # 本说明
├── CLAUDE.md                 # 封板保护、关键路径（AI / 人工必读）
├── data/
│   ├── source/               # 原始输入（KML、Excel、归档 JSON）
│   └── sink/                   # 生成 GeoJSON（五版本目录直接在 sink 下）
├── scripts/
│   ├── active/               # 日常只改此处
│   ├── lib/                  # 共享模块（坐标转换等）
│   ├── ops/                  # FineReport 本地运维 Shell
│   └── versions/             # 与 GeoJSON 目录同名的脚本快照
└── openspec/
    ├── project.md            # 项目约定、版本史、与本仓关系
    ├── specs/                # bigscreen / geojson / scripts
    ├── release-notes-*.md    # FVS / GeoJSON / 脚本台账
    ├── changes/              # 进行中的 OpenSpec 变更
    └── archive/              # 已归档变更
```

---

## scripts / source / sink 对应关系

**数据流：** `data/source`（只读输入）→ `scripts/lib/geojson`（生成逻辑）→ `data/sink/{版本}/`（GCJ-02 产物，纳入 Git）→ 可选 `sync_sink_map_to_finereport.sh` → FineReport `WEB-INF/.../农业基地-大疆测绘/{版本}/`。

### 公共部分（五版本共用）

| 项 | 路径 / 说明 |
|----|-------------|
| **source · KML** | `data/source/1.农业基地KML/` |
| **source · 盘点表** | `data/source/农业资产盘点明细.xlsx` |
| **source · 参考 JSON** | `data/source/2.农业基地JSON/`（归档只读，非生成入口）|
| **source · v2 sidecar** | `data/source/农业基地_v2_WGS84/`（v7.0/7.2/7.3/7.4 生成时写入；v7.1 不写）|
| **实现（勿直接改快照）** | `scripts/lib/geojson/`（`generate.py`、`profiles.py`、`cli.py`）|
| **日常入口（默认 v7.4）** | `scripts/active/geojson_generate_from_kml.py` |
| **五版本一次生成** | `./scripts/ops/generate_all_sink_versions.sh` |
| **部署 FR** | `./scripts/ops/sync_sink_map_to_finereport.sh {版本目录名}` |
| **全量测试** | `MYSQL_PASSWORD=test pytest tests/ -v`（会话级写满 `data/sink/` 五目录）|
| **结构回归 golden** | `tests/golden/geojson/{版本}/manifest.json` + `tests/test_all_versions.py` |

离线生成建议环境变量：`GEOJSON_SKIP_DB=1`、`GEOJSON_PROTECT_EXISTING=0`、`MYSQL_PASSWORD=test`（不连库）。

### 按版本对照（v7.0–v7.4）

| GeoJSON 版本目录（= `GEOJSON_VERSION`）| 脚本入口（`scripts/versions/…`）| sink 输出目录 | 生成命令（单版本）| 测试命令（单版本结构回归）| 产物概要 |
|--------------------------------------|----------------------------------|---------------|-------------------|---------------------------|----------|
| `农业基地_v7.0_GCJ02_Polygon` | `农业基地_v7.0_GCJ02_Polygon/geojson_generate_from_kml.py` | `data/sink/农业基地_v7.0_GCJ02_Polygon/` | `python3 scripts/versions/农业基地_v7.0_GCJ02_Polygon/geojson_generate_from_kml.py` | `pytest "tests/test_all_versions.py::test_generate_matches_golden_manifest[农业基地_v7.0_GCJ02_Polygon]" -v` | 4× `农业基地_GCJ02_{CS,WS,BS,YY}.json` |
| `农业基地_v7.1_GCJ02_MultiPolygon` | `农业基地_v7.1_GCJ02_MultiPolygon/geojson_generate_from_kml.py` | `data/sink/农业基地_v7.1_GCJ02_MultiPolygon/` | `python3 scripts/versions/农业基地_v7.1_GCJ02_MultiPolygon/geojson_generate_from_kml.py` | `pytest "tests/test_all_versions.py::test_generate_matches_golden_manifest[农业基地_v7.1_GCJ02_MultiPolygon]" -v` | 8× `*-area.json` / `*-point.json` |
| `农业基地_v7.2_GCJ02_MP_L2` | `农业基地_v7.2_GCJ02_MP_L2/geojson_generate_from_kml.py` | `data/sink/农业基地_v7.2_GCJ02_MP_L2/` | `python3 scripts/versions/农业基地_v7.2_GCJ02_MP_L2/geojson_generate_from_kml.py` | `pytest "tests/test_all_versions.py::test_generate_matches_golden_manifest[农业基地_v7.2_GCJ02_MP_L2]" -v` | L3 树 + legacy 合并（约 140 json）|
| `农业基地_v7.3_GCJ02_L3` | `农业基地_v7.3_GCJ02_L3/geojson_generate_from_kml.py` | `data/sink/农业基地_v7.3_GCJ02_L3/` | `python3 scripts/versions/农业基地_v7.3_GCJ02_L3/geojson_generate_from_kml.py` | `pytest "tests/test_all_versions.py::test_generate_matches_golden_manifest[农业基地_v7.3_GCJ02_L3]" -v` | 同 v7.2 形态（约 140 json）|
| `农业基地_v7.4_GCJ02_L3_SingleMap` | `农业基地_v7.4_GCJ02_L3_SingleMap/geojson_generate_from_kml.py`（同 `active/`）| `data/sink/农业基地_v7.4_GCJ02_L3_SingleMap/` | `python3 scripts/active/geojson_generate_from_kml.py` | `pytest "tests/test_all_versions.py::test_generate_matches_golden_manifest[农业基地_v7.4_GCJ02_L3_SingleMap]" -v` | L3 树、无 legacy（约 136 json）|

| 仅重庆酉阳（v7.0，不改 CS/WS/BS） | `./scripts/ops/generate_youyang_v70.sh` | 写 `农业基地_GCJ02_YY.json`；`GEOJSON_BASES=重庆酉阳` |
| 仅重庆酉阳（v7.1，不改 CS/WS/BS） | `./scripts/ops/generate_youyang_v71.sh` | 写 `农业基地_GCJ02_YY-area.json` + `-point.json`（7 片区重心点）|
| 运维 / 补救（非主生成路径） | 脚本 | 说明 |
|----------------------------|------|------|
| v7.1 从旧合并 json 拆分 | `versions/农业基地_v7.1_…/geojson_fix_area_point_split.py` | 仅修已有文件；新生成请用上表 `geojson_generate_from_kml.py` |
| 坐标工具 | `scripts/lib/coord_convert_wgs84_to_gcj02.py` | WGS84 → GCJ-02 |
| 更新 golden | `python3 tests/tools/build_all_golden_manifests.py` | 改 `lib/geojson` 后重算五版本 manifest |

指定版本也可用环境变量：`GEOJSON_VERSION=农业基地_v7.3_GCJ02_L3 python3 scripts/active/geojson_generate_from_kml.py`。

---

## 快速开始

```bash
cp .env.example .env
./scripts/ops/generate_all_sink_versions.sh    # 或见上表单版本命令
MYSQL_PASSWORD=test pytest tests/ -v           # 生成 + 回归（写入 data/sink/）
./scripts/ops/sync_sink_map_to_finereport.sh 农业基地_v7.4_GCJ02_L3_SingleMap
```

依赖：生成 `pip install shapely openpyxl`；测试 `pip install -r requirements-dev.txt`。

---

## 测试

详细计划与报告见 [`tests/TEST_PLAN.md`](tests/TEST_PLAN.md)、[`tests/TEST_REPORT.md`](tests/TEST_REPORT.md)；用例表见 [`tests/cases/geojson_test_cases.yaml`](tests/cases/geojson_test_cases.yaml)。

### 环境准备

```bash
pip install -r requirements-dev.txt
cp .env.example .env   # 可选；pytest 离线生成不连库
```

离线回归只需设置占位密码（不访问 MySQL）：

```bash
export MYSQL_PASSWORD=test
```

### 运行全部测试

```bash
MYSQL_PASSWORD=test pytest tests/ -v
```

`pytest` 与 `./scripts/ops/generate_all_sink_versions.sh` 均会写满 **`data/sink/`** 下五个版本目录（详见上文对照表）。`data/sink/` 内 GeoJSON **纳入 Git**，可 `git add data/sink && git commit && git push`。

### 测试模块与数据目录

| 测试文件 | 主要验证 | 是否写入 `data/sink/` |
|----------|----------|------------------------|
| `tests/test_all_versions.py` | 五版本脚本存在、sink 五目录、golden 结构 | 是（会话 fixture）|
| `tests/test_data_layout.py` | `source` / `sink` 默认路径 | 否 |
| `tests/test_geojson_generate.py` | v7.4 golden + `PROTECT_EXISTING` | 前者是；后者用临时目录 |
| `tests/test_geojson_conventions.py` | v7.4 area/point 命名约定 | 是（依赖会话 fixture）|
| `tests/test_version_profiles.py` | `profiles.py` 标志位 | 否 |
| `tests/test_kml_parser.py` 等 | KML / 坐标 / 匹配 / 配置单元 | 否 |

### 运行指定测试

语法：`pytest <路径>::<函数名>` 或 `pytest <路径>::<类名>::<方法名>`。

```bash
# 单个文件（整个模块）
pytest tests/test_all_versions.py -v
pytest tests/test_data_layout.py -v

# 单个用例（函数）
pytest tests/test_all_versions.py::test_sink_has_five_version_directories -v
pytest tests/test_all_versions.py::test_generate_matches_golden_manifest -v

# 参数化用例：指定某一版本（须带完整参数值）
pytest "tests/test_all_versions.py::test_generate_matches_golden_manifest[农业基地_v7.0_GCJ02_Polygon]" -v
pytest "tests/test_all_versions.py::test_generate_matches_golden_manifest[农业基地_v7.4_GCJ02_L3_SingleMap]" -v

# 按关键字过滤（-k，匹配节点 id / 类名 / 函数名）
pytest tests/ -k "sink_has_five" -v
pytest tests/ -k "v7.1" -v
pytest tests/ -k "golden_manifest" -v

# 仅结构约定（v7.4，依赖会话级 sink 生成）
pytest tests/test_geojson_conventions.py -v

# 先看会跑哪些用例，不执行
pytest tests/ --collect-only
```

**说明：**

- 多数 GeoJSON 用例依赖会话 fixture `sink_all_versions`，**单独跑某一个 `test_generate_matches_golden_manifest[版本]` 时，pytest 仍会先执行会话级生成**，写入上述五个 sink 目录。
- `tests/test_geojson_generate.py::test_protect_existing_skips_writes` 使用临时目录，不写 sink。
- 默认 `pytest.ini` 带 `-q`（简略输出）；需要完整列表时加 `-v`。

### 更新 golden（生成逻辑变更后）

```bash
python3 tests/tools/build_all_golden_manifests.py
MYSQL_PASSWORD=test pytest tests/test_all_versions.py -v
```

### 测试相关文档

| 文档 | 内容 |
|------|------|
| [tests/TEST_PLAN.md](tests/TEST_PLAN.md) | 策略、准出、数据布局 |
| [tests/TEST_REPORT.md](tests/TEST_REPORT.md) | 最近执行结果 |
| [tests/TASKS.md](tests/TASKS.md) | TDD / 验收任务勾选 |
| [tests/cases/README.md](tests/cases/README.md) | 用例 ID 与 YAML 索引 |

---

## 文档索引

| 文档 | 内容 |
|------|------|
| [openspec/project.md](openspec/project.md) | 项目概述、技术栈、版本历史 |
| [openspec/specs/bigscreen.md](openspec/specs/bigscreen.md) | 大屏功能与数据源 |
| [openspec/specs/geojson.md](openspec/specs/geojson.md) | GeoJSON 格式与部署层级 |
| [openspec/specs/scripts.md](openspec/specs/scripts.md) | 脚本目录与命名规范 |
| [openspec/release-notes-fvs.md](openspec/release-notes-fvs.md) | FVS 版本与 geourl |
| [openspec/release-notes-geojson.md](openspec/release-notes-geojson.md) | GeoJSON 版本目录 |
| [scripts/README.md](scripts/README.md) | 脚本入口摘要 |

---

## 与原项目路径对照

| 原路径（P2025 全量目录） | 本仓路径 |
|--------------------------|----------|
| `5.数据设计/.../1.农业基地KML/` | `data/source/1.农业基地KML/` |
| `5.数据设计/.../农业资产盘点明细.xlsx` | `data/source/农业资产盘点明细.xlsx` |
| `5.数据设计/.../2.农业基地JSON/` | `data/source/2.农业基地JSON/` |
| FR `WEB-INF/.../农业基地-大疆测绘/{版本}/` | `data/sink/{版本}/`（生成后 `sync_sink_map_to_finereport.sh` 同步）|
| `6.开发实现/scripts/` | `scripts/` |

FineReport 部署路径（`WEB-INF/...`）**未迁移**，见 `CLAUDE.md` 关键路径表。
