#!/bin/bash
# split-chapters.sh <source.txt> <chapters.tsv>
#
# Cuts a prepared source.txt into one file per confirmed chapter, using the
# page ranges the agent wrote to chapters.tsv after the inspectional pass.
# Idempotent: re-running overwrites the chapter files.
set -euo pipefail

usage() {
  echo "Usage: split-chapters.sh <source.txt> <chapters.tsv>" >&2
  exit 1
}

[ $# -eq 2 ] || usage
source_txt="$1"
tsv="$2"

[ -f "$source_txt" ] || { echo "Source file not found: $source_txt" >&2; exit 1; }
[ -f "$tsv" ] || { echo "Chapters file not found: $tsv" >&2; exit 1; }

workspace="$(cd "$(dirname "$source_txt")" && pwd)"
chapters_dir="$workspace/chapters"
mkdir -p "$chapters_dir"

max_page=$(grep -Ec '^\[\[page [0-9]+\]\]$' "$source_txt")
if [ "$max_page" -eq 0 ]; then
  echo "No page markers found in $source_txt" >&2
  exit 1
fi

slugify() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'
}

tmp_rows="$(mktemp)"
cleanup() { rm -f "$tmp_rows" 2>/dev/null; return 0; }
trap cleanup EXIT

# Strip comment (#...) and blank lines.
grep -Ev '^[[:space:]]*(#.*)?$' "$tsv" > "$tmp_rows" || true

if [ ! -s "$tmp_rows" ]; then
  echo "No chapter rows found in $tsv" >&2
  exit 1
fi

# --- Overlap check: warning only, does not stop the split (front/back matter
# gaps and non-chapter rows are expected to leave holes). ---
sort -t "$(printf '\t')" -k2,2n "$tmp_rows" | awk -F'\t' '
{
  from = $2 + 0; to = $3 + 0
  if (NR > 1 && from <= prev_to) {
    print "warning: " $1 " (p." from "-" to ") overlaps previous range ending p." prev_to > "/dev/stderr"
  }
  prev_to = to
}
'

json_entries=""
first=true

while IFS="$(printf '\t')" read -r id from to title; do
  [ -n "$id" ] || continue

  case "$from" in (*[!0-9]*|'') echo "Invalid 'from' for $id: $from" >&2; exit 1 ;; esac
  case "$to" in (*[!0-9]*|'') echo "Invalid 'to' for $id: $to" >&2; exit 1 ;; esac
  if [ "$from" -lt 1 ] || [ "$to" -lt "$from" ] || [ "$to" -gt "$max_page" ]; then
    echo "Invalid range for $id: $from-$to (valid: 1-$max_page)" >&2
    exit 1
  fi

  slug="$(slugify "$title")"
  [ -n "$slug" ] || slug="untitled"
  out_file="$chapters_dir/${id}-${slug}.txt"

  awk -v from="$from" -v to="$to" '
    /^\[\[page [0-9]+\]\]$/ {
      p = $0; gsub(/[^0-9]/, "", p); page = p + 0
      printing = (page >= from && page <= to)
      if (printing) print
      next
    }
    { if (printing) print }
  ' "$source_txt" > "$out_file"

  pages=$((to - from + 1))
  words=$(grep -Ev '^\[\[page [0-9]+\]\]$' "$out_file" | wc -w | tr -d ' ')

  entry="{\"id\": \"$id\", \"file\": \"$out_file\", \"from\": $from, \"to\": $to, \"pages\": $pages, \"words\": $words}"
  if [ "$first" = true ]; then
    json_entries="$entry"
    first=false
  else
    json_entries="$json_entries, $entry"
  fi
  echo "Wrote $out_file (p.$from-$to, $words words)" >&2
done < "$tmp_rows"

printf '{"chapters": [%s]}\n' "$json_entries"
