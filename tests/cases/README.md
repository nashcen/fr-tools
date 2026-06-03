# 测试用例目录

- **测试计划（总览）：** [`../TEST_PLAN.md`](../TEST_PLAN.md) v2.0（source/sink）
- **测试报告：** [`../TEST_REPORT.md`](../TEST_REPORT.md)
- **测试任务：** [`../TASKS.md`](../TASKS.md)
- **机器可读用例表：** [`geojson_test_cases.yaml`](geojson_test_cases.yaml)
- **自动化实现：** `tests/test_*.py`

用例 ID 格式：`TC-{域}-{序号}`，域 = CFG / CRD / KML / MCH / VER / GEO / INT / FVS。

## 如何运行

完整说明见仓库根目录 [`README.md` § 测试](../../README.md#测试)。常用命令：

```bash
pip install -r requirements-dev.txt
MYSQL_PASSWORD=test pytest tests/ -v                              # 全部
pytest tests/test_all_versions.py -v                              # 版本 + sink
pytest tests/test_all_versions.py::test_sink_has_five_version_directories -v
pytest "tests/test_all_versions.py::test_generate_matches_golden_manifest[农业基地_v7.4_GCJ02_L3_SingleMap]" -v
pytest tests/ -k "v7.0" -v                                        # 关键字过滤
```
