#!/bin/bash
# planning-with-files: User prompt submit hook for Cursor
# Injects plan context on every user message.
# Critical for session recovery after /clear — dumps actual content, not just advice.

# --- PWF_PLAN_ROOT: absolute plan-root binding (issue #212). ---
# A thread whose cwd is a shared PARENT of the real project can be pinned to
# the nested project root; every planning-state read below goes through the
# prefix. An explicit but broken pin fails CLOSED: one notice, nothing
# injected, never a silent fall back to the ambiguous cwd plan the caller was
# escaping. With the var unset the prefix is EMPTY so every path string stays
# byte-identical to the legacy shape. Wording matches scripts/inject-plan.sh.
PLAN_PREFIX=""
if [ -n "${PWF_PLAN_ROOT:-}" ]; then
    if [ -d "${PWF_PLAN_ROOT}" ]; then
        PLAN_PREFIX="${PWF_PLAN_ROOT}/"
    else
        echo "[planning-with-files] PWF_PLAN_ROOT is not a directory: ${PWF_PLAN_ROOT} — nothing injected."
        exit 0
    fi
fi

if [ -f "${PLAN_PREFIX}task_plan.md" ]; then
    # --- Nested-root conflict detection (issue #212): fail CLOSED on ambiguity.
    # This hook resolves only the legacy root task_plan.md, so any resolution
    # is a cwd GUESS unless PWF_PLAN_ROOT pinned it. If a direct child carries
    # its own competing .planning (an .active_plan pointer, or at least one
    # <slug>/task_plan.md), this cwd is a shared parent and injecting the root
    # plan is the wrong answer for at least one thread — inject NOTHING and
    # say why. Depth 1 only: one shell glob per hook fire is the whole perf
    # budget; `*` does not match dotted names, so the root's own .planning is
    # never a hit. Wording matches scripts/inject-plan.sh, minus the PLAN_ID
    # escape hatch this route does not implement.
    if [ -z "$PLAN_PREFIX" ]; then
        NESTED_LIST=""
        NESTED_N=0
        for nd in */.planning; do
            [ -d "$nd" ] || continue
            COMPETING=0
            [ -f "${nd}/.active_plan" ] && COMPETING=1
            if [ "$COMPETING" = "0" ]; then
                for np in "${nd}"/*/task_plan.md; do
                    [ -f "$np" ] && { COMPETING=1; break; }
                done
            fi
            [ "$COMPETING" = "1" ] || continue
            NR="${nd%/.planning}"
            NESTED_N=$((NESTED_N + 1))
            if [ "$NESTED_N" -le 3 ]; then
                if [ -z "$NESTED_LIST" ]; then NESTED_LIST="$NR"; else NESTED_LIST="${NESTED_LIST}, ${NR}"; fi
            fi
        done
        if [ "$NESTED_N" -gt 0 ]; then
            echo "[planning-with-files] Ambiguous plan: this cwd has an active plan and a nested project below it has its own (${NESTED_LIST}). Nothing injected. Pin the thread with PWF_PLAN_ROOT=<absolute path>."
            exit 0
        fi
    fi

    echo "[planning-with-files] ACTIVE PLAN — current state:"
    head -50 "${PLAN_PREFIX}task_plan.md"
    echo ""
    echo "=== recent progress ==="
    # Timestamp normalization matches scripts/inject-plan.sh (KV-cache stability, v2.40).
    tail -20 "${PLAN_PREFIX}progress.md" 2>/dev/null | sed -E 's/T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?Z/T00:00:00Z/g; s/T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?([+-][0-9]{2}:[0-9]{2})/T00:00:00\2/g'
    echo ""
    echo "[planning-with-files] Read findings.md for research context. Continue from the current phase."
fi
exit 0
