# Change: 重庆酉阳 KML 入库与五版本验收

**Change ID:** `agri-youyang-kml`  
**状态:** 已完成并归档（2026-06-03）  
**关联:** `data/source/1.农业基地KML/4.酉阳地图KML/酉阳地图KML导出_20260602130151.kml`

## 背景

封板前 GeoJSON/FVS 台账记载酉阳为空；大疆测绘 KML 到达后需在不改动封板 FVS 结构的前提下补全地图数据。

## 范围

- 脚本：`youyang_kml.py`、`excel_hierarchy` 合同映射、`GEOJSON_BASES` 过滤
- 输出：`data/sink/` 五版本目录中酉阳 7 片区（下腴、平桥、桂香、龙沙、清溪、响水、小河）
- 部署：用户手工同步至 FineReport `WEB-INF/.../农业基地-大疆测绘/{版本}/`
- **不修改** `CLAUDE.md` 所列 12 项封板 FVS 文件内容（仅 GeoJSON 资产更新）

## 验收

| 项 | 结果 |
|----|------|
| pytest | 51 passed（含 v7.0/v7.1 酉阳断言）|
| FR 手工 | v7.0–v7.4 五版本切换酉阳，地图正常展示 |
| 封板 | 维持 FROZEN；台账见 `release-notes-geojson.md` / `release-notes-fvs.md` |

## 残留

Excel 16 片区中 9 个仍无 KML（见 `openspec/specs/geojson.md` P1）。
