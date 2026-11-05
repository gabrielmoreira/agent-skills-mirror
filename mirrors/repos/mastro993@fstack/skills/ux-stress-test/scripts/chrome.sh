#!/usr/bin/env bash
# Starts or stops one persona's private headless Chrome for browser-use. Each session gets its own
# Chrome process and a fresh profile, so parallel personas never share cookies, logins or tabs.
# Usage: chrome.sh start <session> <output-dir>   prints the env prefix for every browser-use call
#        chrome.sh stop  <session> <output-dir>
set -euo pipefail
cmd=$1 session=$2 profile=$3/.chrome-$2

case $cmd in
start)
  chrome=${CHROME:-}
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" google-chrome google-chrome-stable chromium; do
    [ -n "$chrome" ] && break
    if [ -x "$c" ] || command -v "$c" >/dev/null; then chrome=$c; fi
  done
  [ -n "$chrome" ] || { echo "Chrome not found; set CHROME=<path to Chrome or Chromium>" >&2; exit 1; }
  rm -rf "$profile"
  mkdir -p "$profile"
  # Port 0 lets Chrome pick a free port and write it to DevToolsActivePort.
  "$chrome" --headless=new --remote-debugging-port=0 --user-data-dir="$profile" \
    --no-first-run --no-default-browser-check about:blank >"$profile/chrome.log" 2>&1 &
  echo $! >"$profile/pid"
  for _ in $(seq 50); do [ -s "$profile/DevToolsActivePort" ] && break; sleep 0.2; done
  [ -s "$profile/DevToolsActivePort" ] || { echo "Chrome did not start; see $profile/chrome.log" >&2; exit 1; }
  prefix="BU_NAME=$session BU_CDP_URL=http://127.0.0.1:$(head -1 "$profile/DevToolsActivePort") BH_TAB_MARKER=0"
  # A background tab counts as hidden: no paint timing, throttled timers. Make the first tab visible.
  env $prefix browser-use <<<'cdp("Page.bringToFront")' >/dev/null
  echo "$prefix"
  ;;
stop)
  BU_NAME=$session browser-use --reload >/dev/null 2>&1 || true
  kill "$(cat "$profile/pid" 2>/dev/null)" 2>/dev/null || true
  ;;
*)
  echo "usage: chrome.sh start|stop <session> <output-dir>" >&2
  exit 2
  ;;
esac
