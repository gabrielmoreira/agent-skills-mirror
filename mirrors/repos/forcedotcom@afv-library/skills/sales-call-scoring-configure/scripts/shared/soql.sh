#!/usr/bin/env bash
# soql.sh — SOQL string-literal escaping.
#
# soql_escape RAW → SAFE
#   Prints RAW with every character that has meaning inside a SOQL string
#   literal escaped so the caller can wrap the result in single quotes:
#
#       WHERE MasterLabel='$(soql_escape "$LABEL")'
#
#   Escapes, in order:
#     \  → \\        (must happen first)
#     '  → \'
#
#   Order matters. If the quote-pass ran first, the backslash-pass would
#   double-escape the backslash inserted for quotes and re-open the string.
#
#   Implemented with sed rather than bash parameter expansion. The natural
#   "${var//\'/\\\'}" pattern silently emits TWO backslashes in the
#   replacement because of how backslashes are consumed by both the shell
#   scanner and the parameter-expansion replacement string. sed sidesteps
#   that quirk and its escape rules match SOQL's directly.

soql_escape() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e "s/'/\\\\'/g"
}
