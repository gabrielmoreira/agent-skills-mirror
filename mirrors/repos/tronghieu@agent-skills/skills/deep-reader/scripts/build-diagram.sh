#!/bin/bash
# build-diagram.sh <workspace-dir> [--append]
#
# Emits a mechanical Mermaid mindmap of the book's structure from
# chapters.tsv (skeleton only; the intelligence-work concept/argument map
# belongs in synthesis.md, hand-authored per SKILL.md). With --append, the
# block is inserted/replaced under "## Structure diagram" in map.md between
# <!-- diagram:start --> / <!-- diagram:end --> markers, so it is re-runnable.
set -euo pipefail

usage() {
  echo "Usage: build-diagram.sh <workspace-dir> [--append]" >&2
  exit 1
}

[ $# -ge 1 ] && [ $# -le 2 ] || usage
workspace="$1"
append=false
if [ $# -eq 2 ]; then
  [ "$2" = "--append" ] || usage
  append=true
fi

[ -d "$workspace" ] || { echo "Workspace directory not found: $workspace" >&2; exit 1; }
workspace="$(cd "$workspace" && pwd)"

tsv="$workspace/chapters.tsv"
if [ ! -f "$tsv" ]; then
  echo "chapters.tsv not found in $workspace" >&2
  echo "Hint: write <workspace>/chapters.tsv (id<TAB>from<TAB>to<TAB>title) after confirming the book's" \
       "structure in the inspectional pass, then rerun." >&2
  exit 1
fi

map_md="$workspace/map.md"
title=""
if [ -f "$map_md" ]; then
  title_line="$(grep -m1 -E '^# ' "$map_md" || true)"
  if [ -n "$title_line" ]; then
    title="${title_line#\# }"
  fi
fi
[ -n "$title" ] || title="$(basename "$workspace")"

tmp_rows="$(mktemp)"
tmp_awk="$(mktemp)"
tmp_map=""
cleanup() { rm -f "$tmp_rows" "$tmp_awk" "${tmp_map:-}" 2>/dev/null; return 0; }
trap cleanup EXIT

grep -Ev '^[[:space:]]*(#.*)?$' "$tsv" > "$tmp_rows" || true
if [ ! -s "$tmp_rows" ]; then
  echo "No chapter rows found in $tsv" >&2
  exit 1
fi

cat > "$tmp_awk" <<'AWK_EOF'
BEGIN { FS = "\t"; n = 0; any_part = 0 }
{
  n++
  ids[n] = $1; froms[n] = $2; tos[n] = $3
  hdg = $4
  gsub(/"/, "'", hdg)
  hdgs[n] = hdg
  is_part[n] = ($1 ~ /^[Pp][0-9]+$/) ? 1 : 0
  if (is_part[n]) any_part = 1
}
END {
  for (i = 1; i <= n; i++) {
    if (is_part[i]) {
      print "  \"" hdgs[i] "\""
    } else {
      label = ids[i] ": " hdgs[i] " (pp. " froms[i] "–" tos[i] ")"
      if (any_part) print "    \"" label "\""
      else          print "  \"" label "\""
    }
  }
}
AWK_EOF

body="$(awk -f "$tmp_awk" "$tmp_rows")"
title_escaped="${title//\"/\'}"

diagram="$(printf '```mermaid\nmindmap\n  "%s"\n%s\n```' "$title_escaped" "$body")"

if [ "$append" = true ]; then
  [ -f "$map_md" ] || : > "$map_md"
  tmp_map="$(mktemp)"

  if grep -q '<!-- diagram:start -->' "$map_md" 2>/dev/null; then
    tmp_diagram="$(mktemp)"
    printf '%s\n' "$diagram" > "$tmp_diagram"
    # -v can't hold a multi-line value on every awk (BSD awk rejects embedded
    # newlines in -v assignments), so the replacement block is read from a file.
    awk -v blockfile="$tmp_diagram" '
      /<!-- diagram:start -->/ {
        print
        while ((getline bl < blockfile) > 0) print bl
        close(blockfile)
        skip = 1
        next
      }
      /<!-- diagram:end -->/ { skip = 0; print; next }
      { if (!skip) print }
    ' "$map_md" > "$tmp_map"
    rm -f "$tmp_diagram"
  else
    {
      cat "$map_md"
      printf '\n## Structure diagram\n\n<!-- diagram:start -->\n%s\n<!-- diagram:end -->\n' "$diagram"
    } > "$tmp_map"
  fi

  mv "$tmp_map" "$map_md"
  tmp_map=""
  echo "Diagram appended to $map_md" >&2
else
  printf '%s\n' "$diagram"
fi
