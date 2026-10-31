#!/bin/bash
# prepare-text.sh <input-file> [workspace-dir]
#
# Converts a book/paper source file into a plain-text workspace copy with
# [[page N]] markers (the coordinate system every other deep-reader script
# relies on). Idempotent: if the workspace already has a source.txt, it is
# reported as-is instead of being reconverted.
set -euo pipefail

usage() {
  echo "Usage: prepare-text.sh <input-file> [workspace-dir]" >&2
  exit 1
}

[ $# -ge 1 ] && [ $# -le 2 ] || usage

input="$1"
[ -f "$input" ] || { echo "Input file not found: $input" >&2; exit 1; }

base="$(basename "$input")"
ext="$(printf '%s' "${base##*.}" | tr '[:upper:]' '[:lower:]')"

case "$ext" in
  pdf|epub|docx|txt|md) ;;
  *)
    echo "Unsupported format: .$ext (supported: pdf, epub, docx, txt, md)" >&2
    exit 1
    ;;
esac

name_noext="${base%.*}"
slug="$(printf '%s' "$name_noext" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"
[ -n "$slug" ] || slug="doc"

dir_of_input="$(cd "$(dirname "$input")" && pwd)"

if [ $# -eq 2 ]; then
  workspace="$2"
else
  workspace="$dir_of_input/$slug-notes"
fi

mkdir -p "$workspace/notes"
workspace="$(cd "$workspace" && pwd)"
source_txt="$workspace/source.txt"

tmp_out=""
# NOTE: this must always end up exiting 0 itself. Bash quirk: with no explicit
# `exit N` at the end of the script, an EXIT trap whose own last command
# evaluates non-zero (e.g. a false `[ -n "$tmp_out" ]` guard when there is
# nothing to clean up) silently overrides the script's real exit status.
cleanup() { rm -f "${tmp_out:-}" 2>/dev/null; return 0; }
trap cleanup EXIT

existing=false
if [ -s "$source_txt" ]; then
  existing=true
  echo "Workspace already prepared; reporting existing stats: $source_txt" >&2
else
  echo "Preparing text from $input (.$ext) into $workspace" >&2
  tmp_out="$(mktemp)"

  case "$ext" in
    pdf)
      if ! command -v pdftotext >/dev/null 2>&1; then
        {
          echo "Missing dependency: pdftotext (poppler)."
          echo "Install: brew install poppler   (macOS)   |   apt-get install poppler-utils   (Debian/Ubuntu)"
          echo "Fallback: read the PDF directly with the Read tool in page batches. Note that without" \
               "source.txt, verify-quotes.sh cannot run later; do manual targeted re-reads to check quotes instead."
        } >&2
        exit 2
      fi
      # pdftotext -layout separates pages with a form-feed (\f). Turn each page
      # into a [[page N]] marker followed by its text; drop a trailing empty
      # page if the stream ends with a stray form feed.
      pdftotext -layout "$input" - | awk '
        BEGIN { RS = "\f"; n = 0 }
        { n++; pages[n] = $0 }
        END {
          last = pages[n]
          gsub(/[ \t\n]/, "", last)
          if (last == "" && n > 1) n--
          for (i = 1; i <= n; i++) {
            print "[[page " i "]]"
            print pages[i]
          }
        }' > "$tmp_out"
      ;;
    epub|docx)
      if ! command -v pandoc >/dev/null 2>&1; then
        {
          echo "Missing dependency: pandoc."
          echo "Install: brew install pandoc   (macOS)   |   apt-get install pandoc   (Debian/Ubuntu)"
          echo "Fallback: read the source file directly with the Read tool (in batches). Note that without" \
               "source.txt, verify-quotes.sh cannot run later; do manual targeted re-reads to check quotes instead."
        } >&2
        exit 2
      fi
      # No real page numbers in EPUB/DOCX: synthesize ~500-word pages. Word
      # granularity (not line granularity) matters here: pandoc --wrap=none
      # puts an entire unwrapped paragraph on one line, so a whole chapter
      # can arrive as a single multi-thousand-word "line" that a line-level
      # page break would never split.
      pandoc -t plain --wrap=none "$input" | awk -v wpp=500 '
        BEGIN { wc = 0; page = 1; print "[[page 1]]" }
        {
          if (NF == 0) { print ""; next }
          buf = ""
          for (i = 1; i <= NF; i++) {
            if (wc > 0 && wc % wpp == 0) {
              if (buf != "") { print buf; buf = "" }
              page++
              print "[[page " page "]]"
            }
            buf = (buf == "") ? $i : buf " " $i
            wc++
          }
          print buf
        }
      ' > "$tmp_out"
      ;;
    txt|md)
      # No real page numbers: synthesize ~500-word pages (see word-granularity
      # note above; plain .txt/.md can also contain very long single lines).
      awk -v wpp=500 '
        BEGIN { wc = 0; page = 1; print "[[page 1]]" }
        {
          if (NF == 0) { print ""; next }
          buf = ""
          for (i = 1; i <= NF; i++) {
            if (wc > 0 && wc % wpp == 0) {
              if (buf != "") { print buf; buf = "" }
              page++
              print "[[page " page "]]"
            }
            buf = (buf == "") ? $i : buf " " $i
            wc++
          }
          print buf
        }
      ' "$input" > "$tmp_out"
      ;;
  esac

  mv "$tmp_out" "$source_txt"
  tmp_out=""
fi

pages=$(grep -Ec '^\[\[page [0-9]+\]\]$' "$source_txt")
words=$(grep -Ev '^\[\[page [0-9]+\]\]$' "$source_txt" | wc -w | tr -d ' ')
est_tokens=$(awk -v w="$words" 'BEGIN { printf "%d", (w * 4 / 3) + 0.5 }')

if [ "$ext" = "pdf" ]; then
  synthetic_pages=false
else
  synthetic_pages=true
fi

if [ "$est_tokens" -lt 50000 ]; then
  mode_hint="small — direct reading may suffice; overview rarely needs the full pipeline"
elif [ "$est_tokens" -le 150000 ]; then
  mode_hint="medium — study mode sequential"
else
  mode_hint="large — study mode; consider per-chapter subagent fan-out"
fi

cat <<JSON
{
  "workspace": "$workspace",
  "source_txt": "$source_txt",
  "format": "$ext",
  "pages": $pages,
  "synthetic_pages": $synthetic_pages,
  "words": $words,
  "est_tokens": $est_tokens,
  "mode_hint": "$mode_hint",
  "existing": $existing
}
JSON
