#!/usr/bin/env bash
# v7.1：仅重庆酉阳 — 写出 农业基地_GCJ02_YY-area.json / -point.json（不改动 CS/WS/BS）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export FR_TOOLS_REPO="$ROOT"
export GEOJSON_VERSION=农业基地_v7.1_GCJ02_MultiPolygon
export GEOJSON_BASES=重庆酉阳
export GEOJSON_SKIP_DB=1
export GEOJSON_SKIP_DB_UPDATE=1
export GEOJSON_PROTECT_EXISTING=0
export MYSQL_PASSWORD="${MYSQL_PASSWORD:-test}"

python3 scripts/versions/农业基地_v7.1_GCJ02_MultiPolygon/geojson_generate_from_kml.py --bases 重庆酉阳
echo ""
echo "输出:"
echo "  $ROOT/data/sink/农业基地_v7.1_GCJ02_MultiPolygon/农业基地_GCJ02_YY-area.json"
echo "  $ROOT/data/sink/农业基地_v7.1_GCJ02_MultiPolygon/农业基地_GCJ02_YY-point.json"
