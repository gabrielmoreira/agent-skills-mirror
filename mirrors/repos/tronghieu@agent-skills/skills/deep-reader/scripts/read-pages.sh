#!/bin/bash
# read-pages.sh <source.txt> <from> [to]
#
# Prints pages from..to (inclusive, default to=from) from a prepared
# source.txt, including the [[page N]] marker lines so the agent keeps its
# page anchors while reading a slice.
set -euo pipefail

usage() {
  echo "Usage: read-pages.sh <source.txt> <from> [to]" >&2
  exit 1
}

[ $# -ge 2 ] && [ $# -le 3 ] || usage
source_txt="$1"
from="$2"
to="${3:-$2}"

[ -f "$source_txt" ] || { echo "Source file not found: $source_txt" >&2; exit 1; }

case "$from" in (*[!0-9]*|'') echo "from must be a positive integer: $from" >&2; exit 1 ;; esac
case "$to" in (*[!0-9]*|'') echo "to must be a positive integer: $to" >&2; exit 1 ;; esac

max_page=$(grep -Ec '^\[\[page [0-9]+\]\]$' "$source_txt")
if [ "$max_page" -eq 0 ]; then
  echo "No page markers found in $source_txt" >&2
  exit 1
fi

if [ "$from" -lt 1 ] || [ "$to" -lt "$from" ] || [ "$to" -gt "$max_page" ]; then
  echo "Invalid range $from-$to; valid range is 1-$max_page" >&2
  exit 1
fi

awk -v from="$from" -v to="$to" '
/^\[\[page [0-9]+\]\]$/ {
  p = $0
  gsub(/[^0-9]/, "", p)
  page = p + 0
  printing = (page >= from && page <= to)
  if (printing) print
  next
}
{ if (printing) print }
' "$source_txt"
