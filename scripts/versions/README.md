# scripts/versions — 版本快照

**仓库：** `fr-tools`（`scripts/` 在仓库根目录）。  
目录名 **必须与** FineReport 部署目录一致：

```
versions/
  _shared/                              # 跨版本工具
  _archive/                             # 已废弃
  农业基地_v7.0_GCJ02_Polygon/
  农业基地_v7.1_GCJ02_MultiPolygon/     # 封板
  农业基地_v7.2_GCJ02_MP_L2/            # 封板（生产 L2）
  农业基地_v7.3_GCJ02_L3/              # 封板（生产 L3 四图）
  农业基地_v7.4_GCJ02_L3_SingleMap/    # 单图试验
```

发版流程：从 `active/` 复制到对应 `农业基地_*` 目录 → 更新 `openspec/release-notes-scripts.md` → 封板后不再改快照。

**生成入口（v7.0–v7.4）：** 各目录下 `geojson_generate_from_kml.py` 为薄封装，逻辑在 `scripts/lib/geojson/`（`profiles.py` 按版本开关输出形态）。

| 版本目录 | 输出形态 | golden 文件数 |
|----------|----------|---------------|
| `农业基地_v7.0_GCJ02_Polygon` | 4× `农业基地_GCJ02_{CS,WS,BS,YY}.json` | 4 |
| `农业基地_v7.1_GCJ02_MultiPolygon` | 8× `*-area.json` / `*-point.json` | 8 |
| `农业基地_v7.2_GCJ02_MP_L2` | L3 树 + legacy 合并 | 140 |
| `农业基地_v7.3_GCJ02_L3` | 同 v7.2 | 140 |
| `农业基地_v7.4_GCJ02_L3_SingleMap` | L3 树，无 legacy | 136 |

**测试：** `MYSQL_PASSWORD=x pytest tests/ -v`；重建 golden：`python3 tests/tools/build_all_golden_manifests.py`。

v7.1 另有 `geojson_fix_area_point_split.py`（从已有合并 json 拆分，运维补救；新生成请用 `geojson_generate_from_kml.py`）。
