#!/usr/bin/env bash
# Prüft, ob alle Phasen in task_plan.md abgeschlossen sind
# Immer mit Exit-Code 0 beenden — Status über stdout melden
# Wird vom Stop-Hook aufgerufen, um Aufgabenabschlussstatus zu melden

# Explicit creation validation; the existing localized advisory path stays unchanged.
VALIDATE=0
VALIDATION_PLAN=""
for _arg in "$@"; do
    case "$_arg" in
        --validate) VALIDATE=1 ;;
        *) [ -z "$VALIDATION_PLAN" ] && VALIDATION_PLAN="$_arg" ;;
    esac
done
if [ "$VALIDATE" -eq 1 ]; then
    PLAN_FILE="${VALIDATION_PLAN:-task_plan.md}"
    [ -f "$PLAN_FILE" ] || { echo "[planning-with-files] Plan format invalid: task_plan.md was not found." >&2; exit 1; }
fi

# Creation validation is deliberately separate from advisory/gated completion.
# Keep one native status per phase, including the existing inline form. This
# never repairs or writes the plan, changes attestation, or weakens Stop guards.
if [ "$VALIDATE" -eq 1 ]; then
    awk '
        function finish_phase() {
            if (in_phase && statuses != 1) invalid = 1
        }
        /^### Phase([ \t]|$)/ {
            finish_phase()
            phases++
            in_phase = 1
            statuses = 0
        }
        !/^### Phase([ \t]|$)/ && /^#[ \t]|^##[ \t]|^###[ \t]/ {
            finish_phase()
            in_phase = 0
        }
        in_phase {
            line = $0
            statuses += gsub(/\*\*Status:\*\*[ \t]+(pending|in_progress|complete)([^[:alnum:]_]|$)/, "&", line)
            line = $0
            statuses += gsub(/\[(pending|in_progress|complete)\]/, "&", line)
        }
        END {
            finish_phase()
            if (!phases || invalid) {
                print "[planning-with-files] Plan format invalid: use ### Phase headings with exactly one native status per phase."
                exit 1
            }
            printf "[planning-with-files] Plan format valid (%d phases).\n", phases
        }
    ' "$PLAN_FILE"
    exit "$?"
fi

# issue #195: per-invocation opt-out (PLANNING_DISABLED=1) for one-shot/CI
# sessions that share a cwd with a plan but never opted into it.
[ "${PLANNING_DISABLED:-}" = "1" ] && exit 0

PLAN_FILE="${1:-task_plan.md}"

if [ ! -f "$PLAN_FILE" ]; then
    # Automatic gate checks have nothing to report without a plan (header:
    # "plans stay silent in --gate mode"); the explicit report keeps its notice.
    [ "$GATE" -eq 1 ] && exit 0
    echo "[planning-with-files-de] task_plan.md nicht gefunden — keine aktive Planungssitzung."
    exit 0
fi

# Gesamtzahl der Phasen zählen
TOTAL=$(grep -c "### Phase" "$PLAN_FILE" || true)

# Zuerst **Status:** Format prüfen
COMPLETE=$(grep -cF "**Status:** complete" "$PLAN_FILE" || true)
IN_PROGRESS=$(grep -cF "**Status:** in_progress" "$PLAN_FILE" || true)
PENDING=$(grep -cF "**Status:** pending" "$PLAN_FILE" || true)

# Fallback: Wenn **Status:** nicht gefunden, [complete] Inline-Format prüfen
if [ "$COMPLETE" -eq 0 ] && [ "$IN_PROGRESS" -eq 0 ] && [ "$PENDING" -eq 0 ]; then
    COMPLETE=$(grep -c "\[complete\]" "$PLAN_FILE" || true)
    IN_PROGRESS=$(grep -c "\[in_progress\]" "$PLAN_FILE" || true)
    PENDING=$(grep -c "\[pending\]" "$PLAN_FILE" || true)
fi

# Auf 0 setzen, wenn leer
: "${TOTAL:=0}"
: "${COMPLETE:=0}"
: "${IN_PROGRESS:=0}"
: "${PENDING:=0}"

# Status melden (immer mit Exit-Code 0 beenden — unvollständige Aufgaben sind normaler Zustand)
# issue #191: TOTAL=0 -> not phase-structured, stay silent
if [ "$TOTAL" -eq 0 ]; then
    exit 0
fi

if [ "$COMPLETE" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
    echo "[planning-with-files-de] Alle Phasen abgeschlossen ($COMPLETE/$TOTAL). Wenn der Benutzer zusätzliche Arbeit hat, neue Phasen in task_plan.md hinzufügen, bevor du beginnst."
else
    echo "[planning-with-files-de] Aufgabe läuft ($COMPLETE/$TOTAL Phasen abgeschlossen). progress.md vor dem Stoppen aktualisieren."
    if [ "$IN_PROGRESS" -gt 0 ]; then
        echo "[planning-with-files-de] $IN_PROGRESS Phasen noch in Bearbeitung."
    fi
    if [ "$PENDING" -gt 0 ]; then
        echo "[planning-with-files-de] $PENDING Phasen ausstehend."
    fi
fi
exit 0
