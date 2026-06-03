# Delta：数据目录布局

## 新增约定

| 路径 | 用途 |
|------|------|
| `data/source/1.农业基地KML/` | DJI 测绘 KML（只读源）|
| `data/source/农业资产盘点明细.xlsx` | 地块层级对账 |
| `data/source/2.农业基地JSON/` | 本地归档 GeoJSON（可选，非生成入口）|
| `data/sink/map/农业基地-大疆测绘/{版本}/` | 脚本生成 GCJ-02 GeoJSON |
| `data/sink/map/农业基地-大疆测绘/农业基地_v2_WGS84/` | v2 对账 sidecar |

## 环境变量（`.env`）

| 变量 | 默认 |
|------|------|
| `DATA_SOURCE_DIR` | `{repo}/data/source` |
| `DATA_SINK_MAP_ROOT` | `{repo}/data/sink/map/农业基地-大疆测绘` |
| `GEOJSON_VERSION` | 版本子目录名 |

`GEOJSON_OUTPUT_DIR` 仍可覆盖单次输出路径（测试 / 临时）。

## 废弃

- `data/1.农业基地KML/`（根级）→ 迁至 `data/source/`
- 生成默认写 `FINEREPORT_WEBINF` → 改为 `data/sink`；部署 FR 为独立步骤
