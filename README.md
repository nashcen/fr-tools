# fr-tools — P2025-G-001 农业大屏（精简仓）

**项目编号：** `P2025-G-001`（数智部 · 农业大屏一期）  
**本仓库：** 自原项目管理目录 **迁移** 后的迭代专用仓，仅保留日常开发所需的核心资产。

**当前生产基线（封板）：** `v7.4` 单图 — `Agriculture_v7.4_GCJ02_L3_SingleMap.fvs` + `农业基地_v7.4_GCJ02_L3_SingleMap/`（组件 `区域地图`，L1 geourl）。  
**可回退：** `v7.3` 四图、`v7.2` L2、`v7.1` L1（见 `CLAUDE.md` **12** 项 FROZEN）。

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

## 快速开始

```bash
cp .env.example .env   # 配置 MYSQL_PASSWORD 等

# 从 KML 生成 GeoJSON → data/sink/{版本}/
python3 scripts/active/geojson_generate_from_kml.py

# 部署至 FineReport（可选）
./scripts/ops/sync_sink_map_to_finereport.sh 农业基地_v7.4_GCJ02_L3_SingleMap

# v7.1 封板：area/point 分离（使用版本快照，勿改封板部署目录）
python3 scripts/versions/农业基地_v7.1_GCJ02_MultiPolygon/geojson_fix_area_point_split.py

# WGS84 → GCJ-02 工具模块
python3 scripts/lib/coord_convert_wgs84_to_gcj02.py
```

依赖：`pip install shapely openpyxl`（主生成脚本）；数据库相关脚本另需 MySQL 客户端。

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

通过后会在 **`data/sink/`** 下直接生成（或覆盖）五个版本目录及全部子目录、`.json`（无 `map/农业基地-大疆测绘` 中间层）：

| 目录 | 说明 |
|------|------|
| `农业基地_v7.0_GCJ02_Polygon/` | 4 个合并 json |
| `农业基地_v7.1_GCJ02_MultiPolygon/` | 8 个 `*-area` / `*-point` |
| `农业基地_v7.2_GCJ02_MP_L2/` | L3 树 + legacy（140 文件）|
| `农业基地_v7.3_GCJ02_L3/` | 同 v7.2 形态（140 文件）|
| `农业基地_v7.4_GCJ02_L3_SingleMap/` | L3 树、无 legacy（136 文件）|

v2 对账 sidecar（若开启）写在 `data/source/农业基地_v2_WGS84/`，不在 sink 下。

一次性生成五版本：`./scripts/ops/generate_all_sink_versions.sh`。`data/sink/` 下 GeoJSON **纳入 Git**，可提交并推送到远程。

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
