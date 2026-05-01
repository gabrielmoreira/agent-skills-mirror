#!/usr/bin/env bash
set -euo pipefail

# watchdog-snapshot.sh — Quick status snapshot for Copilot skill usage.
# Installed to ~/.copilot/skills/mem-watchdog-ops/ by the VS Code extension.

svc=$(systemctl --user is-active mem-watchdog 2>/dev/null || echo unknown)
avail=$(awk '/^MemAvailable:/{print $2; exit}' /proc/meminfo 2>/dev/null || echo 0)
total=$(awk '/^MemTotal:/{print $2; exit}' /proc/meminfo 2>/dev/null || echo 0)
psi=$(awk '/^full[[:space:]]/{for(i=1;i<=NF;i++){if($i ~ /^avg10=/){sub("avg10=","",$i);print $i; exit}}}' /proc/pressure/memory 2>/dev/null || echo 0)
vscode_rss=$(ps -C code -o rss= 2>/dev/null | awk '{s+=$1} END{print s+0}')
chrome_rss=$(ps -eo comm,rss --no-headers 2>/dev/null | awk '$1 ~ /(chrome|chromium)/{s+=$2} END{print s+0}')

pct=0
if [[ "$total" -gt 0 ]]; then
  pct=$(( avail * 100 / total ))
fi

echo "mem-watchdog status: ${svc}"
echo "mem free: ${pct}% ($((avail / 1024)) MB / $((total / 1024)) MB)"
echo "psi full avg10: ${psi}%"
echo "vscode rss: $((vscode_rss / 1024)) MB"
echo "chrome rss: $((chrome_rss / 1024)) MB"
echo
echo "recent journal:"
journalctl --user -u mem-watchdog -n 15 --no-pager --output=short-monotonic 2>/dev/null || true
