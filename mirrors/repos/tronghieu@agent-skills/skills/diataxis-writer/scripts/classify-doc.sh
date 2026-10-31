#!/bin/bash
set -e

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

CONTENT_FILE="$TMP_DIR/content.txt"

if [ "${1:-}" != "" ]; then
  if [ ! -f "$1" ]; then
    echo "Input file not found: $1" >&2
    exit 1
  fi
  cp "$1" "$CONTENT_FILE"
  SOURCE="$1"
else
  cat > "$CONTENT_FILE"
  SOURCE="stdin"
fi

echo "Analyzing Diataxis signals from $SOURCE" >&2

LOWER_FILE="$TMP_DIR/content-lower.txt"
tr '[:upper:]' '[:lower:]' < "$CONTENT_FILE" > "$LOWER_FILE"

count_pattern() {
  grep -Eio "$1" "$LOWER_FILE" | wc -l | tr -d ' '
}

tutorial_score=0
howto_score=0
reference_score=0
explanation_score=0

tutorial_score=$((tutorial_score + $(count_pattern 'tutorial|walkthrough|lesson|exercise|practice|beginner|getting started|learn|first app|quickstart')))
howto_score=$((howto_score + $(count_pattern 'how to|steps|procedure|configure|install|deploy|migrate|troubleshoot|fix|set up|setup|verify|rollback')))
reference_score=$((reference_score + $(count_pattern 'reference|api|endpoint|parameter|field|schema|option|flag|command|syntax|default|limit|property|attribute')))
explanation_score=$((explanation_score + $(count_pattern 'why|concept|architecture|background|rationale|trade[- ]?off|overview|mental model|design decision|understand')))

step_headings=$(grep -Eic '^(#{1,6} )?(step [0-9]+|[0-9]+\. )' "$LOWER_FILE" || true)
table_lines=$(grep -Ec '^\s*\|' "$LOWER_FILE" || true)
why_headings=$(grep -Eic '^#{1,6} .*(why|concept|architecture|overview|rationale|trade)' "$LOWER_FILE" || true)

howto_score=$((howto_score + step_headings))
reference_score=$((reference_score + table_lines / 2))
explanation_score=$((explanation_score + why_headings * 2))

likely_type="unknown"
max_score=0

set_likely() {
  local type="$1"
  local score="$2"
  if [ "$score" -gt "$max_score" ]; then
    likely_type="$type"
    max_score="$score"
  fi
}

set_likely "tutorial" "$tutorial_score"
set_likely "how-to" "$howto_score"
set_likely "reference" "$reference_score"
set_likely "explanation" "$explanation_score"

active_types=0
for score in "$tutorial_score" "$howto_score" "$reference_score" "$explanation_score"; do
  if [ "$score" -ge 3 ]; then
    active_types=$((active_types + 1))
  fi
done

mixed=false
if [ "$active_types" -ge 2 ]; then
  mixed=true
fi

if [ "$max_score" -eq 0 ]; then
  recommendation="No strong Diataxis signal found. Identify the reader job before writing or restructuring."
elif [ "$mixed" = true ]; then
  recommendation="Mixed signals found. Choose one primary reader job and move supporting material into separate or related sections."
else
  recommendation="Likely $likely_type. Structure the document around that reader job and keep other Diataxis types secondary."
fi

cat <<JSON
{
  "source": "$SOURCE",
  "likely_type": "$likely_type",
  "mixed_signals": $mixed,
  "scores": {
    "tutorial": $tutorial_score,
    "how_to": $howto_score,
    "reference": $reference_score,
    "explanation": $explanation_score
  },
  "structural_signals": {
    "step_headings": $step_headings,
    "table_lines": $table_lines,
    "why_or_concept_headings": $why_headings
  },
  "recommendation": "$recommendation"
}
JSON
