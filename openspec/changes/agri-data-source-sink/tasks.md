# 任务：data/source + data/sink

## Phase 0：规范（SDD）

- [x] 提案 `proposal.md`
- [x] Delta `specs/data-layout_delta.md`
- [x] 合并更新 `openspec/specs/geojson.md`、`scripts.md`

## Phase 1：目录迁移

- [x] 创建 `data/source/`、`data/sink/map/农业基地-大疆测绘/`
- [x] 迁移 KML、Excel、归档 JSON 至 `source/`

## Phase 2：代码（TDD）

- [x] 更新 `lib/settings.py` 默认路径
- [x] 测试先红后绿：`test_settings`、`test_data_layout`
- [x] 更新文档、`.env.example`、TEST_PLAN、cases、TASKS、REPORT

## Phase 3：验收

- [x] `pytest` 全绿（27）
- [x] 生成 v7.4 至 `data/sink/...` 与 golden 一致
- [x] 填写 `tests/TEST_REPORT.md`
