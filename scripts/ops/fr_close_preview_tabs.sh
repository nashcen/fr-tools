#!/usr/bin/env bash
# 仅关闭 FineReport 本地预览相关的浏览器标签（不结束整个 Chrome）
#
# 匹配: URL 含 localhost:8075 或 127.0.0.1:8075
#
# 用法:
#   ./close_finereport_preview_tabs.sh           # 列出匹配标签
#   ./close_finereport_preview_tabs.sh --close   # 确认后关闭
#   ./close_finereport_preview_tabs.sh --close -y

set -euo pipefail

PORT="${PORT:-8075}"
DO_CLOSE=false
ASSUME_YES=false
BROWSER="${BROWSER:-Google Chrome}"

for arg in "$@"; do
  case "$arg" in
    --close) DO_CLOSE=true ;;
    --yes|-y) ASSUME_YES=true ;;
    -h|--help)
      sed -n '2,9p' "$0"
      exit 0
      ;;
    *)
      echo "未知参数: $arg" >&2
      exit 1
      ;;
  esac
done

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "此脚本仅支持 macOS" >&2
  exit 1
fi

if ! osascript -e "tell application \"System Events\" to (name of processes) contains \"$BROWSER\"" 2>/dev/null | grep -q true; then
  echo "未检测到正在运行的: $BROWSER"
  exit 0
fi

fr_list_tabs() {
  export FR_PORT="$PORT"
  osascript <<'APPLESCRIPT'
on tabMatchesPreview(u)
  if u is missing value then return false
  if u contains "localhost:" & (system attribute "FR_PORT") then return true
  if u contains "127.0.0.1:" & (system attribute "FR_PORT") then return true
  return false
end tabMatchesPreview

tell application "Google Chrome"
  if (count of windows) is 0 then
    return "0"
  end if
  set out to ""
  set nMatch to 0
  repeat with w in windows
    set winId to id of w
    repeat with t in tabs of w
      set u to URL of t
      if tabMatchesPreview(u) then
        set nMatch to nMatch + 1
        set tabIdx to index of t
        set out to out & winId & "\t" & tabIdx & "\t" & (title of t) & "\t" & u & linefeed
      end if
    end repeat
  end repeat
  return (nMatch as string) & linefeed & out
end tell
APPLESCRIPT
}

fr_close_tabs() {
  export FR_PORT="$PORT"
  osascript <<'APPLESCRIPT'
on tabMatchesPreview(u)
  if u is missing value then return false
  if u contains "localhost:" & (system attribute "FR_PORT") then return true
  if u contains "127.0.0.1:" & (system attribute "FR_PORT") then return true
  return false
end tabMatchesPreview

tell application "Google Chrome"
  set closedCount to 0
  repeat with w in windows
    set n to count of tabs of w
    repeat with i from n to 1 by -1
      set t to tab i of w
      if tabMatchesPreview(URL of t) then
        close t
        set closedCount to closedCount + 1
      end if
    end repeat
  end repeat
  return closedCount
end tell
APPLESCRIPT
}

RAW=$(fr_list_tabs)
COUNT=$(echo "$RAW" | head -n 1 | tr -d '[:space:]')
[[ -z "$COUNT" || "$COUNT" == "0" ]] && COUNT=0
LINES=$(echo "$RAW" | tail -n +2)

if [[ "$COUNT" -eq 0 ]]; then
  echo "OK: $BROWSER 中无 localhost:$PORT 预览标签"
  exit 0
fi

echo "$BROWSER 中 FineReport 预览标签 ($COUNT 个):"
echo ""
idx=0
while IFS=$'\t' read -r winId tabIdx title url; do
  [[ -z "${winId:-}" ]] && continue
  idx=$((idx + 1))
  echo "[$idx] 窗口 $winId · 标签 #$tabIdx"
  echo "    $title"
  echo "    $url"
  echo ""
done <<< "$LINES"

if [[ "$DO_CLOSE" != true ]]; then
  echo "未关闭。执行以下命令仅关这些标签:"
  echo "  $0 --close"
  echo "  $0 --close -y"
  exit 0
fi

if [[ "$ASSUME_YES" != true ]]; then
  read -r -p "确认关闭这 $COUNT 个标签? [y/N] " ans
  if [[ ! "$ans" =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
  fi
fi

CLOSED=$(fr_close_tabs)
echo "OK: 已关闭 $CLOSED 个预览标签 (其它 Chrome 标签不受影响)"
