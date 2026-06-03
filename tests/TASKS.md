# 测试任务清单（TDD / 验收）

**关联：** `TEST_PLAN.md` v2.0 · Change `agri-data-source-sink`

## Phase A — 规范（SDD）

- [x] A1 编写 `openspec/changes/agri-data-source-sink/proposal.md`
- [x] A2 编写 `specs/data-layout_delta.md`
- [x] A3 更新 `openspec/specs/geojson.md` v5、`scripts.md` v1.3

## Phase B — 红（测试先行）

- [x] B1 新增 `tests/test_data_layout.py`（TC-DATA-01..04）
- [x] B2 调整 `test_settings` / `test_kml_parser` 路径断言

## Phase C — 绿（实现）

- [x] C1 迁移 `data/source`、`data/sink/map/`
- [x] C2 重构 `lib/settings.py`（`data_source_dir`、`data_sink_map_root`）
- [x] C3 新增 `scripts/ops/sync_sink_map_to_finereport.sh`

## Phase D — 回归与报告

- [x] D1 `pytest tests/ -v` 全绿（48 passed；写入 sink 五版本目录）
- [x] D2 `build_all_golden_manifests.py` 生成五版本 golden
- [x] D3 `test_all_versions.py` 参数化 manifest 回归
- [x] D4 填写 `TEST_REPORT.md`
- [x] D5 手工：sync FR + FVS 五版本抽检（2026-06-03，含酉阳）

## Phase E — 验收签字

| 角色 | 项 | 状态 |
|------|-----|------|
| 开发 | 代码 + 自动化 | 完成 |
| 测试 | TEST_REPORT | 完成 |
| 产品 | FVS TC-FVS-*（v7.0–v7.4 + 酉阳） | 完成（2026-06-03）|
