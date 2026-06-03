# 项目规范：P2025-G-001 农业大屏一期

**项目编号：** `P2025-G-001`  
**归属：** 数智部  
**状态：** **v7.2 生产封板**（L2，验收通过）；v7.1 封板可回退；v7.3 实验验证中  
**建档日期：** 2026-06-03  
**代码仓：** `fr-tools`（2026-06 自全量项目目录迁移）

---

## 仓库说明（fr-tools）

本 Git 仓库为 **精简迭代仓**，从原路径  
`P2025-G-001-数智部-农业大屏一期 ★/` 迁出，**刻意不包含** 规划/跟踪/调研/原型等历史文件夹与根目录散落的一次性文档。

| 目标 | 做法 |
|------|------|
| 降低认知负担 | 仅 `data/` + `scripts/` + `openspec/` + `CLAUDE.md` |
| 规范单一来源 | 全部有效说明写入 `openspec/`，废除与台账重复的根目录 md |
| 运行时资产外置 | FVS、生产 GeoJSON 仍在 FineReport `WEB-INF/`，由 release-notes 台账管理 |

**不在本仓、迭代时仍需访问：**

- FVS：`WEB-INF/reportlets/YXG-项目/5.农业大屏二期/`
- GeoJSON：`WEB-INF/assets/map/geographic/农业基地-大疆测绘/`
- 原项目盘中的 DB DDL、效果图等（只读参考，不阻塞日常脚本与规范更新）

---

## 项目概述

为柚香谷四大农业基地（浙江常山、四川武胜、广西百色、重庆酉阳）构建可视化管理大屏，通过 FineReport FVS 大屏组件实现片区分布地图、种植概况、环境监测、作业分析等综合展示。

## 技术栈

| 层级 | 技术 |
|------|------|
| 大屏引擎 | FineReport v11（FVS 格式） |
| 地图底图 | 高德卫星图（GCJ-02 坐标） |
| 片区边界 | GeoJSON（RFC 7946，Polygon / MultiPolygon） |
| 数据库 | MySQL 8（`yxg_bigscreen` @ `172.17.4.4:3310`） |
| 核心数据表 | `ods_ag_base_v2`、`ods_ag_area` |
| 脚本语言 | Python 3（GeoJSON 生成、坐标转换） |

## 本仓目录结构

```
fr-tools/
├── README.md              # 迁移说明、快速开始、路径对照
├── CLAUDE.md              # 封板保护 + FineReport 关键路径
├── data/
│   ├── 1.农业基地KML/     # KML 源（大疆测绘）
│   ├── 2.农业基地JSON/    # 本地中间 / 归档 GeoJSON
│   └── 农业资产盘点明细.xlsx
├── scripts/               # 见 openspec/specs/scripts.md
│   ├── active/
│   ├── lib/
│   ├── ops/
│   └── versions/
└── openspec/              # 规范与版本台账（唯一文档真相源）
    ├── project.md         # 本文件
    ├── specs/
    ├── release-notes-*.md
    ├── changes/
    └── archive/
```

## 版本历史

| 版本 | 日期 | 文件 | 主要内容 |
|------|------|------|----------|
| v4 | 2025-03 | `Agriculture_v4.fvs` | 早期版本（归档） |
| v6 | 2025-06-24 | `Agriculture_v6.0_20250624_UI_Green.fvs` | 多基地地图切换 |
| v7.0 | 2026-06-03 | `Agriculture_v7.0_GCJ02_Polygon.fvs` | 四基地 Polygon 封板 |
| v7.1 | 2026-06-03 | `Agriculture_v7.1_GCJ02_MultiPolygon.fvs` | MultiPolygon 扁平 L1，**封板**（可回退）|
| v7.2 | 2026-06-03 | `Agriculture_v7.2_GCJ02_MP_L2.fvs` | MultiPolygon L2，**封板 + 验收通过（当前生产）** |
| v7.3 | 2026-06-03 | `Agriculture_v7.3_GCJ02_L3.fvs` | 三层层级（开发中）|

台账详情：`release-notes-fvs.md`、`release-notes-geojson.md`、`release-notes-scripts.md`。

## 关键约束

1. `d-chart-AREA_MAP` **支持 `MultiPolygon`**；推荐同名片区合并为单一 feature
2. 地图底图为高德 GCJ-02，GeoJSON 坐标须转换至 GCJ-02
3. GeoJSON 顶层须有 `name` 字段；`properties.name` 与 `ods_ag_base_v2.片区名称` 完全一致
4. `panTo([lat, lng])` 为纬度在前、经度在后
5. v7.1 封板及以后：**仅** `*-area.json` + `*-point.json`，FVS geourl 指向 `-area.json`

## 数据库连接

```
Host:     172.17.4.4:3310
Database: yxg_bigscreen
User:     bigdata
```

（凭据见各脚本内 `DB` 常量或环境配置，**勿提交** `.env` 至 Git。）

## OpenSpec 变更列表

| Change ID | 日期 | 类型 | 状态 | 描述 |
|-----------|------|------|------|------|
| `agri-bigscreen-v7-archive` | 2026-06-03 | 文档归档 | ✅ 已归档 | v6→v7 升级工作完整归档 |
| `agri-version-management` | 2026-06-03 | 版本管理 | 🔧 进行中 | 台账、封板保护、非封板 geourl 修复 |
| *(仓库)* `fr-tools` 迁移 | 2026-06-03 | 工程结构 | ✅ 已完成 | 全量项目目录 → 本仓核心文件 + 文档路径更新 |
