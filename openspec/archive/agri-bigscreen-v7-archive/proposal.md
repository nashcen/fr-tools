# 提案：农业大屏 v6→v7 升级工作归档

**Change ID：** `agri-bigscreen-v7-archive`  
**创建日期：** 2026-06-03  
**状态：** Draft → 归档中

---

## 问题陈述

在 2026-06-02 至 2026-06-03 两天内，农业大屏完成了从 v6 到 v7 的重要升级，包含 GeoJSON 目录结构重组和 FVS 文件更新。这些工作缺乏统一的规范文档归档，导致：

- 变更内容分散在多个 markdown 文件中，缺乏结构化索引
- 没有正式的规范文档描述大屏功能约束和数据格式要求
- 后续维护人员难以快速了解当前状态和历史决策背景

## 提案方案

按 OpenSpec 规范，将本次 v6→v7 所有工作成果系统性归档：

1. 建立 `openspec/` 目录结构（`project.md` + `specs/` + `changes/`）
2. 提取核心约束到基础规范文档（`bigscreen.md`、`geojson.md`）
3. 将本次迭代变更记录为独立 change（delta specs）
4. 补充 claude-mem 历史观察到文档中（工具调试、数据库连接等背景）

**无需修改代码或数据库**，纯文档整理。

---

## 范围

### In Scope
- 建立 `openspec/` 目录结构和 `project.md`
- 提取 `specs/bigscreen.md`（大屏功能规范）
- 提取 `specs/geojson.md`（GeoJSON 数据格式规范）
- 记录本次变更 delta spec（`bigscreen_delta.md`）
- 补充 claude-mem 历史观察摘要到 tasks.md
- 更新 `大屏分析报告.md` 的 v7 章节（已完成）

### Out of Scope
- 代码修改（脚本、FVS 等）
- 数据库变更
- 酉阳 KML 补充（单独 change）
- `农业基地_v3_GCJ02/` 目录脚本化部署（单独 change）

---

## 影响分析

| 组件 | 是否变更 | 说明 |
|------|----------|------|
| FVS 文件 | 否 | v7 已由人工完成 |
| 数据库 | 否 | 无变更 |
| GeoJSON | 否 | 已整理，仅记录目录结构 |
| 文档 | ✅ 是 | 新增 openspec/ 结构，更新 md 文件 |

---

## 背景：v6→v7 实际完成内容（2026-06-02 至 2026-06-03）

### 2026-06-02 工作（v6 升级）

| 工作项 | 详情 |
|--------|------|
| GeoJSON 生成 | 修复 `should_keep()` Bug（育苗中心被误丢弃）+ `buffer(0)` 修复自相交几何 |
| GeoJSON 覆盖 | 常山 24 片区、武胜 37 片区、百色 2 片区全量覆盖；酉阳 0/15（KML 缺失）|
| FVS v6 更新 | 新增武胜/百色/酉阳三基地地图组件（`区域地图_WS/BS/YY`）|
| 地图切换 JS | 16 个切换按钮补充 `setVisible + panTo` 逻辑 |
| DB 更新 | `ods_ag_base_v2` 新增基地/区域/片区编码字段；63 个片区坐标批量更新为 GCJ-02 |
| 数据导出 | 导出天气实况、空气质量、水质监测、24h/15天天气预报 CSV（验证数据联通）|

### 2026-06-03 工作（v7 完成）

| 工作项 | 详情 |
|--------|------|
| GeoJSON 目录重组 | 从 `world/中国/` 迁移至 `world/农业基地-大疆测绘/`；建立 `农业基地_v3_GCJ02/` 子目录 |
| FVS v7 制作 | 组件名统一（`区域地图_CS` 等）；geourl 更新至新目录；UI Green 优化 |
| 文档更新 | `大屏分析报告.md` 增加 v7 章节；新建 `农业基地-大疆测绘-GeoJSON格式说明.md` |
| OpenSpec 建档 | 本次任务 |

---

## claude-mem 历史观察摘要

当前项目共 **33 条 observations**，覆盖 Jun 2–3 全部开发会话。

### 自动采集（#1–#18）：工具调试与数据验证（Jun 3 上午）

会话 `4ced36ea`（claude-mem 配置）+ `b3c34c88`（数据验证）

| ID | 类型 | 会话 | 内容摘要 |
|----|------|------|----------|
| 1 | discovery | 4ced36ea | claude-mem worker 重启后代理环境变量丢失（HTTPS_PROXY 未继承）|
| 2 | discovery | b3c34c88 | 成功连接 yxg_bigscreen DB，确认 AQI 数据可访问 |
| 3 | discovery | 4ced36ea | Gemini 模型返回空响应（gemini-2.5-flash 在 claude-mem 中异常）|
| 4 | discovery | b3c34c88 | 查询 `ods_ag_alicityweather_condition`，天气数据最新时间 2026-06-02 23:55 |
| 5 | discovery | 4ced36ea | 确认 claude-mem 数据库持久化正常（3 条记录存储成功）|
| 6 | change | b3c34c88 | 创建 `6.开发实现/数据导出/` 目录 |
| 7 | feature | b3c34c88 | 导出天气实况 CSV（`01_天气实况_20260602.csv`）|
| 8 | feature | b3c34c88 | 导出空气质量 CSV（`02_空气质量_20260602.csv`）|
| 9 | feature | b3c34c88 | 导出水质监测 CSV（`03_水质监测_近一周_20260527-20260602.csv`）|
| 10 | feature | b3c34c88 | 导出 24h 天气预报 CSV（`04_24h天气预报_近3日_20260602-20260604.csv`）|
| 11 | change | b3c34c88 | 用户请求连接 yxg_bigscreen 数据库 |
| 12 | feature | 4ced36ea | 请求自动化会话窗口监控任务 |
| 13 | feature | 4ced36ea | 创建会话窗口监控自动化任务 |
| 14 | change | 4ced36ea | claude-mem worker 重启，PID 40763，端口 37702 |
| 15 | discovery | 4ced36ea | 发现项目 Claude transcript 文件（7 个 JSONL，最大 8MB）|
| 16 | discovery | 4ced36ea | transcript-watch 状态文件不存在（首次启动前正常）|
| 17 | discovery | 4ced36ea | claude-mem 数据库统计：16 观察、20 会话、237 用户提示 |
| 18 | discovery | 4ced36ea | 通过 ToolSearch 找到 `observation_add` 工具 |

---

### 自动采集（#19–#23）：其他开发会话片段

| ID | 类型 | 会话 | 内容摘要 |
|----|------|------|----------|
| 19 | discovery | 31db3a46 | 找到水电费统计表（工业大屏数据导入相关）|
| 20 | discovery | affdd20b | 理解大屏页面与交互逻辑，重点分析地图切换与边界处理 |
| 21 | discovery | 5f0ac8e0 | 更新农业大屏多边形中心点坐标 |
| 22 | discovery | da8543b6 | FVS 文件修改失败（修改中心点后未生效，为帆软设计器缓存问题）|
| 23 | discovery | b3c34c88 | 连接 yxg_bigscreen 并导出数据集 |

---

### 手动补充（#24–#33）：核心开发会话归档（2026-06-03 补录）

三个关键会话（683734a5 / 35f462e0 / dc899928）原未被 claude-mem 采集，本次手动写入。

#### 会话 `683734a5`（Jun 2 18:47，7.7MB，231 prompts）— v6 FVS 解析 + DB 重设计 + GeoJSON 生成

| ID | 类型 | 内容摘要 |
|----|------|----------|
| 24 | discovery | v6 FVS 深度解析：243 组件，GeoJSON 仅覆盖常山 6/24 片区（匹配率 7.4%），分析保存至大屏分析报告.md |
| 25 | feature | ods_ag_base_v2 重新设计：新增区域名称(旧)、基地/区域/片区三级编码，按空间局部性重排片区编号，78 条记录入库 |
| 26 | feature | GeoJSON 全量生成脚本：解析 7 个 KML，颜色过滤测绘/种植面积，WGS84→GCJ02，MultiPolygon 拆 Polygon，生成四基地文件 |
| 27 | bugfix | 坐标系修复：大疆测绘 CGCS2000≈WGS84，帆软卫星底图为高德 GCJ-02，不转换偏移约 500m |

#### 会话 `35f462e0`（Jun 2 21:25，4.5MB，138 prompts）— GeoJSON 格式调试 + 坐标更新

| ID | 类型 | 内容摘要 |
|----|------|----------|
| 28 | bugfix | **FineReport GeoJSON 不显示根因**：FeatureCollection 缺顶层 `name` 字段，地图配置可见但大屏无渲染 |
| 29 | change | ods_ag_base_v2 片区坐标批量更新：63 个片区更新为 GCJ-02 多边形重心，育苗中心从 KML 单独提取 |

#### 会话 `dc899928`（Jun 3 11:25，4.6MB，208 prompts）— 多基地地图切换 + 高亮 + skill 提炼

| ID | 类型 | 内容摘要 |
|----|------|----------|
| 30 | bugfix | 多基地切换根因：WS/BS/YY chart 存在于 FVS 包但未注册为 Widget；非 UUID 文件名导致帆软保存失败 |
| 31 | feature | 四基地切换 JS：16 个按钮全量配置 setVisible + panTo，setTimeout 延迟初始化 |
| 32 | feature | 片区高亮：`getChart().charts[0].dispatchAction` 触发 ECharts select/unselect，白色边框样式 |
| 33 | feature | fr-bigscreen skill 提炼：FVS 结构、UUID 命名规则、GeoJSON 格式、panTo 参数顺序等核心知识点 |

---

## 成功标准

- [x] `openspec/` 目录结构建立
- [x] `project.md` 记录项目约定
- [x] `specs/bigscreen.md` 提取核心规范
- [x] `specs/geojson.md` 记录 GeoJSON 格式规范
- [x] `changes/agri-bigscreen-v7-archive/` 记录本次变更
- [x] `大屏分析报告.md` 更新 v7 章节
- [x] claude-mem 三个未归档会话（683734a5 / 35f462e0 / dc899928）手动补录 10 条 observations
- [x] proposal.md claude-mem 摘要更新至全量 33 条

---

## 风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| 文档与实际 FVS 状态不一致 | 低 | 中 | 文档来源于当天解析的 FVS，与实际文件同步 |
| 酉阳 KML 缺失导致地图空白持续 | 高 | 中 | 已记录为 P1 待办，不影响其他三基地 |
| FineReport 地图同步未执行 | 中 | 高 | tasks.md 中作为 deployment checklist 强制步骤 |

---

## 归档信息

**归档时间：** 2026-06-03  
**创建日期：** 2026-06-03  
**历时：** 1 天  
**结果：** 文档归档完成

### 修改的文件
- `openspec/project.md` — 新建，项目约定与版本历史
- `openspec/specs/bigscreen.md` — 新建，大屏功能规范（含变更历史）
- `openspec/specs/geojson.md` — 新建，GeoJSON 数据格式规范（含变更历史）
- `大屏分析报告.md` — 新增 §三-C v7 更新记录，更新文件索引
- `~/.claude-mem/claude-mem.db` — 手动补录 10 条 observations（#24–#33）

### 更新的规范
- `openspec/specs/bigscreen.md` — 应用 ADDED（三基地地图组件）+ MODIFIED（命名/目录/坐标）
- `openspec/specs/geojson.md` — 应用 ADDED（全量文件）+ MODIFIED（部署目录）

### claude-mem 摘要
- 归档前共 33 条 observations，其中 10 条（#24–#33）为本次手动补录
- 覆盖三个核心开发会话：683734a5 / 35f462e0 / dc899928
