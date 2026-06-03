# Claude 指令：P2025-G-001 农业大屏（fr-tools）

> **仓库：** 自 `P2025-G-001-数智部-农业大屏一期 ★/` 迁移的精简仓，仅含 `data/`、`scripts/`、`openspec/`。FVS 与生产 GeoJSON 仍在 FineReport `WEB-INF/`。说明见根目录 `README.md`。

**生产基线：** **v7.4** 单图（`Agriculture_v7.4_GCJ02_L3_SingleMap.fvs` + `农业基地_v7.4_GCJ02_L3_SingleMap/`）— 验收通过且已封板。v7.0–v7.3 同为封板（可回退）。  
**酉阳（2026-06-03）：** v7.0–v7.4 五版本 FR 手工验收通过；GeoJSON 含 **7** 个酉阳片区（Excel 另 9 片区待 KML）。本仓 `data/sink/` 为生成真相源，部署用 `scripts/ops/sync_sink_map_to_finereport.sh`。

## ⛔ 封板文件保护（CRITICAL）

以下 **12** 个文件/目录已**封板（FROZEN）**，绝对不允许修改、重命名、移动或删除内容：

| 类型 | 路径 |
|------|------|
| FVS | `WEB-INF/reportlets/YXG-项目/5.农业大屏二期/Agriculture_v6.0_TEST.fvs` |
| FVS | `WEB-INF/reportlets/YXG-项目/5.农业大屏二期/Agriculture_v7.0_GCJ02_Polygon.fvs` |
| FVS | `WEB-INF/reportlets/YXG-项目/5.农业大屏二期/Agriculture_v7.1_GCJ02_MultiPolygon.fvs` |
| FVS | `WEB-INF/reportlets/YXG-项目/5.农业大屏二期/Agriculture_v7.2_GCJ02_MP_L2.fvs` |
| FVS | `WEB-INF/reportlets/YXG-项目/5.农业大屏二期/Agriculture_v7.3_GCJ02_L3.fvs` |
| FVS | `WEB-INF/reportlets/YXG-项目/5.农业大屏二期/Agriculture_v7.4_GCJ02_L3_SingleMap.fvs` |
| GeoJSON 目录 | `WEB-INF/assets/map/geographic/农业基地-大疆测绘/农业基地_v6.0_TEST/` |
| GeoJSON 目录 | `WEB-INF/assets/map/geographic/农业基地-大疆测绘/农业基地_v7.0_GCJ02_Polygon/` |
| GeoJSON 目录 | `WEB-INF/assets/map/geographic/农业基地-大疆测绘/农业基地_v7.1_GCJ02_MultiPolygon/` |
| GeoJSON 目录 | `WEB-INF/assets/map/geographic/农业基地-大疆测绘/农业基地_v7.2_GCJ02_MP_L2/` |
| GeoJSON 目录 | `WEB-INF/assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/` |
| GeoJSON 目录 | `WEB-INF/assets/map/geographic/农业基地-大疆测绘/农业基地_v7.4_GCJ02_L3_SingleMap/` |

**如果用户要求修改上述任意文件，必须执行 3 次独立确认：**

1. 第一次确认：`你确认要修改封板文件 {文件名} 吗？这是封板保护的第1次确认。`
2. 等待用户明确回复"确认"
3. 第二次确认：`再次确认：修改封板文件 {文件名} 是不可逆操作，可能破坏当前唯一可用的大屏版本。这是第2次确认。`
4. 等待用户明确回复"确认"
5. 第三次确认：`最终确认：即将修改封板文件 {文件名}。请输入"我已了解风险"以继续。`
6. 等待用户输入"我已了解风险"
7. 仅在3次全部确认后方可执行操作

如果用户在任何一步没有明确确认，必须停止操作并保持文件不变。

---

## 项目规范

详见 `openspec/` 目录：
- `project.md` — 项目约定与版本历史
- `specs/bigscreen.md` — 大屏功能规范
- `specs/geojson.md` — GeoJSON 数据格式规范
- `release-notes-geojson.md` — GeoJSON 版本台账
- `release-notes-fvs.md` — FVS 版本台账
- `specs/scripts.md` — 脚本目录与命名规范
- `release-notes-scripts.md` — 脚本版本台账（`scripts/versions/`）

## ⛔ GeoJSON 目录规范（v7.1–v7.4 封板及后续新版本，CRITICAL）

`农业基地_v7.1_GCJ02_MultiPolygon/` … `农业基地_v7.4_GCJ02_L3_SingleMap/`（**已封板**）及后续新版本采用 **area/point 分离**：

| 允许 | 禁止 |
|------|------|
| `{名}-area.json`（仅 Polygon/MultiPolygon） | `{名}.json`（无 `-area`/`-point` 后缀） |
| `{名}-point.json`（仅 Point） | 在同一文件混写 area + point |

**禁止原因：** 无后缀的合并 `.json` 会导致 FineReport **点地图显示异常**（已实测）。

**FVS geourl 必须指向 `-area.json`**，例如：

- v7.1（L1 扁平）：`.../农业基地_v7.1_GCJ02_MultiPolygon/农业基地_GCJ02_CS-area.json`
- v7.2（L2）：`.../农业基地_v7.2_GCJ02_MP_L2/农业基地/浙江常山-area.json`
- v7.3（L3 四图，可回退）：`.../农业基地_v7.3_GCJ02_L3/农业基地/浙江常山-area.json`
- v7.4（L3 单图，**当前生产**）：`.../农业基地_v7.4_GCJ02_L3_SingleMap/农业基地-area.json`

v6 / v7.0 封板仍用旧式 `农业基地_GCJ02_{基地}.json`；**v7.1–v7.4 封板**仅允许 `*-area.json` + `*-point.json`，勿改动上述 **12** 项封板路径。

---

## 关键路径

| 资源 | 路径 |
|------|------|
| **本仓** 说明 | `README.md` |
| GeoJSON（生产） | FineReport：`WEB-INF/assets/map/geographic/农业基地-大疆测绘/` |
| FVS 全部版本 | FineReport：`WEB-INF/reportlets/YXG-项目/5.农业大屏二期/` |
| FVS 历史归档 | FineReport：`WEB-INF/reportlets/YXG-项目/1.农业大屏/`（只读）|
| 生成脚本（活跃） | `scripts/active/geojson_generate_from_kml.py` |
| 脚本版本快照 | `scripts/versions/{GeoJSON目录名}/` |
| KML 源文件 | `data/source/1.农业基地KML/` |
| 盘点 Excel | `data/source/农业资产盘点明细.xlsx` |
| GeoJSON 生成输出 | `data/sink/{版本}/` |
| FR 部署（同步） | FineReport `WEB-INF/assets/map/geographic/农业基地-大疆测绘/` |
