# data/sink — 生成 GeoJSON

脚本与 `pytest` 在 **`data/sink/` 根下直接** 写出五个版本目录（无 `map/农业基地-大疆测绘` 中间层）：

| 目录 |
|------|
| `农业基地_v7.0_GCJ02_Polygon/` |
| `农业基地_v7.1_GCJ02_MultiPolygon/` |
| `农业基地_v7.2_GCJ02_MP_L2/` |
| `农业基地_v7.3_GCJ02_L3/` |
| `农业基地_v7.4_GCJ02_L3_SingleMap/` |

```bash
# 五版本一次生成（推荐）
./scripts/ops/generate_all_sink_versions.sh

# 或跑测试（同样会写满 data/sink/）
MYSQL_PASSWORD=test pytest tests/ -v

# 仅当前默认版本 v7.4
python3 scripts/active/geojson_generate_from_kml.py
```

本目录 **GeoJSON 纳入 Git**，可推送到远程做版本管理；重新生成后 `git add data/sink` 再提交。

部署至 FineReport 时，同步到  
`WEB-INF/assets/map/geographic/农业基地-大疆测绘/{版本}/`（见 `scripts/ops/sync_sink_map_to_finereport.sh`）。

v2 对账 sidecar 写在 `data/source/农业基地_v2_WGS84/`，不在 sink 下。
