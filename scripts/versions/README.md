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
  农业基地_v7.3_GCJ02_L3/              # 封板（生产 L3）
```

发版流程：从 `active/` 复制到对应 `农业基地_*` 目录 → 更新 `openspec/release-notes-scripts.md` → 封板后不再改快照。
