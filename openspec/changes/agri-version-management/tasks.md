# 实施任务：GeoJSON 与 FVS 版本管理规范

**Change ID：** `agri-version-management`

---

## Phase 0：基础建设（✅ 已完成）

- [x] 创建 `CLAUDE.md`，封板文件 + 3 次确认保护规则
- [x] 确认封板绑定（v6.0 / v7.0 / **v7.1** ↔ 对应 GeoJSON 目录）
- [x] v7.1 验收通过并封板（2026-06-03，`CLAUDE.md` 6 项 FROZEN）
- [x] v7.2 验收通过并封板（2026-06-03，`CLAUDE.md` 8 项 FROZEN）
- [x] v7.3 验收通过并封板（2026-06-03 生产基线，`CLAUDE.md` 10 项 FROZEN）
- [x] 创建 `openspec/release-notes-geojson.md`（所有版本记录、封板标注、问题诊断）
- [x] 创建 `openspec/release-notes-fvs.md`（所有版本记录、geourl 有效性检查、封板标注）
- [x] 清理根目录陈旧文档（删除 6 份：大屏分析报告、GeoJSON格式说明、ods 工作文档、claude-mem-setup）
- [x] 更新 `openspec/project.md`（目录结构重写、变更列表补充）

## Phase 0.5：fr-tools 仓库迁移（✅ 已完成）

- [x] 从 `P2025-G-001-数智部-农业大屏一期 ★/` 迁出核心文件至本仓
- [x] 新增根目录 `README.md`（迁移原因、目录、路径对照、快速开始）
- [x] 更新 `CLAUDE.md`、`openspec/project.md`、`specs/scripts.md`、`specs/geojson.md`
- [x] 更新 `scripts/README.md`、`release-notes-scripts.md`、`release-notes-geojson.md` 中的路径
- [x] `scripts/active/geojson_generate_from_kml.py`：`KML_DIR` / `EXCEL_PATH` 指向 `data/`
- [x] `scripts/versions/_shared/geojson_patch_missing_from_kml.py`：KML 路径指向 `data/1.农业基地KML/`

---

## Phase 1：FVS geourl 修复（`5.农业大屏二期/` 非封板版本）

> **封板版本不得修改。** 所有非封板 FVS 的共同根因：geourl 含 `world/` 前缀 + 目录名使用已废弃的 `农业基地_v3_GCJ02/`。

- [x] 1.1 `Agriculture_v6.9_WGS84_Polygon.fvs` — 手动修复（2026-06-03，含天地图配置）

- [x] 1.2 修复 `Agriculture_v7.1_GCJ02_MultiPolygon.fvs`
  - geourl：`农业基地-大疆测绘/农业基地_v7.1_GCJ02_MultiPolygon/农业基地_GCJ02_{CS/WS/BS/YY}-area.json`（禁止无后缀 `.json`）
  - [x] 测试验证：地图配置 + 大屏预览通过（2026-06-03）
  - [x] 更新 release-notes-fvs.md（geourl 表格台账）

- [x] 1.3 `Agriculture_v7.2_GCJ02_MP_L2.fvs` — geourl 指向 L2 `农业基地/{基地名}-area.json`（2026-06-03）
  - [x] FR 地图配置 L1/L2 树 + 大屏验收（2026-06-03 封板）
  - [x] release-notes-fvs.md / release-notes-geojson.md

- [x] 1.4 修复 `Agriculture_v7.3_GCJ02_L3.fvs` geourl（2026-06-03，`fr_patch_v73_geourl.py`）
  - 四图 → `农业基地_v7.3_GCJ02_L3/农业基地/{基地名}-area.json`（L2，对齐 GeoJSON L3 树）
  - [x] 用户验收：FR「同步地理文件」+ 地图配置 L1/L2/L3 + 大屏预览（2026-06-03 封板）
  - [x] 版本策略：v7.3 **保持四图**；单图试验列入 **v7.4**（不修改 v7.3 结构）
  - [x] 更新 release-notes-fvs.md

## Phase 1.5：v7.4 单图验证（🔧 待验收）

- [x] `Agriculture_v7.4_GCJ02_L3_SingleMap.fvs` + `农业基地_v7.4_GCJ02_L3_SingleMap/`
- [x] 单图 `区域地图`，geourl L1（`fr_patch_v74_single_map.py`）
- [x] 基地切换 JS：去掉四图 setVisible，统一 `panTo(区域地图)`
- [x] v7.3 临时文件清理（`fr_cleanup_v73_temp.py`）
- [x] 更新 release-notes / `agri-v74-single-map` tasks
- [ ] 用户验收：切换、树、高亮、L3 下钻

---

## Phase 2：GeoJSON 格式验证（非封板版本）

- [x] 2.1 验证 `农业基地_v7.1_GCJ02_MultiPolygon/`
  - [x] area/point 分离修复（脚本 `geojson_fix_area_point_split.py`）
  - [x] 检查各基地 `-area.json` 顶层 `name`、仅 MultiPolygon
  - [x] 检查 `point.json` features 数量（CS/WS 各 24/37）
  - [x] 更新 release-notes-geojson.md
  - [x] FR 地图配置 + 点地图验收通过（2026-06-03）
  - [x] release-notes-geojson.md 表格化关键信息

- [x] 2.2 部署 `农业基地_v7.2_GCJ02_MP_L2/` L2 目录树（10 个 json，无 L3 子目录）
  - [x] FR「同步地理文件」+ 地图配置验收（2026-06-03 封板）
  - [x] release-notes-geojson.md

- [x] 2.3 验证 `农业基地_v7.3_GCJ02_L3/`（2026-06-03 封板）
  - [x] 三层目录完整（基地 → 片区 → 地块）
  - [x] FR 地图配置 + 大屏验收
  - [x] release-notes-geojson.md

---

## Phase 3：规范文档补充

- [ ] 3.1 `openspec/specs/geojson.md` 补充版本目录命名规范章节
  - 格式：`农业基地_v{major}.{minor}_{坐标系}_{几何描述}`
  - 版本更新流程末尾加入「更新 release-notes-geojson.md」步骤

- [ ] 3.2 `openspec/specs/bigscreen.md` 补充 FVS 版本命名规范章节

- [x] 3.3 `openspec/release-notes-scripts.md` + `scripts/versions/` 分版本快照（2026-06-03）
- [x] 3.4 `openspec/specs/scripts.md` — 目录/文件命名规范；`active/lib/ops/versions` 重组（2026-06-03）
  - 格式：`Agriculture_v{GeoJSON版本}_{坐标系}_{几何描述}.fvs`（与 GeoJSON 命名对齐）
  - 版本更新流程加入「更新 release-notes-fvs.md」步骤

---

## 完成检查表

- [x] 封板保护建立
- [x] release-notes 初版建立
- [x] 陈旧文档清理
- [x] project.md 更新
- [ ] Phase 1：4 个 FVS geourl 修复完成
- [ ] Phase 2：3 个 GeoJSON 版本格式验证完成
- [ ] Phase 3：specs 规范补充完成
- [ ] 准备执行 `/openspec-archive agri-version-management`
