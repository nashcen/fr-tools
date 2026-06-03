# 提案：data/source + data/sink 数据布局

**Change ID：** `agri-data-source-sink`  
**状态：** ✅ 已完成（2026-06-03）  
**日期：** 2026-06-03

## 问题

- 源数据（KML、Excel）与生成 GeoJSON 混在 `data/` 根下，与 FineReport `WEB-INF` 输出路径耦合。
- 生成脚本默认写 FR 安装目录，不利于 Git 管理、CI 测试与 SDD/TDD 闭环。

## 方案

```
data/
  source/          # 只读原始输入（KML、Excel、归档 JSON）
  sink/
    map/
      农业基地-大疆测绘/
        农业基地_v7.4_GCJ02_L3_SingleMap/   # 生成产物，与 FR geourl 目录名一致
        农业基地_v2_WGS84/                  # WGS84 对账 sidecar
```

- **生成默认输出：** `data/sink/map/农业基地-大疆测绘/{GEOJSON_VERSION}/`
- **部署：** 人工或 ops 脚本将 `sink` 同步至 `WEB-INF/.../农业基地-大疆测绘/`（不替代封板保护）
- **测试：** pytest 仍可用 `GEOJSON_OUTPUT_DIR` 指向临时目录；golden 结构不变

## 验收

- [x] 源数据全部位于 `data/source/`
- [x] 离线生成 v7.4 写入 `data/sink/map/.../农业基地_v7.4_.../`
- [x] `pytest` 全绿（27）
- [x] `openspec/specs/geojson.md`、`scripts.md` 已更新
