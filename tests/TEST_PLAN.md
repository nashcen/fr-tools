# 测试计划：农业基地 GeoJSON 生成（source/sink 布局）

| 项 | 值 |
|----|-----|
| 文档版本 | 2.0 |
| 日期 | 2026-06-03 |
| 变更 | `data/source` + `data/sink/map`；生成与 FR 部署分离 |
| 规范 | `openspec/changes/agri-data-source-sink/`、`openspec/specs/geojson.md` v5 |

---

## 1. 测试目标

1. **源数据**仅存在于 `data/source/`，生成产物写入 `data/sink/map/农业基地-大疆测绘/{版本}/`。
2. 生成结果与 golden manifest 一致（结构回归）。
3. 版本 profile、封板保护、配置外置行为不变。
4. SDD 规范与代码一致；TDD 用例可重复执行。

---

## 2. 数据布局（被测）

```
data/source/1.农业基地KML/
data/source/农业资产盘点明细.xlsx
data/sink/map/农业基地-大疆测绘/
  农业基地_v7.4_GCJ02_L3_SingleMap/   ← 默认 GEOJSON_VERSION
  农业基地_v2_WGS84/                  ← sidecar
```

部署：`scripts/ops/sync_sink_map_to_finereport.sh {版本}` → `WEB-INF/...`

---

## 3. 测试策略

| 层级 | 内容 |
|------|------|
| 布局 | 目录存在、`settings` 默认路径 |
| 单元 | 坐标、KML、匹配、profile |
| 集成 | 离线生成 → tmp 或 sink |
| 回归 | golden manifest（v7.4）|
| 手工 | FR 同步 + FVS |

**CI 准入：** `data/source` 齐全；`pytest` 使用 `GEOJSON_OUTPUT_DIR=<tmp>`，不写 sink 封板目录。

---

## 4. 用例索引

完整表见 `tests/cases/geojson_test_cases.yaml`；新增 **TC-DATA-*** 见下表。

| ID | 名称 | 自动化 |
|----|------|--------|
| TC-DATA-01 | source 下 KML 存在 | `test_data_layout.py` |
| TC-DATA-02 | source 下 Excel 存在 | `test_data_layout.py` |
| TC-DATA-03 | sink map 根存在 | `test_data_layout.py` |
| TC-DATA-04 | 默认输出 = sink/{版本} | `test_data_layout.py` |
| TC-CFG-03 | KML/Excel 指向 source | `test_settings.py` |
| TC-GEO-01..08 | 结构回归 | `test_geojson_*.py` |
| TC-VER-01..04 | 版本差异 | `test_version_profiles.py` |
| TC-FVS-* | 部署后大屏 | 手工 |

---

## 5. 执行

```bash
pip install -r requirements-dev.txt
MYSQL_PASSWORD=test pytest tests/ -v

# 写入 sink（离线）
GEOJSON_SKIP_DB=1 GEOJSON_PROTECT_EXISTING=0 MYSQL_PASSWORD=x \
  python3 scripts/active/geojson_generate_from_kml.py

# 更新 golden（从 sink 只读）
python3 tests/tools/build_geojson_manifest.py \
  --source data/sink/map/农业基地-大疆测绘/农业基地_v7.4_GCJ02_L3_SingleMap \
  --version 农业基地_v7.4_GCJ02_L3_SingleMap
```

---

## 6. 准出

- [ ] `pytest` 全绿（见 `tests/TEST_REPORT.md`）
- [ ] v7.4 生成至 sink 与 golden 一致
- [ ] 文档 / `.env.example` / openspec 已更新

---

## 7. 变更历史

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-06-03 | 1.0 | 初版 |
| 2026-06-03 | 2.0 | source/sink 布局 |
