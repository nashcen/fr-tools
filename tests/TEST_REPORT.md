# 测试报告：GeoJSON 生成（source/sink 重构）

| 项 | 值 |
|----|-----|
| 报告日期 | 2026-06-03 |
| 变更 | `agri-data-source-sink` |
| 执行人 | 自动化 + CI 本地 |
| 计划版本 | `tests/TEST_PLAN.md` v2.0 |

---

## 1. 摘要

| 结论 | 说明 |
|------|------|
| **通过** | 27 项 pytest 全部通过 |
| **通过** | v7.4 离线生成写入 `data/sink/map/.../农业基地_v7.4_GCJ02_L3_SingleMap/`，结构与 golden manifest 一致（136 文件）|
| **待办** | FR 部署与 FVS 手工项（TC-DEP-01、TC-FVS-*）|

---

## 2. 环境

| 项 | 值 |
|----|-----|
| Python | 3.14.3 |
| pytest | 9.0.3 |
| 数据布局 | `data/source` + `data/sink/map/农业基地-大疆测绘` |
| CI 模式 | `GEOJSON_OUTPUT_DIR=<tmp>`，`GEOJSON_SKIP_DB=1` |

---

## 3. 自动化结果

```text
pytest tests/ -v
============================== 27 passed in 12.55s ==============================
```

| 套件 | 用例数 | 结果 |
|------|--------|------|
| test_data_layout | 4 | PASS |
| test_settings | 4 | PASS |
| test_coord_convert | 2 | PASS |
| test_kml_parser | 3 | PASS |
| test_plot_matching | 3 | PASS |
| test_version_profiles | 4 | PASS |
| test_geojson_generate | 2 | PASS |
| test_geojson_conventions | 5 | PASS |

---

## 4. 集成验收（sink）

| 步骤 | 命令 | 结果 |
|------|------|------|
| 生成 v7.4 | `GEOJSON_SKIP_DB=1 GEOJSON_PROTECT_EXISTING=0 python3 scripts/active/...` | 成功，63 片区 |
| 输出路径 | `data/sink/map/农业基地-大疆测绘/农业基地_v7.4_GCJ02_L3_SingleMap/` | 136 个 `.json` |
| manifest 对比 | 与 `tests/golden/.../manifest.json` | **一致** |

---

## 5. 用例覆盖（TC 摘要）

| 域 | 计划数 | 自动化通过 | 手工 |
|----|--------|------------|------|
| DATA | 4 | 4 | — |
| CFG | 4 | 4 | — |
| CRD | 2 | 2 | — |
| KML | 2 | 3 | — |
| MCH | 3 | 3 | — |
| VER | 4 | 4 | — |
| GEO | 8 | 7 | — |
| DEP | 1 | — | 待执行 |
| FVS | 5 | — | 待执行 |

---

## 6. 缺陷与风险

| ID | 严重度 | 描述 | 状态 |
|----|--------|------|------|
| — | — | 无阻塞缺陷 | — |

| 风险 | 缓解 |
|------|------|
| sink 与 FR 漂移 | 部署前 `rsync` + `PROTECT_EXISTING=1` |
| golden 仅 v7.4 | v7.3 铺数后补 manifest |

---

## 7. 验收结论

- **开发 / 自动化验收：通过**（满足 SDD + TDD 准出条：pytest 全绿、sink 生成与 golden 一致）。
- **发布验收：待** FineReport 同步与大屏手工（`tests/TASKS.md` Phase E）。

---

## 8. 签核

| 角色 | 签名 | 日期 |
|------|------|------|
| 开发 | — | 2026-06-03 |
| 测试 | 自动化报告 | 2026-06-03 |
