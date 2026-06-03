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
| `Agriculture_v7.1_GCJ02_MultiPolygon.fvs` | `农业基地_v7.1_GCJ02_MultiPolygon` | ✅ | ✅ FROZEN | 封板可用（推荐生产）|
| `Agriculture_v7.2_GCJ02_MP_L2.fvs` | `农业基地_v7.2_GCJ02_MP_L2` | ✅ | — | 🔧 L2 验证中 |
| `Agriculture_v7.3_GCJ02_L3.fvs` | `农业基地_v7.3_GCJ02_L3` | ❌ | — | 🔧 待修复 |

> ⛔ 封板版本禁止修改，见 `CLAUDE.md`。

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
| 定位 | **四基地 MultiPolygon 推荐生产版本** |

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

## 🔧 开发 / 验证版本

### `Agriculture_v7.2_GCJ02_MP_L2.fvs`

| 项 | 值 |
|----|-----|
| 命名 | `MP_L2` = MultiPolygon + **2 层层级**（基地/片区，类比省/市）|
| 目标 | 验证 FR 地图配置两层目录 + 四基地大屏 geourl 绑 **L2** 片区文件 |
| GeoJSON 目录 | `农业基地_v7.2_GCJ02_MP_L2` |
| 层级 | L1 `农业基地-area.json`；L2 `农业基地/{基地名}-area.json` |
| 不含 | 地块 L3 子目录（见 v7.3）|

**geourl 路径表（2026-06-03 已修正）：**

| 组件名 | 基地 | geourl（相对 `WEB-INF/`）| 验证 |
|--------|------|--------------------------|------|
| `区域地图_CS` | 浙江常山 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.2_GCJ02_MP_L2/农业基地/浙江常山-area.json` | ✅ |
| `区域地图_WS` | 四川武胜 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.2_GCJ02_MP_L2/农业基地/四川武胜-area.json` | ✅ |
| `区域地图_BS` | 广西百色 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.2_GCJ02_MP_L2/农业基地/广西百色-area.json` | ✅ |
| `区域地图_YY` | 重庆酉阳 | `assets/map/geographic/农业基地-大疆测绘/农业基地_v7.2_GCJ02_MP_L2/农业基地/重庆酉阳-area.json` | ✅（空）|

**与 v7.1 geourl 差异：**

| 版本 | 常山 geourl 文件名 |
|------|-------------------|
| v7.1 | `…/农业基地_GCJ02_CS-area.json`（扁平）|
| v7.2 | `…/农业基地/浙江常山-area.json`（L2 目录）|

**待验证：** FR「同步地理文件」后 L1→L2 树可见；大屏四基地渲染。

---

### `Agriculture_v7.3_GCJ02_L3.fvs`

| 项 | 值 |
|----|-----|
| 当前 geourl 问题 | 含 `world/`；目录错误；应为三层层级单入口 |
| 目标 geourl | `.../农业基地_v7.3_GCJ02_L3/农业基地-area.json` |
| 前置条件 | FR「地图配置 → 同步地理文件」|
| 修复状态 | ⬜ 未开始 |

---

## geourl 路径规则

| 规则 | 说明 |
|------|------|
| 前缀 | `assets/map/geographic/农业基地-大疆测绘/{版本目录}/` |
| 禁止 | 路径中含 `world/`（内置地图专用）|
| v6 / v7.0 封板 | `{基地}.json` 无后缀（勿改）|
| **v7.1 封板** | 必须 `{基地}-area.json`；目录内禁止无后缀 `.json`（点地图异常）|
| v7.2 L2 | `农业基地/{基地名}-area.json`（两层目录）|
| v7.3 L3 | `农业基地-area.json` 入口 + 地块子目录 |

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

---

## 其他

### `Agriculture_v6.9_WGS84_Polygon.fvs`

| 项 | 值 |
|----|-----|
| 修复状态 | ✅ 手动修复（2026-06-03）|
| 说明 | 非生产；WGS84 已废弃 |
