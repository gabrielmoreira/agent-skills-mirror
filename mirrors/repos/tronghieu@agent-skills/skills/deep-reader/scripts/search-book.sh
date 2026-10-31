#!/bin/bash
# search-book.sh <source.txt> <pattern> [context-lines]
#
# Case-insensitive extended-regex search across a prepared source.txt, with
# each matching (and optional context) line reported by page number so
# results can be followed straight into read-pages.sh.
set -euo pipefail

usage() {
  echo "Usage: search-book.sh <source.txt> <pattern> [context-lines]" >&2
  exit 1
}

[ $# -ge 2 ] && [ $# -le 3 ] || usage
source_txt="$1"
pattern="$2"
context="${3:-0}"

[ -f "$source_txt" ] || { echo "Source file not found: $source_txt" >&2; exit 1; }
case "$context" in (*[!0-9]*|'') echo "context-lines must be a non-negative integer: $context" >&2; exit 1 ;; esac

tmp_matches="$(mktemp)"
cleanup() { rm -f "$tmp_matches" 2>/dev/null; return 0; }
trap cleanup EXIT

set +e
grep -nEi -- "$pattern" "$source_txt" | cut -d: -f1 > "$tmp_matches"
grep_status="${PIPESTATUS[0]}"
set -e

if [ "$grep_status" -gt 1 ]; then
  echo "search failed (invalid pattern?): $pattern" >&2
  exit 1
fi

total_matches=$(wc -l < "$tmp_matches" | tr -d ' ')

if [ "$total_matches" -eq 0 ]; then
  echo "no matches: $pattern" >&2
  exit 1
fi

truncated=false
if [ "$total_matches" -gt 200 ]; then
  truncated=true
  head -n 200 "$tmp_matches" > "$tmp_matches.head"
  mv "$tmp_matches.head" "$tmp_matches"
fi

awk -v ctxfile="$tmp_matches" -v ctx="$context" '
BEGIN {
  while ((getline ln < ctxfile) > 0) matchline[ln + 0] = 1
  close(ctxfile)
  for (m in matchline) {
    lo = m - ctx; hi = m + ctx
    for (i = lo; i <= hi; i++) if (i >= 1) wanted[i] = 1
  }
}
/^\[\[page [0-9]+\]\]$/ {
  p = $0
  gsub(/[^0-9]/, "", p)
  page = p + 0
}
{
  if (wanted[NR]) {
    prefix = (NR in matchline) ? ": " : "- "
    print "p." page prefix $0
  }
}
' "$source_txt"

if [ "$truncated" = true ]; then
  echo "more than 200 matches; showing first 200 - narrow the pattern" >&2
fi
