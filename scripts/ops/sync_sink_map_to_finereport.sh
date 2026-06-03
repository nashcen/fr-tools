#!/usr/bin/env bash
# 将 data/sink/{版本} 同步到 FineReport WEB-INF/.../农业基地-大疆测绘/{版本}
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VERSION="${1:-农业基地_v7.4_GCJ02_L3_SingleMap}"
FR_WEBINF="${FINEREPORT_WEBINF:-/Applications/FineReport/webapps/webroot/WEB-INF}"
SRC="$ROOT/data/sink/$VERSION"
DST="$FR_WEBINF/assets/map/geographic/农业基地-大疆测绘/$VERSION"
if [[ ! -d "$SRC" ]]; then
  echo "Source missing: $SRC — run geojson_generate_from_kml.py or pytest first" >&2
  exit 1
fi
mkdir -p "$(dirname "$DST")"
rsync -av "$SRC/" "$DST/"
echo "Synced $SRC -> $DST"
