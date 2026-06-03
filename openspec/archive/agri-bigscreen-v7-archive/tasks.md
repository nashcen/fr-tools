# 实施任务：农业大屏 v6→v7 升级归档

**Change ID：** `agri-bigscreen-v7-archive`

---

## Phase 1：基础设施（文档目录）

- [x] 1.1 创建 `openspec/` 目录结构（`specs/`、`changes/`）
- [x] 1.2 编写 `openspec/project.md`（项目约定、版本历史、关键约束）
- [x] 1.3 更新 `大屏分析报告.md` 标题为 v6/v7，增加 §三-C 变更记录

**Quality Gate：**
- [x] 目录结构存在且命名规范
- [x] project.md 包含技术栈、目录规范、版本历史

---

## Phase 2：核心规范文档

- [x] 2.1 提取 `openspec/specs/bigscreen.md`（功能区划分、全局参数、数据源、切换逻辑、片区交互）
- [x] 2.2 提取 `openspec/specs/geojson.md`（数据链路、版本目录、文件清单、格式规范、覆盖情况、更新流程）
- [x] 2.3 确认 `农业基地-大疆测绘-GeoJSON格式说明.md` 已包含 v7 §十全量配置

**Quality Gate：**
- [x] bigscreen.md 覆盖四基地地图切换规范
- [x] geojson.md 记录 Polygon 限制和 GCJ-02 要求

---

## Phase 3：变更 Delta Spec

- [x] 3.1 编写 `changes/agri-bigscreen-v7-archive/proposal.md`（问题陈述、方案、范围、v6→v7 实际内容、claude-mem 摘要）
- [x] 3.2 编写 `changes/agri-bigscreen-v7-archive/tasks.md`（本文件）
- [x] 3.3 编写 `changes/agri-bigscreen-v7-archive/specs/bigscreen_delta.md`（v6→v7 功能变化 delta）

**Quality Gate：**
- [x] delta spec 明确标注 ADDED / MODIFIED / REMOVED
- [x] claude-mem 历史观察已整合到 proposal.md

---

## Phase 4：验证与收尾

- [ ] 4.1 确认 FineReport 部署检查清单已记录（geourl 目录、同步地理文件）
- [ ] 4.2 确认 `openspec/project.md` change 列表已更新
- [ ] 4.3 检查所有文档内部链接是否有效
- [ ] 4.4 如需 `/openspec-archive`，运行归档命令

**Quality Gate：**
- [ ] 所有 Phase 1-3 任务完成
- [ ] 无破损文件引用

---

## 部署 Checklist（FVS v7 上线前必做）

- [x] D1 `农业基地_v3_GCJ02/` 目录及四基地文件已存在于 FineReport 服务器（已完成）
- [ ] D2 FineReport 管理后台「地图配置」→「同步地理文件」
- [ ] D3 在大屏中验证四基地切换、片区高亮、tooltip 显示正常
- [ ] D4 验证 `panTo` 坐标顺序（[纬度, 经度]）定位准确

---

## 完成检查清单

- [x] Phase 1 完成
- [x] Phase 2 完成
- [x] Phase 3 完成（delta spec 见 specs/ 子目录）
- [ ] Phase 4 完成
- [ ] 部署 Checklist 执行完毕
- [ ] 准备运行 `/openspec-archive`
