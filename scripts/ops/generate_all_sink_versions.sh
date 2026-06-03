#!/usr/bin/env bash
# 离线生成 v7.0–v7.4 至 data/sink/{版本}/（与 pytest 会话 fixture 一致）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export FR_TOOLS_REPO="$ROOT"
export GEOJSON_SKIP_DB=1
export GEOJSON_SKIP_DB_UPDATE=1
export GEOJSON_PROTECT_EXISTING=0
export MYSQL_PASSWORD="${MYSQL_PASSWORD:-test}"

VERSIONS=(
  农业基地_v7.0_GCJ02_Polygon
  农业基地_v7.1_GCJ02_MultiPolygon
  农业基地_v7.2_GCJ02_MP_L2
  农业基地_v7.3_GCJ02_L3
  农业基地_v7.4_GCJ02_L3_SingleMap
)

for v in "${VERSIONS[@]}"; do
  echo "=== $v ==="
  GEOJSON_VERSION="$v" python3 scripts/versions/"$v"/geojson_generate_from_kml.py
done

echo ""
echo "Done. Output: $ROOT/data/sink/"
ls -1 "$ROOT/data/sink"
