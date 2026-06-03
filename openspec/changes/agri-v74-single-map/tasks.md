# 实施任务：v7.4 单图 AREA_MAP

**Change ID：** `agri-v74-single-map`

---

## Phase 0：v7.3 清理（✅）

- [x] 删除 `Agriculture_v7.3_GCJ02_L3.fvs.bak-*`
- [x] 删除 `农业基地_v7.3_GCJ02_L3/` 下 `.DS_Store`（`fr_cleanup_v73_temp.py`）

## Phase 1：v7.4 资产（✅）

- [x] GeoJSON 目录 `农业基地_v7.4_GCJ02_L3_SingleMap/`（与 v7.3 同 L3 结构）
- [x] FVS `Agriculture_v7.4_GCJ02_L3_SingleMap.fvs`（单组件 `区域地图`）

## Phase 2：FVS 单图逻辑（✅）

- [x] geourl → L1 `…/农业基地_v7.4_GCJ02_L3_SingleMap/农业基地-area.json`（`fr_patch_v74_single_map.py`）
- [x] 移除四图 `区域地图_CS/WS/BS/YY` 的 `setVisible`
- [x] 基地切换 / 树视图 `panTo` 统一为 `区域地图`
- [ ] 用户验收：四基地切换、片区树、高亮、L3 下钻

## Phase 3：文档与脚本（✅）

- [x] `scripts/active` `GCJ02_DIR` → v7.4 目录
- [x] `scripts/versions/农业基地_v7.4_GCJ02_L3_SingleMap/` 快照
- [x] 更新 release-notes / bigscreen / project
