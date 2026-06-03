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

- [x] D1 `pytest tests/ -v` 全绿（27 passed）
- [x] D2 离线生成 v7.4 至 sink
- [x] D3 golden manifest 与 sink 输出一致（136 文件）
- [x] D4 填写 `TEST_REPORT.md`
- [ ] D5 手工：sync FR + FVS 抽检（可选）

## Phase E — 验收签字

| 角色 | 项 | 状态 |
|------|-----|------|
| 开发 | 代码 + 自动化 | 待 D1 |
| 测试 | TEST_REPORT | 待 D4 |
| 产品 | FVS TC-FVS-* | 待手工 |
