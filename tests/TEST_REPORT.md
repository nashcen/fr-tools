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
| **通过** | 51 项 pytest 全部通过；会话级写入 sink 五版本目录 |
| **通过** | v7.0–v7.4 离线生成与 golden manifest 一致；酉阳 7 片区（v7.0/v7.1 专项断言）|
| **通过** | FR 五版本手工验收（TC-DEP-01、TC-FVS-*）：重庆酉阳地图展示正常（2026-06-03，产品确认）|

---

## 2. 环境

| 项 | 值 |
|----|-----|
| Python | 3.14.3 |
| pytest | 9.0.3 |
| 数据布局 | `data/source` + `data/sink/{五版本}/` |
| CI 模式 | 会话 fixture 写入 `data/sink/{v7.0–v7.4}/`，`GEOJSON_SKIP_DB=1` |

---

## 3. 自动化结果

```text
pytest tests/ -v
============================== 51 passed in ~16s ==============================
```

| 套件 | 用例数 | 结果 |
|------|--------|------|
| test_all_versions | 22 | PASS |
| test_data_layout | 4 | PASS |
| test_settings | 4 | PASS |
| test_coord_convert | 2 | PASS |
| test_kml_parser | 3 | PASS |
| test_plot_matching | 3 | PASS |
| test_version_profiles | 6 | PASS |
| test_geojson_generate | 2 | PASS |
| test_geojson_conventions | 5 | PASS |

---

## 4. 集成验收（sink）

| 步骤 | 命令 | 结果 |
|------|------|------|
| golden 重建 | `python3 tests/tools/build_all_golden_manifests.py` | v7.0–v7.4 五份 manifest |
| 参数化回归 | `test_all_versions.py` | 5 版本 × 清单 + 结构断言 |
| v7.4 sink（可选） | `scripts/active/geojson_generate_from_kml.py` | 136 个 `.json` |

---

## 5. 用例覆盖（TC 摘要）

| 域 | 计划数 | 自动化通过 | 手工 |
|----|--------|------------|------|
| DATA | 4 | 4 | — |
| CFG | 4 | 4 | — |
| CRD | 2 | 2 | — |
| KML | 2 | 3 | — |
| MCH | 3 | 3 | — |
| VER | 10 | 10 | — |
| GEO | 8 | 8 | — |
| DEP | 1 | — | 通过（用户 sync FR）|
| FVS | 5 | — | 通过（v7.0–v7.4 酉阳展示）|

---

## 6. 缺陷与风险

| ID | 严重度 | 描述 | 状态 |
|----|--------|------|------|
| — | — | 无阻塞缺陷 | — |

| 风险 | 缓解 |
|------|------|
| sink 与 FR 漂移 | 部署前 `rsync` + `PROTECT_EXISTING=1` |
| v7.1 补救脚本 | 新生成用 `geojson_generate_from_kml.py`；`geojson_fix_area_point_split.py` 仅修已有合并 json |

---

## 7. 验收结论

- **开发 / 自动化验收：通过**（pytest 全绿、sink 与 golden 一致）。
- **发布验收：通过**（FineReport 已同步；v7.0–v7.4 大屏手工验收通过，含重庆酉阳）。

---

## 8. 签核

| 角色 | 签名 | 日期 |
|------|------|------|
| 开发 | — | 2026-06-03 |
| 测试 | 自动化报告 | 2026-06-03 |
