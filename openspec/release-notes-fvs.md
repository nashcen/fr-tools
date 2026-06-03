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
| `Agriculture_v7.3_GCJ02_L3.fvs` | `农业基地_v7.3_GCJ02_L3` | ✅ | ✅ FROZEN | **生产基线（L3 四图，验收通过）** |
| `Agriculture_v7.4_GCJ02_L3_SingleMap.fvs` | `农业基地_v7.3_GCJ02_L3`（复用）| — | — | 📋 规划：单图验证 |

> ⛔ 封板版本禁止修改，见 `CLAUDE.md`。  
> **路线：** v7.3 固定四图；v7.4 新建 FVS 试单图，GeoJSON 目录可与 v7.3 共用。

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
| `区域地图_YY` | 重庆酉阳 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.0_GCJ02_Polygon/农业基地_GCJ02_YY.json` | ✅ | ✅（0 feature）|

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
| 酉阳 | `YY.json` 为空（KML 缺失）|
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
| `区域地图_YY` | 重庆酉阳 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.1_GCJ02_MultiPolygon/农业基地_GCJ02_YY-area.json` | ✅（空）|

**封板后已知限制（不修复）：**

| 项 | 说明 |
|----|------|
| 酉阳 | KML 缺失，YY-area 为空 |
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
| `区域地图_YY` | 重庆酉阳 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.2_GCJ02_MP_L2/农业基地/重庆酉阳-area.json` | ✅（空）|

**与 v7.1 geourl 差异：**

| 版本 | 常山 geourl |
|------|-------------|
| v7.1 | `…/农业基地_GCJ02_CS-area.json`（扁平）|
| v7.2 | `…/农业基地/浙江常山-area.json`（L2）|

**封板后已知限制（不修复）：** 酉阳 L2 为空；无地块 L3。

---

### `Agriculture_v7.3_GCJ02_L3.fvs` — FROZEN

| 项 | 值 |
|----|-----|
| 封板日期 | 2026-06-03 |
| 验收 | ✅ L3 目录、四基地大屏、FR 地图配置 L1/L2/L3 通过 |
| GeoJSON 目录 | `农业基地_v7.3_GCJ02_L3` |
| 大屏结构 | **四图** `区域地图_CS/WS/BS/YY`（固定，v7.4 单图另版）|
| 定位 | **当前生产版本**（基地 → 片区 → 地块）|

**geourl 路径表：**

| 组件名 | 基地 | geourl（相对 `WEB-INF/`）| 验证 |
|--------|------|--------------------------|------|
| `区域地图_CS` | 浙江常山 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/农业基地/浙江常山-area.json` | ✅ |
| `区域地图_WS` | 四川武胜 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/农业基地/四川武胜-area.json` | ✅ |
| `区域地图_BS` | 广西百色 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/农业基地/广西百色-area.json` | ✅ |
| `区域地图_YY` | 重庆酉阳 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.3_GCJ02_L3/农业基地/重庆酉阳-area.json` | ✅（空）|

**封板后已知限制（不修复）：** 酉阳无 KML；姜盘石等无坐标片区不在 L3。

**geourl 修复记录：** `scripts/ops/fr_patch_v73_geourl.py`（去除 `world/`、`v3_GCJ02`、无后缀 `.json`）。

---

## 🔧 开发 / 验证版本

### `Agriculture_v7.4_GCJ02_L3_SingleMap.fvs` — 📋 规划（未创建）

| 项 | 值 |
|----|-----|
| 目的 | 验证 **单张** `AREA_MAP` 能否替代四图（L1 入口或参数化 L2 geourl）|
| GeoJSON | **复用** `农业基地_v7.3_GCJ02_L3/`（不新建目录，除非单图需改数据）|
| 与 v7.3 差异 | 仅 FVS 组件数与切换 JS；v7.3 四图版本保持不变 |
| 创建方式 | 设计器复制 v7.3 → 重命名 v7.4 → 删三图留一图 → 改 geourl/切换逻辑 |
| 验收 | 四基地切换、片区树、高亮、下钻 L3；对比 v7.3 四图行为 |

**候选 geourl（待实测二选一）：**

| 方案 | geourl | 备注 |
|------|--------|------|
| A | `…/农业基地_v7.3_GCJ02_L3/农业基地-area.json` | L1 入口 + 地图内下钻 |
| B | 单图 + 参数/公式切换 L2 `农业基地/{基地名}-area.json` | 需设计器支持动态 geourl |

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

---

## 其他

### `Agriculture_v6.9_WGS84_Polygon.fvs`

| 项 | 值 |
|----|-----|
| 修复状态 | ✅ 手动修复（2026-06-03）|
| 说明 | 非生产；WGS84 已废弃 |
