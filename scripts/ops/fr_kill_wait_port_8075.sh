#!/usr/bin/env bash
# 清理浏览器/FineReport 预览遗留的 localhost:8075 CLOSE_WAIT 连接
# 用法:
#   ./kill_close_wait_8075.sh          # 仅检查，不杀进程
#   ./kill_close_wait_8075.sh --kill   # 检查并结束相关进程
#   ./kill_close_wait_8075.sh --kill --yes  # 不交互确认，直接结束

set -euo pipefail

PORT="${PORT:-8075}"
MODE="check"
ASSUME_YES=false

for arg in "$@"; do
  case "$arg" in
    --kill) MODE="kill" ;;
    --yes|-y) ASSUME_YES=true ;;
    -h|--help)
      sed -n '2,8p' "$0"
      exit 0
      ;;
    *)
      echo "未知参数: $arg（支持 --kill --yes）" >&2
      exit 1
      ;;
  esac
done

if ! command -v lsof >/dev/null 2>&1; then
  echo "错误: 需要 lsof 命令" >&2
  exit 1
fi

TMP_PIDS=$(mktemp)
trap 'rm -f "$TMP_PIDS"' EXIT

# 收集 CLOSE_WAIT 的 PID（去重）
lsof -nP -iTCP:"$PORT" -sTCP:CLOSE_WAIT 2>/dev/null | awk 'NR>1 {print $2}' | sort -u > "$TMP_PIDS" || true

if [[ ! -s "$TMP_PIDS" ]]; then
  echo "✓ 端口 $PORT 无 CLOSE_WAIT 连接"
  if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null | grep -q LISTEN; then
    echo "  注意: 仍有进程在监听 $PORT（可能是 FineReport 设计器内嵌服务）:"
    lsof -nP -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null | tail -n +2
  else
    echo "  端口 $PORT 无 LISTEN（设计器内嵌服务未运行）"
  fi
  exit 0
fi

echo "发现 localhost:$PORT 的 CLOSE_WAIT 连接:"
printf "%-8s %-24s %s\n" "PID" "进程名" "CLOSE_WAIT数"
while read -r pid; do
  [[ -z "$pid" ]] && continue
  cnt=$(lsof -nP -iTCP:"$PORT" -sTCP:CLOSE_WAIT 2>/dev/null | awk -v p="$pid" '$2==p {c++} END {print c+0}')
  cmd=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
  printf "%-8s %-24s %s\n" "$pid" "$cmd" "$cnt"
done < "$TMP_PIDS"
echo ""

echo "进程详情:"
while read -r pid; do
  [[ -z "$pid" ]] && continue
  ps -p "$pid" -o pid=,ppid=,user=,etime=,command= 2>/dev/null || echo "  PID $pid 已不存在"
done < "$TMP_PIDS"
echo ""

if [[ "$MODE" != "kill" ]]; then
  echo "仅检查模式。若要结束上述进程，请执行:"
  echo "  $0 --kill"
  echo "  $0 --kill --yes   # 跳过确认"
  exit 0
fi

PIDS=$(tr '\n' ' ' < "$TMP_PIDS" | sed 's/ $//')
if [[ "$ASSUME_YES" != true ]]; then
  echo "将向以下 PID 发送 SIGTERM: $PIDS"
  read -r -p "确认结束? [y/N] " ans
  if [[ ! "$ans" =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
  fi
fi

while read -r pid; do
  [[ -z "$pid" ]] && continue
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "跳过 PID $pid（已不存在）"
    continue
  fi
  cmd=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
  echo "SIGTERM -> PID $pid ($cmd)"
  kill -TERM "$pid" 2>/dev/null || true
done < "$TMP_PIDS"

for _ in 1 2 3 4 5; do
  alive=0
  while read -r pid; do
    [[ -z "$pid" ]] && continue
    kill -0 "$pid" 2>/dev/null && alive=1
  done < "$TMP_PIDS"
  [[ $alive -eq 0 ]] && break
  sleep 1
done

while read -r pid; do
  [[ -z "$pid" ]] && continue
  if kill -0 "$pid" 2>/dev/null; then
    echo "SIGKILL -> PID $pid"
    kill -KILL "$pid" 2>/dev/null || true
  fi
done < "$TMP_PIDS"

echo ""
echo "清理后复查:"
if lsof -nP -iTCP:"$PORT" -sTCP:CLOSE_WAIT 2>/dev/null | grep -q CLOSE_WAIT; then
  echo "⚠ 仍有 CLOSE_WAIT:"
  lsof -nP -iTCP:"$PORT" -sTCP:CLOSE_WAIT 2>/dev/null
  exit 1
else
  echo "✓ 端口 $PORT 已无 CLOSE_WAIT"
fi
