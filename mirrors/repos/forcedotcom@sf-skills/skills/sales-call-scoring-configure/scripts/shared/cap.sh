#!/bin/bash
# Shared cap-diagnosis helpers for the 8-active EnablementCompetencyDef limit.
#
# Server-side, EnablementCompetencyDef enforces a hard cap of 8 IsActive=true
# records per org (CoachingCompetenciesFeature.MAX_ACTIVE_COMPETENCIES). All
# five write scripts (create-competency, create-custom-competency,
# toggle-custom-competency, install-ootb-competencies,
# install-best-practice-competencies) call these helpers to keep the
# admin-facing cap message identical across the surface.
#
# Contract for callers: source this file, then use
#   query_active_count <ORG_ALIAS>
#   print_cap_report   <ORG_ALIAS> <CONTEXT>
#   print_cap_footer_activate_hint <NEW_ID_OR_NAME>
#
# CONTEXT is a short human phrase used in the header, e.g.
#   "creating '$MASTER_LABEL'"     (create paths)
#   "activating '$REC_LABEL'"      (toggle paths)
#   "installing OOTB competencies" (installer paths)
#
# All queries run through `sf api request rest --target-org` so the org's
# access token is never passed as curl argv (visible in the process table).
# Nothing here writes to the org — read-only diagnosis only. The decision to
# fall back to inactive (custom / installer paths) or refuse outright (toggle
# path — you can't activate to inactive) is the caller's.

MAX_ACTIVE_COMPETENCIES=8
CAP_TOOLING_BASE="services/data/v68.0/tooling"

# Return the current active count (or "0" on any failure — callers should
# treat a query failure as "cannot verify cap" and continue optimistically;
# the server-side hard cap still protects them).
query_active_count() {
  local org_alias="$1"
  (sf api request rest \
    "${CAP_TOOLING_BASE}/query/?q=SELECT+COUNT()+FROM+EnablementCompetencyDef+WHERE+IsActive=true" \
    --target-org "$org_alias" 2>/dev/null || true) \
    | jq -r '.totalSize // 0' 2>/dev/null || echo "0"
}

# Print a rich, admin-actionable cap report to stderr. Lists the currently
# active competencies with their Ids (deactivate command is copy-pasteable)
# and explains next steps. Caller supplies the context string that goes at
# the top ("Cap reached while <context>").
print_cap_report() {
  local org_alias="$1"
  local context="$2"

  local list_json
  list_json=$(sf api request rest \
    "${CAP_TOOLING_BASE}/query/?q=SELECT+Id,MasterLabel,DeveloperName,SourceCompetencyTemplate+FROM+EnablementCompetencyDef+WHERE+IsActive=true+ORDER+BY+MasterLabel" \
    --target-org "$org_alias" 2>/dev/null || true)

  {
    echo ""
    echo "Warning: Active Coaching Competency cap reached while ${context}."
    echo ""
    echo "    Salesforce allows up to ${MAX_ACTIVE_COMPETENCIES} active competencies per org."
    echo "    This org currently has ${MAX_ACTIVE_COMPETENCIES} active — listed below."
    echo ""
    echo "    Currently active:"
    echo "$list_json" | jq -r '.records[]? | "      • \(.MasterLabel)  (\(.Id))"' 2>/dev/null || echo "      (unable to list — the server-side cap check will still enforce this)"
    echo ""
    echo "    To free a slot, deactivate one of the above:"
    echo "$list_json" | jq -r '.records[0:1][]? | "      ./skills/sales-call-scoring-configure/scripts/toggle-custom-competency.sh <alias> \(.Id) deactivate"' 2>/dev/null
    echo ""
  } >&2
}

# Print the second half of the fallback message (only used by paths that
# auto-create an inactive record). Explains what just happened and how to
# flip it on later.
#
# Args:
#   $1 = record identifier the admin can copy-paste (Id preferred,
#        MasterLabel acceptable)
print_cap_footer_activate_hint() {
  local ident="$1"
  {
    echo "    The new competency was created INACTIVE so your work isn't blocked."
    echo "    Once you deactivate an existing competency, activate the new one:"
    echo ""
    echo "      ./skills/sales-call-scoring-configure/scripts/toggle-custom-competency.sh <alias> ${ident} activate"
    echo ""
  } >&2
}
