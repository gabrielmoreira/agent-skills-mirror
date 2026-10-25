#!/bin/sh
# Cursor reader adapter for the canonical skill-owned plan resolver.
# Set CURSOR_PLAN_DIR only for selected or legitimate legacy state. Empty
# resolver output also represents refusals, so it must not imply root fallback.

cursor_resolve_plan_context() {
    CURSOR_PLAN_DIR=""
    CURSOR_PLAN_STATUS="invalid"
    CURSOR_PLAN_DETAIL="resolver-error"
    _cursor_hook_dir="$1"
    _cursor_legacy_root="$(pwd)" || return 0

    if [ -n "${PWF_PLAN_ROOT:-}" ]; then
        case "${PWF_PLAN_ROOT}" in
            \\\\*|//*|[A-Za-z]:[!\\/]*|'')
                CURSOR_PLAN_STATUS="invalid-pin"
                CURSOR_PLAN_DETAIL="${PWF_PLAN_ROOT}"
                return 0 ;;
            /*|[A-Za-z]:[\\/]*) ;;
            *)
                CURSOR_PLAN_STATUS="invalid-pin"
                CURSOR_PLAN_DETAIL="${PWF_PLAN_ROOT}"
                return 0 ;;
        esac
        if [ ! -d "${PWF_PLAN_ROOT}" ]; then
            CURSOR_PLAN_STATUS="invalid-pin"
            CURSOR_PLAN_DETAIL="${PWF_PLAN_ROOT}"
            return 0
        fi
        _cursor_legacy_root="${PWF_PLAN_ROOT}"
    fi

    _cursor_plan_root="${_cursor_legacy_root}/.planning"
    if [ -z "${PLAN_ID:-}" ] && [ ! -d "${_cursor_plan_root}" ]; then
        CURSOR_PLAN_DIR="${_cursor_legacy_root}"
        CURSOR_PLAN_STATUS="legacy"
        return 0
    fi

    _cursor_resolver="${_cursor_hook_dir}/resolve-plan-dir.sh"
    _cursor_canonical="${_cursor_hook_dir}/../skills/planning-with-files/scripts/resolve-plan-dir.sh"
    if [ ! -f "${_cursor_resolver}" ] || [ ! -f "${_cursor_canonical}" ]; then
        CURSOR_PLAN_DETAIL="resolver-missing"
        return 0
    fi

    # An explicit PLAN_ID outranks this unused pointer. Otherwise reject its
    # unsafe object type before the resolver can read a link or scan past it.
    _cursor_active="${_cursor_plan_root}/.active_plan"
    if [ -z "${PLAN_ID:-}" ]; then
        if [ -d "${_cursor_active}" ] || [ -L "${_cursor_active}" ]; then
            CURSOR_PLAN_DETAIL="unsafe-pointer"
            return 0
        fi
    fi

    # Named-plan selection, slug validation and physical containment remain owned
    # by the canonical resolver. This adapter only classifies an empty result.
    _cursor_resolved="$(sh "${_cursor_resolver}" 2>/dev/null)" || return 0
    if [ -n "${_cursor_resolved}" ]; then
        CURSOR_PLAN_DIR="${_cursor_resolved}"
        CURSOR_PLAN_STATUS="selected"
        return 0
    fi
    _cursor_ambiguity="$(sh "${_cursor_resolver}" --check-ambiguity 2>/dev/null)" || return 0
    if [ "${_cursor_ambiguity}" = "PWF_PLAN_AMBIGUOUS_V1" ]; then
        CURSOR_PLAN_STATUS="ambiguous"
        return 0
    fi
    if [ -n "${PLAN_ID:-}" ]; then
        CURSOR_PLAN_STATUS="invalid-plan-id"
        CURSOR_PLAN_DETAIL="${PLAN_ID}"
        return 0
    fi

    # Match the PowerShell adapter: a live slug-shaped plan that the resolver
    # refused is not legacy state. Stale pointers and invalid/dot names can
    # still fall back to legacy. No candidate is selected or canonicalized here.
    for _cursor_plan_file in "${_cursor_plan_root}"/*/task_plan.md; do
        [ -f "${_cursor_plan_file}" ] || continue
        _cursor_candidate="${_cursor_plan_file%/task_plan.md}"
        _cursor_slug="${_cursor_candidate##*/}"
        case "${_cursor_slug}" in
            ''|[!A-Za-z0-9_]*|*[!A-Za-z0-9._-]*) continue ;;
        esac
        CURSOR_PLAN_STATUS="refused"
        CURSOR_PLAN_DETAIL="containment"
        return 0
    done
    CURSOR_PLAN_DIR="${_cursor_legacy_root}"
    CURSOR_PLAN_STATUS="legacy"
    return 0
}
