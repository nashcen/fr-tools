# 规范：开发脚本（scripts）

**规范 ID：** `scripts`  
**版本：** 1.1（2026-06-03，fr-tools 迁移路径）  
**路径：** `scripts/`（仓库根目录，原 `6.开发实现/scripts/`）

---

## 一、目录结构

```
scripts/
├── README.md                 # 入口说明
├── active/                   # 活跃开发（仅此处日常修改）
├── lib/                      # 可被其他脚本 import 的共享逻辑
├── ops/                      # FineReport 本地运维 Shell
└── versions/                 # 版本快照（与 GeoJSON 目录名一致，纳入 Git）
    ├── _shared/              # 跨版本工具
    ├── _archive/             # 已废弃逻辑
    ├── 农业基地_v7.0_GCJ02_Polygon/
    ├── 农业基地_v7.1_GCJ02_MultiPolygon/
    ├── 农业基地_v7.2_GCJ02_MP_L2/
    └── 农业基地_v7.3_GCJ02_L3/
```

| 目录 | 规则 |
|------|------|
| `active/` | 当前迭代唯一入口；发版后复制到 `versions/{GeoJSON目录名}/` |
| `versions/{名}/` | **必须与** `WEB-INF/.../农业基地-大疆测绘/` 下 GeoJSON 目录名 **完全一致** |
| `versions/_shared/` | 前缀 `_` 表示非绑定单一发布版本 |
| `versions/_archive/` | 历史废弃脚本，勿用于生产 |

**禁止：** 在 `versions/` 下使用 `v7.2_GCJ02_MP_L2` 简写（与 GeoJSON 目录不一致）；禁止 `common/` / `archive/` 无下划线（易与基地名混淆）。

---

## 二、文件命名

### Python

```
{领域}_{动作}.py
```

| 字段 | 取值 | 示例 |
|------|------|------|
| 领域 `领域` | `coord` `geojson` `db` | — |
| 动作 | 动词短语，小写，下划线分隔 | `generate_from_kml` `fix_area_point_split` |

**完整示例：**

| 脚本名 | 含义 |
|--------|------|
| `coord_convert_wgs84_to_gcj02.py` | 坐标转换 |
| `geojson_generate_from_kml.py` | KML → GeoJSON 主生成 |
| `geojson_patch_missing_from_kml.py` | 补缺失片区 |
| `geojson_fix_area_point_split.py` | area/point 分离（v7.1）|
| `geojson_explode_multipolygon_compat.py` | 旧 FR 兼容（归档）|
| `db_update_ods_ag_base_v2.py` | 回写 DB 坐标 |

**禁止：** 数字前缀（旧 `01_` `02_`）；禁止版本号写入活跃脚本文件名（版本只体现在 `versions/` 目录）。

### Shell（运维）

```
fr_{动作}.sh
```

| 示例 | 含义 |
|------|------|
| `fr_close_preview_tabs.sh` | 关闭预览 Tab |
| `fr_kill_wait_port_8075.sh` | 结束 FR 并等待 8075 端口 |

---

## 三、版本快照规则

1. GeoJSON + FVS 封板或发版时，将 `active/`（及相关 `_shared` 依赖）复制到 `versions/农业基地_{版本}/`
2. 快照内脚本头部必须有：`【版本快照 {GeoJSON目录名} — 封板|验证中，勿改】`
3. 更新 `openspec/release-notes-scripts.md`
4. 封板后只改 `active/`，不回改快照

---

## 四、配置常量命名（代码内）

| 常量 | 含义 |
|------|------|
| `KML_DIR` | KML 源目录 |
| `GEOJSON_DIR` / `GCJ02_DIR` | 输出 GeoJSON 目录（逐步统一为 `GEOJSON_DIR`）|
| `EXCEL_PATH` | 农业资产盘点明细 |
| `DB` | MySQL 连接 dict |

`GCJ02_DIR` 在快照中必须指向对应 `versions/` 目录名的部署路径。

---

## 五、依赖关系

```
geojson_generate_from_kml.py
geojson_patch_missing_from_kml.py  → importlib 加载 lib/coord_convert_wgs84_to_gcj02.py
```

---

## 变更历史

| 日期 | 变更 |
|------|------|
| 2026-06-03 | v1.0：废除 `01_`~`05_` 编号；`active/lib/ops/versions` 结构；版本目录与 GeoJSON 目录同名 |
| 2026-06-03 | v1.1：迁移至 `fr-tools`，规范路径 `scripts/`；`KML_DIR` / `EXCEL_PATH` 默认 `data/` |
