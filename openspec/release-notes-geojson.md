# GeoJSON 版本台账

**文件：** `openspec/release-notes-geojson.md`  
**最后更新：** 2026-06-03  
**部署根路径：** `WEB-INF/assets/map/geographic/农业基地-大疆测绘/`（FineReport，不在本 Git 仓）  
**本仓源数据：** `data/1.农业基地KML/`、`data/农业资产盘点明细.xlsx`

---

## 版本总览

| 版本目录 | 坐标系 | 几何 | 层级 | 基地 | 文件规范 | 封板 | 状态 |
|----------|--------|------|------|------|----------|------|------|
| `农业基地_v6.0_TEST` | GCJ-02 | Polygon | 1 | 常山 | 旧式 `.json` | ✅ FROZEN | 封板可用 |
| `农业基地_v6.9_WGS84_Polygon` | WGS-84 | Polygon | 1 | 4 | 旧式 | — | ❌ 废弃 |
| `农业基地_v7.0_GCJ02_Polygon` | GCJ-02 | Polygon | 1 | 4 | 旧式 `.json` | ✅ FROZEN | 封板可用 |
| `农业基地_v7.1_GCJ02_MultiPolygon` | GCJ-02 | MultiPolygon | 1 | 4 | 仅 `-area`/`-point` 扁平 | ✅ FROZEN | 封板可用（L1，可回退）|
| `农业基地_v7.2_GCJ02_MP_L2` | GCJ-02 | MultiPolygon | **2** | 3+空 | 目录层级 L2 | ✅ FROZEN | 封板可用（L2，可回退）|
| `农业基地_v7.3_GCJ02_L3` | GCJ-02 | MultiPolygon | **3** | 4 | 基地/片区/地块 | ✅ FROZEN | 封板可用（四图，可回退）|
| `农业基地_v7.4_GCJ02_L3_SingleMap` | GCJ-02 | MultiPolygon | **3** | 4 | 同 v7.3 | ✅ FROZEN | **生产基线（单图，验收通过）** |

> ⛔ 封板目录禁止修改，见 `CLAUDE.md`（**12** 项）。v7.1–v7.4 **禁止**无后缀 `农业基地_GCJ02_XX.json`。  
> v7.4 独立 GeoJSON 目录；FVS 单图绑 L1 `农业基地-area.json`。

---

## ✅ 封板版本

### `农业基地_v6.0_TEST` — FROZEN

| 文件 | 顶层 name | features | 几何 | FVS geourl |
|------|-----------|----------|------|------------|
| `农业基地_GCJ02.json` | `农业基地` | 122 | Polygon | ✅ |

---

### `农业基地_v7.0_GCJ02_Polygon` — FROZEN

| 基地 | 文件 | features | 片区去重 | FVS geourl |
|------|------|----------|----------|------------|
| CS | `农业基地_GCJ02_CS.json` | 368 | 24 | ✅ |
| WS | `农业基地_GCJ02_WS.json` | 507 | 37 | ✅ |
| BS | `农业基地_GCJ02_BS.json` | 10 | 2 | ✅ |
| YY | `农业基地_GCJ02_YY.json` | 0 | 0 | ✅ 空 |

已删除：`农业基地_GCJ02_CS_test.json`（2026-06-03）。

---

### `农业基地_v7.1_GCJ02_MultiPolygon` — FROZEN

| 项 | 值 |
|----|-----|
| 封板日期 | 2026-06-03 |
| 验收 | ✅ area/point 分离、FR 地图配置、点地图、四基地大屏预览通过 |
| 对应 FVS | `Agriculture_v7.1_GCJ02_MultiPolygon.fvs` |
| 定位 | L1 扁平 — **封板**（可回退；生产推荐 **v7.2**）|

| 基地 | area 文件 | 片区数 | point 数 |
|------|-----------|--------|----------|
| CS | `农业基地_GCJ02_CS-area.json` | 24 | 24 |
| WS | `农业基地_GCJ02_WS-area.json` | 37 | 37 |
| BS | `农业基地_GCJ02_BS-area.json` | 2 | 2 |
| YY | `农业基地_GCJ02_YY-area.json` | 0 | 0 |

仅 8 个 `*-area.json` / `*-point.json`，禁止无后缀 `.json`。

---

### `农业基地_v7.2_GCJ02_MP_L2` — FROZEN

| 项 | 值 |
|----|-----|
| 封板日期 | 2026-06-03 |
| 验收 | ✅ L1/L2 目录、FR 地图配置、四基地大屏通过 |
| 对应 FVS | `Agriculture_v7.2_GCJ02_MP_L2.fvs` |
| 生成脚本 | `scripts/active/geojson_generate_from_kml.py`（`GCJ02_DIR` 指向本目录）|
| 定位 | L2 两层 — **封板**（可回退；生产推荐 **v7.3**）|

**目录结构（对照 `world/中国`）：**

| FR 内置 | v7.2 农业 |
|---------|-----------|
| `中国-area.json` | `农业基地-area.json` |
| `中国-point.json` | `农业基地-point.json` |
| `中国/浙江省-area.json` | `农业基地/浙江常山-area.json` |
| `中国/浙江省-point.json` | `农业基地/浙江常山-point.json` |

```
农业基地_v7.2_GCJ02_MP_L2/
  农业基地-area.json          ← L1：3 基地（酉阳无 KML）
  农业基地-point.json
  农业基地/
    浙江常山-area.json        ← L2：24 片区
    浙江常山-point.json
    四川武胜-area.json        ← 37 片区
    …（百色 2、酉阳 0）
```

| 层级 | 文件 | features | 几何 |
|------|------|----------|------|
| L1 | `农业基地-area.json` | 3 | MultiPolygon |
| L2 常山 | `农业基地/浙江常山-area.json` | 24 | MultiPolygon |
| L2 武胜 | `农业基地/四川武胜-area.json` | 37 | MultiPolygon |
| L2 百色 | `农业基地/广西百色-area.json` | 2 | MultiPolygon |
| L2 酉阳 | `农业基地/重庆酉阳-area.json` | 0 | — |

**与 v7.1：** 扁平 `农业基地_GCJ02_CS-area.json` → L2 `农业基地/浙江常山-area.json`。

---

### `农业基地_v7.3_GCJ02_L3` — FROZEN

| 项 | 值 |
|----|-----|
| 封板日期 | 2026-06-03 |
| 验收 | ✅ L1/L2/L3 目录、四基地大屏、FR 地图配置通过 |
| 对应 FVS | `Agriculture_v7.3_GCJ02_L3.fvs`（**四图**，L2 geourl）|
| 定位 | L3 四图 — **封板**（可回退；生产推荐 **v7.4**）|

```
农业基地_v7.3_GCJ02_L3/
  农业基地-area.json
  农业基地-point.json
  农业基地/
    浙江常山-area.json          ← L2（FVS geourl）
    浙江常山/
      {片区名}-area.json        ← L3 地块
    …（武胜/百色/酉阳同结构）
```

---

### `农业基地_v7.4_GCJ02_L3_SingleMap` — FROZEN（生产基线）

| 项 | 值 |
|----|-----|
| 封板日期 | 2026-06-03 |
| 验收 | ✅ 单图四基地切换、树视图、高亮、L3 下钻通过 |
| 对应 FVS | `Agriculture_v7.4_GCJ02_L3_SingleMap.fvs`（**单图**，L1 geourl）|
| 定位 | **当前生产版本**（L3 目录 + 单 `区域地图`）|

目录树与 v7.3 同结构；FVS geourl 绑 L1 `农业基地-area.json`。

---

## ⚠ 归档

### `农业基地_v6.9_WGS84_Polygon` — ❌ 废弃（WGS84 偏移）

---

## 版本命名规范

```
农业基地_v{major}.{minor}_{坐标系}_{几何}_{层级}
```

| 后缀 | 含义 |
|------|------|
| `Polygon` / `MultiPolygon` | 几何类型 |
| `MP` | MultiPolygon 缩写 |
| `L2` | 2 层层级（基地/片区）|
| `L3` | 3 层层级（+地块）|

---

## 变更历史

| 日期 | 版本 | 事件 |
|------|------|------|
| 2026-06-03 | v7.0 | 抽检；删除 CS_test |
| 2026-06-03 | v7.1 | 验收通过并封板（生产基线） |
| 2026-06-03 | v7.2 | 重命名为 `GCJ02_MP_L2`；部署 L2 目录树；FVS geourl 指向 `农业基地/{基地}-area.json` |
| 2026-06-03 | v7.2 | 验收通过并封板 |
| 2026-06-03 | v7.3 | geourl 修复（`fr_patch_v73_geourl.py`）；四图 L2 绑定 |
| 2026-06-03 | v7.3 | 验收通过并封板（生产基线）；`CLAUDE.md` 封板 **10** 项 |
| 2026-06-03 | v7.4 | 目录 `农业基地_v7.4_GCJ02_L3_SingleMap`；单图 FVS L1 geourl |
| 2026-06-03 | v7.4 | 验收通过并封板（生产基线）；`CLAUDE.md` 封板 **12** 项 |
