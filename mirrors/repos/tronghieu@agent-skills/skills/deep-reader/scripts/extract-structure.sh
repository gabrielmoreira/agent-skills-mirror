#!/bin/bash
# extract-structure.sh <source.txt>
#
# Heuristic outline seed: scans a prepared source.txt for lines that look
# like headings and prints them with their page number. This is intentionally
# noisy (it is a seed to confirm against the real table of contents, not a
# final chapters.tsv) — see SKILL.md for how it's meant to be used.
set -euo pipefail

usage() {
  echo "Usage: extract-structure.sh <source.txt>" >&2
  exit 1
}

[ $# -eq 1 ] || usage
source_txt="$1"
[ -f "$source_txt" ] || { echo "Source file not found: $source_txt" >&2; exit 1; }

awk '
BEGIN {
  page = 0
  # --- Heading heuristics: the single source of truth for the pattern list ---
  # 1. English section markers with a number: Chapter/CHAPTER/Part/PART/Book N
  #    (digits or roman numerals), matched case-insensitively via tolower().
  re_en_num   = "^(chapter|part|book)[[:blank:]]+([0-9]+|[ivxlcdm]+)([[:blank:]:.,-]|$)"
  # 2. Vietnamese section markers with a number: Chuong/Phan/Muc N. Matched
  #    case-sensitively against the raw line: POSIX awk tolower() is ASCII-only
  #    and does not reliably fold Vietnamese accented capitals.
  re_vi_num   = "(Chương|chương|Phần|phần|Mục|mục)[[:blank:]]+[0-9IVXLCDMivxlcdm]+([[:blank:]:.,-]|$)"
  # 3. Numbered headings: "1", "2.3", "4)" followed by whitespace and more text.
  re_numbered = "^[0-9]+(\\.[0-9]+)*[.)]?[[:blank:]]+[^[:blank:]]"
  # 4. Standalone structural words (front/back matter), matched case-insensitively
  #    via tolower(); optionally followed by a short label ("Appendix A") or a
  #    trailing colon/period. This also covers reasonable ALL-CAPS variants,
  #    since ALL CAPS lowercases to the same pattern.
  re_struct   = "^(preface|foreword|introduction|prologue|contents|abstract|conclusion|epilogue|appendix|glossary|bibliography|references|index|acknowledgments|acknowledgements)([[:blank:]]+[a-z0-9]+)?[:.]?[[:blank:]]*$"
}
/^\[\[page [0-9]+\]\]$/ {
  page = $0
  gsub(/[^0-9]/, "", page)
  next
}
{
  line = $0
  gsub(/^[[:blank:]]+|[[:blank:]]+$/, "", line)
  if (line == "" || length(line) > 120) next
  lower = tolower(line)
  if (lower ~ re_en_num || line ~ re_vi_num || line ~ re_numbered || lower ~ re_struct) {
    print "- [p. " page "] " line
  }
}
' "$source_txt"
