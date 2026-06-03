# FVS 版本台账

**文件：** `openspec/release-notes-fvs.md`  
**最后更新：** 2026-06-03  
**管理目录：** `WEB-INF/reportlets/YXG-项目/5.农业大屏二期/`  
**历史归档（只读）：** `WEB-INF/reportlets/YXG-项目/1.农业大屏/`  
**geourl 根前缀：** `assets/map/geographic/农业基地-大疆测绘/`

---

## 版本总览

FVS 与 GeoJSON 目录**一一对应**命名：

| FVS 文件 | GeoJSON 目录 | geourl | 封板 | 状态 |
|----------|--------------|--------|------|------|
| `Agriculture_v6.0_TEST.fvs` | `农业基地_v6.0_TEST` | ✅ | ✅ FROZEN | 封板可用 |
| `Agriculture_v6.9_WGS84_Polygon.fvs` | `农业基地_v6.9_WGS84_Polygon` | ✅ | — | 手动修复，非生产 |
| `Agriculture_v7.0_GCJ02_Polygon.fvs` | `农业基地_v7.0_GCJ02_Polygon` | ✅ | ✅ FROZEN | 封板可用 |
| `Agriculture_v7.1_GCJ02_MultiPolygon.fvs` | `农业基地_v7.1_GCJ02_MultiPolygon` | ✅ | ✅ FROZEN | 封板可用（L1 扁平，可回退）|
| `Agriculture_v7.2_GCJ02_MP_L2.fvs` | `农业基地_v7.2_GCJ02_MP_L2` | ✅ | ✅ FROZEN | 封板可用（L2，可回退）|
| `Agriculture_v7.3_GCJ02_L3.fvs` | `农业基地_v7.3_GCJ02_L3` | ✅ | ✅ FROZEN | 封板可用（L3 四图，可回退）|
| `Agriculture_v7.4_GCJ02_L3_SingleMap.fvs` | `农业基地_v7.4_GCJ02_L3_SingleMap` | ✅ | ✅ FROZEN | **生产基线（L3 单图，验收通过）** |

> ⛔ 封板版本禁止修改，见 `CLAUDE.md`（**12** 项）。  
> **路线：** v7.3 四图封板保留；v7.4 单图为当前生产。

---

## ✅ 封板版本

### `Agriculture_v6.0_TEST.fvs` — FROZEN

| 项 | 值 |
|----|-----|
| 封板日期 | 2026-06-03 |
| GeoJSON 目录 | `农业基地_v6.0_TEST` |

**geourl 路径表：**

| 组件名 | geourl（相对 `WEB-INF/`）| 验证 |
|--------|--------------------------|------|
| （单图） | `assets/map/geographic/农业基地-大疆测绘/农业基地_v6.0_TEST/农业基地_GCJ02.json` | ✅ |

---

### `Agriculture_v7.0_GCJ02_Polygon.fvs` — FROZEN

| 项 | 值 |
|----|-----|
| 封板日期 | 2026-06-03 |
| 最近抽检 | 2026-06-03（磁盘路径 + geourl + GeoJSON 对照）|
| 文件大小 | ~41.5 MB（`43489382` bytes）|
| GeoJSON 目录 | `农业基地_v7.0_GCJ02_Polygon` |
| 格式 | 旧式无后缀 `.json`（单文件 Polygon，**无** `-area`/`-point` 分离）|
| 定位 | 四基地 Polygon 封板基线；生产推荐改用 **v7.1** |

**geourl 路径表（抽检：无 `world/`，无 `v3_GCJ02`）：**

| 组件名 | 基地 | geourl（相对 `WEB-INF/`）| 文件存在 | geourl |
|--------|------|--------------------------|----------|--------|
| `区域地图_CS` | 浙江常山 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.0_GCJ02_Polygon/农业基地_GCJ02_CS.json` | ✅ | ✅ |
| `区域地图_WS` | 四川武胜 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.0_GCJ02_Polygon/农业基地_GCJ02_WS.json` | ✅ | ✅ |
| `区域地图_BS` | 广西百色 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.0_GCJ02_Polygon/农业基地_GCJ02_BS.json` | ✅ | ✅ |
| `区域地图_YY` | 重庆酉阳 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.0_GCJ02_Polygon/农业基地_GCJ02_YY.json` | ✅ | ✅（7 片区，2026-06-03 验收）|

**FVS ↔ chart 绑定（供维护对照）：**

| chart 文件 | 绑定基地 |
|------------|----------|
| `bf4df8fc-…bff.chart` | CS |
| `f878433d-…d40.chart` | WS |
| `0bd77711-…57f5.chart` | BS |
| `8a3947cb-…619de.chart` | YY |

**封板后已知限制（不修复）：**

| 项 | 说明 |
|----|------|
| 几何 | Polygon 未合并，同片区名多 feature，区域列表重复 |
| 点图层 | 无独立 `-point.json`（与 v7.1 规范不同）|
| 酉阳 | 仅 **7/16** 片区有 KML（后溪/大地/杉岭等 9 片区待补）；已可正常展示 |
| 测试文件 | `农业基地_GCJ02_CS_test.json` 已从 GeoJSON 目录删除（2026-06-03），与本 FVS 无关 |

---

### `Agriculture_v7.1_GCJ02_MultiPolygon.fvs` — FROZEN

| 项 | 值 |
|----|-----|
| 封板日期 | 2026-06-03 |
| 验收 | ✅ 地图配置 + 大屏预览通过 |
| GeoJSON 目录 | `农业基地_v7.1_GCJ02_MultiPolygon` |
| 格式 | geourl → `*-area.json`；目录仅 `-area`/`-point`（**禁止无后缀 `.json`**）|
| 定位 | 四基地 MultiPolygon L1 扁平 — **封板**（可回退；生产推荐 **v7.2**）|

**geourl 路径表：**

| 组件名 | 基地 | geourl（相对 `WEB-INF/`）| 验证 |
|--------|------|--------------------------|------|
| `区域地图_CS` | 浙江常山 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.1_GCJ02_MultiPolygon/农业基地_GCJ02_CS-area.json` | ✅ |
| `区域地图_WS` | 四川武胜 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.1_GCJ02_MultiPolygon/农业基地_GCJ02_WS-area.json` | ✅ |
| `区域地图_BS` | 广西百色 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.1_GCJ02_MultiPolygon/农业基地_GCJ02_BS-area.json` | ✅ |
| `区域地图_YY` | 重庆酉阳 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.1_GCJ02_MultiPolygon/农业基地_GCJ02_YY-area.json` | ✅（7 片区 + 7 point）|

**封板后已知限制（不修复）：**

| 项 | 说明 |
|----|------|
| 酉阳 | 9 个 Excel 片区尚无 KML（见 `openspec/specs/geojson.md` P1）|
| 姜盘石 | 无 KML/坐标，不在 area 中 |

---

### `Agriculture_v7.2_GCJ02_MP_L2.fvs` — FROZEN

| 项 | 值 |
|----|-----|
| 封板日期 | 2026-06-03 |
| 验收 | ✅ L1/L2 目录、FR 地图配置、四基地大屏预览通过 |
| GeoJSON 目录 | `农业基地_v7.2_GCJ02_MP_L2` |
| 层级 | L1 `农业基地-area.json`；L2 `农业基地/{基地名}-area.json` |
| 定位 | L2 两层 — **封板**（可回退；生产推荐 **v7.3**）|
| 不含 | 地块 L3 子目录 |

**geourl 路径表：**

| 组件名 | 基地 | geourl（相对 `WEB-INF/`）| 验证 |
|--------|------|--------------------------|------|
| `区域地图_CS` | 浙江常山 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.2_GCJ02_MP_L2/农业基地/浙江常山-area.json` | ✅ |
| `区域地图_WS` | 四川武胜 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.2_GCJ02_MP_L2/农业基地/四川武胜-area.json` | ✅ |
| `区域地图_BS` | 广西百色 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.2_GCJ02_MP_L2/农业基地/广西百色-area.json` | ✅ |
| `区域地图_YY` | 重庆酉阳 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.2_GCJ02_MP_L2/农业基地/重庆酉阳-area.json` | ✅（7 片区）|

**与 v7.1 geourl 差异：**

| 版本 | 常山 geourl |
|------|-------------|
| v7.1 | `…/农业基地_GCJ02_CS-area.json`（扁平）|
| v7.2 | `…/农业基地/浙江常山-area.json`（L2）|

**封板后已知限制（不修复）：** 酉阳无 L3 地块层；9 个片区待 KML。

---

### `Agriculture_v7.3_GCJ02_L3.fvs` — FROZEN

| 项 | 值 |
|----|-----|
| 封板日期 | 2026-06-03 |
| 验收 | ✅ L3 目录、四基地大屏、FR 地图配置 L1/L2/L3 通过 |
| GeoJSON 目录 | `农业基地_v7.3_GCJ02_L3` |
| 大屏结构 | **四图** `区域地图_CS/WS/BS/YY`（固定，v7.4 单图另版）|
| 定位 | L3 四图 — **封板**（可回退；生产推荐 **v7.4**）|

**geourl 路径表：**

| 组件名 | 基地 | geourl（相对 `WEB-INF/`）| 验证 |
|--------|------|--------------------------|------|
| `区域地图_CS` | 浙江常山 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/农业基地/浙江常山-area.json` | ✅ |
| `区域地图_WS` | 四川武胜 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/农业基地/四川武胜-area.json` | ✅ |
| `区域地图_BS` | 广西百色 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/农业基地/广西百色-area.json` | ✅ |
| `区域地图_YY` | 重庆酉阳 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/农业基地/重庆酉阳-area.json` | ✅（7 片区）|

**封板后已知限制（不修复）：** 酉阳 9 片区无 KML；姜盘石等无坐标片区不在 L3。

**geourl 修复记录：** `scripts/ops/fr_patch_v73_geourl.py`（去除 `world/`、`v3_GCJ02`、无后缀 `.json`）。

---

### `Agriculture_v7.4_GCJ02_L3_SingleMap.fvs` — FROZEN（生产基线）

| 项 | 值 |
|----|-----|
| 封板日期 | 2026-06-03 |
| 验收 | ✅ 单图四基地切换、树视图、高亮、L3 下钻通过 |
| GeoJSON 目录 | `农业基地_v7.4_GCJ02_L3_SingleMap` |
| 大屏结构 | **单图** `区域地图`（L1 geourl + `panTo`）|
| 定位 | **当前生产版本** |

**geourl 路径表：**

| 组件名 | geourl（相对 `WEB-INF/`）| 验证 |
|--------|--------------------------|------|
| `区域地图` | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.4_GCJ02_L3_SingleMap/农业基地-area.json` | ✅ |

**封板后已知限制（不修复）：** 与 v7.3 相同（酉阳 7/16 片区；9 片区待 KML）。

**配置脚本：** `scripts/ops/fr_patch_v74_single_map.py`。

---

## geourl 路径规则

| 规则 | 说明 |
|------|------|
| 前缀 | `assets/map/geographic/农业基地-大疆测绘/{版本目录}/` |
| 禁止 | 路径中含 `world/`（内置地图专用）|
| v6 / v7.0 封板 | `{基地}.json` 无后缀（勿改）|
| **v7.1 封板** | 扁平 `{基地码}-area.json`（如 `农业基地_GCJ02_CS-area.json`）|
| **v7.2 封板** | L2：`农业基地/{基地名}-area.json` |
| **v7.3 封板** | 四图绑 L2 `农业基地/{基地名}-area.json`；L3 在 `农业基地/{基地}/{片区}-area.json` |
| **v7.4 封板** | 单图绑 L1 `农业基地-area.json`；L2/L3 由 FR 地图配置下钻 |

**命名：**

```
Agriculture_v{版本}_{坐标系}_{几何描述}.fvs
```

与 GeoJSON 目录名一致（去掉 `农业基地_` 前缀）。

---

## 变更历史

| 日期 | 事件 |
|------|------|
| 2026-06-03 | 6 个 FVS 统一至 `5.农业大屏二期/` |
| 2026-06-03 | v6.0 + v7.0 封板 |
| 2026-06-03 | v7.0 封板资产抽检：geourl/GeoJSON 四基地一致，台账表格更新 |
| 2026-06-03 | v7.0 GeoJSON 目录删除 `农业基地_GCJ02_CS_test.json` |
| 2026-06-03 | **v7.1 封板**（FROZEN）：MultiPolygon + `*-area.json` geourl |
| 2026-06-03 | v7.1 geourl 定为 `*-area.json`；弃用无后缀合并 GeoJSON |
| 2026-06-03 | 清理 v7.1 临时文件：FVS `.bak`/`.deprecated`；废弃目录 `农业基地_v7.1.1_GCJ02` |
| 2026-06-03 | v7.2 更名为 `GCJ02_MP_L2`；部署 L2 GeoJSON；FVS geourl 指向 `农业基地/{基地}-area.json` |
| 2026-06-03 | **v7.2 封板**（FROZEN）：L2 验收通过 |
| 2026-06-03 | `CLAUDE.md` 封板项增至 **8**（含 v7.2 FVS + GeoJSON）|
| 2026-06-03 | v7.3 geourl 修复；**v7.3 封板**；生产基线升至 v7.3；封板 **10** 项 |
| 2026-06-03 | v7.3 临时文件清理（`.bak`、`.DS_Store`）|
| 2026-06-03 | v7.4 单图 FVS：`fr_patch_v74_single_map.py`（L1 geourl + 统一 `区域地图`）|
| 2026-06-03 | **v7.4 封板**（FROZEN）：单图验收通过；生产基线升至 v7.4；封板 **12** 项 |
| 2026-06-03 | **酉阳补全验收**：v7.0–v7.4 四图/单图切换重庆酉阳，地图与片区展示通过（7 片区；9 片区仍待 KML）|

---

## 其他

### `Agriculture_v6.9_WGS84_Polygon.fvs`

| 项 | 值 |
|----|-----|
| 修复状态 | ✅ 手动修复（2026-06-03）|
| 说明 | 非生产；WGS84 已废弃 |
