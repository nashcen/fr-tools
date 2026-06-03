# sink/map/农业基地-大疆测绘 — 生成 GeoJSON

目录名与 FineReport 部署路径一致：

`WEB-INF/assets/map/geographic/农业基地-大疆测绘/{版本}/`

## 生成

```bash
python3 scripts/active/geojson_generate_from_kml.py
# 默认写入本目录下 农业基地_v7.4_GCJ02_L3_SingleMap/
```

## 部署至 FineReport

将对应版本子目录同步到 FR `WEB-INF`（封板目录勿覆盖已有文件，见 `GEOJSON_PROTECT_EXISTING`）。
