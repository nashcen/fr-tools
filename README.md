# fr-tools — P2025-G-001 农业大屏（精简仓）

**项目编号：** `P2025-G-001`（数智部 · 农业大屏一期）  
**本仓库：** 自原项目管理目录 **迁移** 后的迭代专用仓，仅保留日常开发所需的核心资产。

**当前生产基线（封板）：** `v7.1` — `Agriculture_v7.1_GCJ02_MultiPolygon.fvs` + `农业基地_v7.1_GCJ02_MultiPolygon/`（MultiPolygon、`*-area.json` / `*-point.json`，验收已通过，禁止修改，见 `CLAUDE.md`）。

---

## 为何迁移

原目录 `P2025-G-001-数智部-农业大屏一期 ★/` 按「项目全生命周期」展开（规划、跟踪、调研、原型、数据设计、开发实现等），积累大量 **一次性文档、历史脚本编号、重复说明**，与 `openspec/` 规范并存，难以判断「哪份有效、改哪里」，严重拖慢 v7 及后续版本迭代。

**本仓原则：**

| 保留在本仓 | 不纳入本仓（仍在 FineReport / 原项目盘） |
|------------|------------------------------------------|
| `openspec/` 规范与版本台账 | FVS 模板（`WEB-INF/reportlets/.../5.农业大屏二期/`） |
| `scripts/` 活跃脚本 + 版本快照 | 生产 GeoJSON（`WEB-INF/assets/map/geographic/农业基地-大疆测绘/`） |
| `data/` KML、盘点 Excel、中间 GeoJSON | 蓝图、会议纪要、UI 切图、DB DDL 归档等 |

规范与封板规则仍以 **`openspec/` + `CLAUDE.md`** 为唯一真相源；运行时大屏资源在 **FineReport 安装目录**，不在 Git 中。

---

## 目录结构

```
fr-tools/
├── README.md                 # 本说明
├── CLAUDE.md                 # 封板保护、关键路径（AI / 人工必读）
├── data/                     # 源数据与本地中间产物
│   ├── 1.农业基地KML/        # 大疆测绘 KML（按基地分子目录）
│   ├── 2.农业基地JSON/       # 本地归档 / 对账用 GeoJSON（可选）
│   └── 农业资产盘点明细.xlsx # 地块层级对账
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
# 从 KML 生成 GeoJSON（输出目录见 scripts/active/geojson_generate_from_kml.py 内 GCJ02_DIR）
python3 scripts/active/geojson_generate_from_kml.py

# v7.1 封板：area/point 分离（使用版本快照，勿改封板部署目录）
python3 scripts/versions/农业基地_v7.1_GCJ02_MultiPolygon/geojson_fix_area_point_split.py

# WGS84 → GCJ-02 工具模块
python3 scripts/lib/coord_convert_wgs84_to_gcj02.py
```

依赖：`pip install shapely openpyxl`（主生成脚本）；数据库相关脚本另需 MySQL 客户端。

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
| `5.数据设计/农业数据/6.片区边界/1.农业基地KML/` | `data/1.农业基地KML/` |
| `5.数据设计/.../农业资产盘点明细.xlsx` | `data/农业资产盘点明细.xlsx` |
| `5.数据设计/.../2.农业基地JSON/` | `data/2.农业基地JSON/` |
| `6.开发实现/scripts/` | `scripts/` |

FineReport 部署路径（`WEB-INF/...`）**未迁移**，见 `CLAUDE.md` 关键路径表。
