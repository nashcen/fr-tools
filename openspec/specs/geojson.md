# 规范：GeoJSON 片区边界数据

**规范 ID：** `geojson`  
**版本：** v5（2026-06-03，data/source + data/sink）  
**状态：** 生效中

---

## 一、数据链路

```
大疆测绘 KML + 盘点 Excel（只读）
  data/source/1.农业基地KML/
  data/source/农业资产盘点明细.xlsx
      ↓ scripts/active/geojson_generate_from_kml.py
      ↓ scripts/versions/{GeoJSON目录名}/（版本入口，见 specs/scripts.md）
  GCJ-02 三层层级 + 可选 legacy 合并 json
      → data/sink/{版本}/
  v2 对账 sidecar
      → data/source/农业基地_v2_WGS84/   # v2 对账 sidecar（非 sink）
      ↓ ops/sync_sink_map_to_finereport.sh（部署，封板目录慎用 PROTECT_EXISTING）
  WEB-INF/assets/map/geographic/农业基地-大疆测绘/{版本}/
      ↓ FR「同步地理文件」+ FVS geourl
  大屏加载
```

---

## 二、FineReport 地图三层层级

对照 FineReport 省/市内置地图的目录规范（`中国-area.json`→`中国/浙江省-area.json`），
农业基地地图采用**三层层级**，在帆软地图配置页面可见清晰的三级导航。

| 层级 | 类比 | 每个 feature | 几何类型 | 名称来源 |
|------|------|-------------|----------|----------|
| 基地 | 省 | 1个基地的所有片区 union | MultiPolygon | — |
| 片区 | 市 | 1个片区（含多块地 union）| MultiPolygon | `ods_ag_base_v2.片区名称` |
| 地块 | 县 | 1个地块（含多个子地块 union）| Polygon / MultiPolygon | `农业资产盘点明细.xlsx 地块名称` |

**片区 ID 严格参照 `ods_ag_base_v2` 表**（片区名称字段），地块名称严格参照**「农业资产盘点明细.xlsx」**。

---

## 三、目录结构（部署路径）

**根路径：** `WEB-INF/assets/map/geographic/world/农业基地-大疆测绘/`

```
农业基地_v3_GCJ02/                      ← v3 标准格式（FR geourl 指向此目录）
  农业基地-area.json                    ← 层级1：基地（3/4 个 MultiPolygon）
  农业基地-point.json
  农业基地/
    浙江常山-area.json                  ← 层级2：片区（24 个 MultiPolygon）
    浙江常山-point.json
    四川武胜-area.json                  ← 37 个片区
    四川武胜-point.json
    广西百色-area.json                  ← 2 个片区
    广西百色-point.json
    重庆酉阳-area.json                  ← 7 个片区（KML 已入库，2026-06-03）
    重庆酉阳-point.json
    浙江常山/
      双溪口1-area.json                 ← 层级3：地块（5 个 Polygon/MultiPolygon）
      双溪口1-point.json
      大埂-area.json                    ← 9 个地块
      ...（共 24 个片区各一对文件）
    四川武胜/
      三溪西区-area.json                ← 单地块片区
      ...（共 37 个片区）
    广西百色/
      平林-area.json                    ← 9 个地块（平林1~平林9）
      龙细-area.json                    ← 1 个地块
  农业基地_GCJ02_CS.json               ← 旧格式（仅 v6/v7.0 封板；单文件 Polygon，无 -area/-point 分离）
  农业基地_GCJ02_WS.json
  农业基地_GCJ02_BS.json
  农业基地_GCJ02_YY.json

农业基地_v7.1_GCJ02_MultiPolygon/       ← v7.1 封板：扁平 L1，仅 -area/-point，禁止无后缀 .json

农业基地_v7.2_GCJ02_MP_L2/             ← v7.2 封板：L2 两层（类比 中国/浙江省）
  农业基地-area.json                    ← L1 基地
  农业基地-point.json
  农业基地/
    浙江常山-area.json                  ← L2 片区（FVS 区域地图_CS geourl）
    浙江常山-point.json
    四川武胜-area.json
    …
  ⛔ 勿放置 农业基地_GCJ02_XX.json（点地图异常）

农业基地_v7.3_GCJ02_L3/                 ← v7.3 封板（四图，可回退）：L3 三层
农业基地_v7.4_GCJ02_L3_SingleMap/       ← v7.4 封板（生产单图）：L3 结构；FVS geourl 绑 L1 农业基地-area.json
  农业基地-area.json                    ← L1
  农业基地/
    浙江常山-area.json                  ← L2（FVS 区域地图_CS geourl）
    浙江常山/
      {片区名}-area.json                ← L3 地块
  …（武胜/百色/酉阳同结构）

农业基地_v2_WGS84/                      ← v2 完整属性（DB 对账用）
农业基地_v1_TEST/                       ← v1 旧版（归档保留）
```

**本地归档路径：** `data/source/2.农业基地JSON/`（只读参考，非生成入口）

---

## 四、数据格式规范

### 命名规范（FR 标准）

```
{区域名}-area.json   ← 区域多边形（Polygon / MultiPolygon）
{区域名}-point.json  ← 点标注（Point，无 center 字段）
```

- `area.json` 顶层**必须有 `name` 字段**，值为区域名称（FR 渲染必需）
- `point.json` 顶层无 `name` 字段（遵循 FR 内置约定）
- **v7.1+ 目录禁止**无 `-area`/`-point` 后缀的 `{名}.json`（area/point 混写或 area-only 合并文件均会导致点地图异常）
- **FVS geourl（v7.1+）** 必须指向 `{名}-area.json`，不得指向无后缀 `.json`

### area.json 格式

```json
{
  "type": "FeatureCollection",
  "name": "浙江常山",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "双溪口1",
        "center": [118.5431354412, 29.0039625158]
      },
      "geometry": {
        "type": "MultiPolygon",
        "coordinates": [[[[lng, lat], ...]]]
      }
    }
  ]
}
```

### point.json 格式

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": { "name": "双溪口1" },
      "geometry": { "type": "Point", "coordinates": [lng, lat] }
    }
  ]
}
```

**规则：**
- 顶层 `name` 字段必须存在（值为上一级区域名称）— **v6 不显示的根因**
- `properties.name` 为区域名称，片区级与 DB `ods_ag_base_v2.片区名称` 严格一致
- `properties.center` 为 `[经度, 纬度]`（GCJ-02，area.json 含，point.json 不含）
- ✅ `MultiPolygon` 在 `d-chart-AREA_MAP` 中**已确认支持**（2026-06-03 实测）
- 片区级：同一片区多个 Polygon 合并为单一 `MultiPolygon`，区域列表无重复
- 地块级：可为 `Polygon`（单块）或 `MultiPolygon`（多块地块）
- 坐标格式：`[经度, 纬度]`（经度在前，GCJ-02）

---

## 五、覆盖情况

| 基地 | DB 片区数 | GeoJSON 片区数 | 地块数 | 片区覆盖率 |
|------|-----------|----------------|--------|-----------|
| 浙江常山 | 24 | 24 | ~167 | 100% |
| 四川武胜 | 37 | 37 | ~62 | 100% |
| 广西百色 | 2 | 2 | 10 | 100% |
| 重庆酉阳 | 16（Excel）| 7 | 0 | 44%（9 片区待 KML：后溪/大地/杉岭/水田/溪口/石堤/茶店/车坝/鱼水村）|
| **合计** | **79** | **70** | — | **89%** |

---

## 六、更新流程

```
1. 获取新 KML 文件 → 放入 1.农业基地KML/
2. 运行对应版本脚本（封板用 `scripts/versions/{GeoJSON目录名}/`，开发用 `scripts/active/`）
3. 更新 `openspec/release-notes-scripts.md` 并将新快照纳入 Git
4. 检查输出：
   - 农业基地-area.json 基地数
   - 农业基地/{基地名}-area.json 片区数
   - 农业基地/{基地名}/{片区名}-area.json 地块数
5. FineReport 管理后台「地图配置」→「同步地理文件」
6. 验证大屏各基地 chart 正常渲染
```

---

## 七、已知缺陷

| 优先级 | 问题 | 状态 |
|--------|------|------|
| P1 | 重庆酉阳 9 个片区无 KML（后溪/大地/杉岭/水田/溪口/石堤/茶店/车坝/鱼水村） | ⏳ 待补充 |
| P2 | 四川武胜多地块片区（干家湾宝箴塞/会云/金狮等）KML 名称无法精确映射到 Excel 地块 | ⚠ 已知偏差 |
| P2 | 四川武胜「姜盘石」片区无 KML 边界 | ⏳ 待补充 |
| P3 | 重庆酉阳无 KML，基地级 area.json 仅含 3 个基地（缺酉阳） | ✅ 已解决（2026-06-03，L1 四基地 + 酉阳 7 片区）|

---

## 变更历史

| 版本 | 日期 | Change ID | 主要变更 |
|------|------|-----------|----------|
| v2 | 2026-06-02 | `agri-bigscreen-v7-archive` | 生成脚本修复（育苗中心保留逻辑 + buffer(0) 自相交修复）；63 片区坐标更新为 GCJ-02 |
| v3 | 2026-06-03 | `agri-bigscreen-v7-archive` | 部署目录从 `world/中国/` 迁移至 `world/农业基地-大疆测绘/`；新增 `农业基地_v3_GCJ02/` |
| v3.1 | 2026-06-03 | 实测验证 | ✅ 确认 `d-chart-AREA_MAP` 支持 `MultiPolygon`；片区合并为单一 MultiPolygon |
| v4 | 2026-06-03 | — | 三层层级重构（基地/片区/地块）；FR 标准 area.json+point.json 分离格式；地块名称参照农业资产盘点明细.xlsx；脚本自动生成全量层级文件 |
| v5 | 2026-06-03 | `agri-youyang-kml` | 酉阳 KML + Excel 合同映射；v7.0–v7.4 sink/FR 验收通过 |
