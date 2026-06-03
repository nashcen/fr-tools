# 提案：v7.4 单图 AREA_MAP 验证

**Change ID：** `agri-v74-single-map`  
**创建日期：** 2026-06-03  
**状态：** ✅ 验收通过并封板（2026-06-03，生产基线 v7.4）  
**前置：** v7.3 保持四图并完成 L3 验收

---

## 背景

v7.3 采用与 v7.2 相同的 **四图叠放**（`区域地图_CS/WS/BS/YY`），geourl 各绑 L2 `农业基地/{基地名}-area.json`，GeoJSON 目录为 L3 三层。

已确认：**不因 v7.3 目录格式改为单图**；单图方案在独立版本试错，避免影响 v7.2 生产封板与 v7.3 验收。

## 目标

新建 `Agriculture_v7.4_GCJ02_L3_SingleMap.fvs`，验证能否用 **一个** `AREA_MAP` 实现：

- 四基地切换（`base` 参数）
- 片区树定位 / 高亮
- L3 地块下钻（若 FR 运行时支持）

## 非目标

- 不修改封板 FVS / GeoJSON（v6 / v7.0 / v7.1 / v7.2）
- 不修改 `Agriculture_v7.3_GCJ02_L3.fvs` 四图结构
- GeoJSON 目录：`农业基地_v7.4_GCJ02_L3_SingleMap/`（与 v7.3 同结构，独立目录）

## 方案草图

| 项 | 内容 |
|----|------|
| FVS | 从 v7.3 复制 → 删 3 图留 1 图 → 调整 geourl 与切换 JS |
| geourl 候选 A | L1：`…/农业基地-area.json` |
| geourl 候选 B | 参数化 L2：`…/农业基地/{基地名}-area.json` |
| 对照组 | v7.3 四图（不变） |

## 成功标准

- [x] FVS geourl + JS 单图改造（`fr_patch_v74_single_map.py`）
- [x] 四基地切换视野与片区显示不低于 v7.3 四图（2026-06-03 验收通过）
- [ ] 片区树 / 点击高亮可用
- [ ] 记录单图 vs 四图结论（采用 / 放弃 / 仅归档）

## 参考

- `openspec/release-notes-fvs.md` — v7.4 规划表
- `openspec/specs/bigscreen.md` — §4.1 四图 vs v7.4
