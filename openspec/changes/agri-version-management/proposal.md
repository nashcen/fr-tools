# 提案：农业大屏 GeoJSON 与 FVS 版本管理规范

**Change ID：** `agri-version-management`  
**创建日期：** 2026-06-03  
**状态：** 进行中

---

## 问题陈述

GeoJSON 文件和 FVS 文件存在以下混乱：

- **GeoJSON**：6 个版本目录并列存在，缺少可用性标注，无法判断哪个是生效版本
- **FVS**：文件分散在多个目录，版本与 GeoJSON 绑定关系不明确，无 release notes
- **陈旧文档**：根目录散落多份一次性工作文档（DB 变更稿、GeoJSON 格式说明、大屏分析报告），与 openspec 内容重复且过时
- **全量项目目录**：`1.项目规划`～`6.开发实现` 等层级过深，有效资产与历史文件混杂，不利于 Git 与 AI 协作

## 提案方案

1. **封板基准版本**：v6.0 / v7.0 / v7.1 / v7.2 / v7.3 / **v7.4** 封板（**12** 项 FROZEN），建立 3 次确认保护机制
2. **统一 FVS 目录**：所有 FVS 统一管理于 `5.农业大屏二期/`，与 GeoJSON 版本一一对应命名
3. **建立 release notes**：`release-notes-geojson.md` + `release-notes-fvs.md` 记录每个版本的 feature/bug/geourl 有效性/可用性
4. **清理陈旧文档**：删除根目录非 openspec 管理的历史文档
5. **迁移至 `fr-tools` 精简仓**（2026-06-03）：仅保留 `data/`、`scripts/`、`openspec/`；文档路径由 `6.开发实现/scripts/` → `scripts/`，KML/Excel 由 `5.数据设计/...` → `data/`

## 范围

### In Scope
- `CLAUDE.md` 封板保护规则（**8** 项 FROZEN：含 v7.1 + v7.2，3 次确认机制）
- `openspec/release-notes-geojson.md`（GeoJSON 版本台账）
- `openspec/release-notes-fvs.md`（FVS 版本台账，含 geourl 有效性诊断）
- `openspec/specs/geojson.md` 补充版本目录命名规范
- `openspec/specs/bigscreen.md` 补充 FVS 版本命名与 release notes 维护规范
- 清理根目录陈旧文档（已完成）
- 逐一修复 `5.农业大屏二期/` 中非封板 FVS 的 geourl 错误
- 逐一验证非封板 GeoJSON 版本的格式合规性

### Out of Scope
- `1.农业大屏/` 历史归档目录（只读，不参与管理）
- FVS 功能迭代（属于独立 change）
- 旧版本文件物理删除（保留归档，仅标注状态）

## 影响分析

| 组件 | 变更 | 说明 |
|------|------|------|
| FVS 文件内容 | geourl 修复 | 4 个非封板 FVS 的 geourl 路径错误需修正 |
| GeoJSON | 无内容变更 | 仅验证格式合规性 |
| 文档 | ✅ 已完成 | release-notes 新增；陈旧文档已删除；project.md / CLAUDE.md / README.md 已更新 |
| 代码仓 | ✅ 已完成 | `fr-tools` 迁移；`data/` + `scripts/` 路径对齐；`active/` 脚本指向本仓 `data/` |

## 当前版本现状

### FVS + GeoJSON（`5.农业大屏二期/` ↔ `农业基地-大疆测绘/`）

FVS 与 GeoJSON **一一对应命名**，6 个版本：

| FVS / GeoJSON 版本 | 封板 | geourl 有效 | 可用性 |
|--------------------|------|------------|--------|
| `v6.0_TEST` | ✅ FROZEN | ✅ | ✅ 可用（常山单基地）|
| `v6.9_WGS84_Polygon` | — | ❌ | 🔧 待修复（geourl 含 `world/` + 目录名错）|
| `v7.0_GCJ02_Polygon` | ✅ FROZEN | ✅ | ✅ 可用（四基地）|
| `v7.1_GCJ02_MultiPolygon` | ✅ FROZEN | ✅ | ✅ **生产基线**（2026-06-03 验收通过并封板）|
| `v7.2_GCJ02_MP_L2` | ✅ FROZEN | ✅ | ✅ **生产基线**（2026-06-03 验收通过并封板）|
| `v7.3_GCJ02_L3` | ✅ FROZEN | ✅ | ✅ 封板（四图，可回退）|
| `v7.4_GCJ02_L3_SingleMap` | ✅ FROZEN | ✅ | ✅ **生产基线**（2026-06-03 验收通过并封板）|

**共同根因（非封板版本）：** geourl 含错误 `world/` 前缀，且目录名使用了已不存在的旧路径 `农业基地_v3_GCJ02/`

## 成功标准

- [x] CLAUDE.md 封板保护建立（**12** 项 FROZEN，含 v7.1–v7.4，3 次确认）
- [x] release-notes-geojson.md 建立（所有版本记录完整）
- [x] release-notes-fvs.md 建立（含 geourl 有效性诊断）
- [x] 根目录陈旧文档清理（6 份已删除）
- [x] openspec/project.md 更新（目录结构 + 变更列表）
- [ ] 4 个非封板 FVS geourl 修复并测试验证
- [ ] 非封板 GeoJSON 版本格式验证完毕
- [ ] specs/geojson.md + bigscreen.md 补充版本命名与流程规范

## 风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| FVS geourl 修复后仍不显示 | 低 | 中 | 修复后在 FR 设计器预览验证，记录修复结果 |
| v7.3 三层层级 geourl 结构变化导致 FR 无法识别 | 中 | 中 | 先执行「同步地理文件」，验证 FR 地图配置可见层级 |
| release-notes 与实际状态不同步 | 中 | 中 | 每次修复后立即更新对应条目，作为任务完成条件之一 |
