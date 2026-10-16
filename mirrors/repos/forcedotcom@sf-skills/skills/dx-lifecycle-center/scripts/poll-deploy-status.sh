#!/usr/bin/env bash
# Poll a Simple Deploy request until it reaches a terminal state, or check once.
# Read-only: issues only GET calls and SOQL queries.
#
# Two sources are read on every check, and a terminal state from EITHER one ends the poll:
#   1. the Simple Deploy status endpoint (live `step`, `metadata.deployId`)
#   2. DevopsRequestInfo, queried by RequestToken (the same record commit polling uses;
#      Status is SUCCESS or ERROR, with Message / ErrorDetails / RequestCompletionDate)
#
# Usage:
#   poll-deploy-status.sh --once <requestId> <source-org-alias>
#   poll-deploy-status.sh <requestId> <source-org-alias> [interval-seconds] [timeout-seconds]
# Env: DETAIL_WAIT=<seconds> how long to wait for the failure detail (default 20; 4 with --once)
#
# On failure the component-level errors are read from the DEPLOYMENT_COMPLETED
# DevopsActivityLog row of the request. Core's DeployDetailFetchHandler fills it in
# asynchronously (it calls the target org's Metadata API through the deploy's named
# credential), so no login to the target org is needed here. The script waits briefly
# for it, and stops waiting early if Core marks it errorDetailUnavailable.
#
# Prints one JSON object on stdout when the check ends:
#   outcome (SUCCEEDED|FAILED|NOT_FOUND|IN_PROGRESS|TIMEOUT), status, step, deployId, message,
#   errorMessage, errorDetails, deployJobLogURL, completedAt, decidedBy,
#   activityMessage, errorDetail (null when unavailable), errorDetailUnavailable, response
# Progress lines go to stderr.
#
# NOT_FOUND from the endpoint is tolerated for the first few polls: right after submit
# the status cache entry may not exist yet. A DevopsRequestInfo row overrides it.
#
# Exit codes:
#   0  deploy succeeded
#   1  usage error, missing dependency, or both status calls failed
#   2  deploy failed, or NOT_FOUND after the grace polls
#   3  timeout reached before a terminal state (poll mode); outcome TIMEOUT carries requestId,
#      step and deployId (when known) so the user can be told what to check
#   4  still processing (--once mode only)
set -euo pipefail

ONCE=0
ARGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --once) ONCE=1; shift ;;
    *) ARGS+=("$1"); shift ;;
  esac
done

REQUEST_ID="${ARGS[0]:-}"
SOURCE_ORG="${ARGS[1]:-}"
INTERVAL="${ARGS[2]:-10}"
TIMEOUT="${ARGS[3]:-100}"
API_VERSION="${SF_API_VERSION:-v67.0}"
API_VERSION="v${API_VERSION#v}"  # accept 67.0 or v67.0
NOT_FOUND_GRACE=3
DETAIL_WAIT="${DETAIL_WAIT:-20}"
[ "$ONCE" -eq 1 ] && DETAIL_WAIT="${DETAIL_WAIT_ONCE:-4}"

usage() {
  echo "Usage: poll-deploy-status.sh [--once] <requestId> <source-org-alias> [interval-seconds] [timeout-seconds]" >&2
  exit 1
}

[ -n "$REQUEST_ID" ] && [ -n "$SOURCE_ORG" ] || usage
case "$REQUEST_ID" in *[!A-Za-z0-9-]*) echo "requestId may only contain letters, digits and hyphens" >&2; exit 1 ;; esac
case "$INTERVAL$TIMEOUT" in *[!0-9]*) echo "interval and timeout must be whole numbers" >&2; exit 1 ;; esac
[ "$INTERVAL" -ge 1 ] || { echo "interval must be >= 1" >&2; exit 1; }
for dep in sf jq; do
  command -v "$dep" >/dev/null 2>&1 || { echo "Missing dependency: $dep" >&2; exit 1; }
done

PATH_URL="/services/data/${API_VERSION}/connect/devops/simple-deploy/deploy?requestID=${REQUEST_ID}"
SOQL="SELECT Id, Status, Message, ErrorDetails, RequestCompletionDate FROM DevopsRequestInfo WHERE RequestToken = '${REQUEST_ID}'"
START=$(date +%s)
NOT_FOUND_COUNT=0
POLLS=0

sfq() { env FORCE_COLOR=0 SF_CLI_DISABLE_AUTOUPDATE=true "$@"; }

# Failure detail from Core: DEPLOYMENT_COMPLETED DevopsActivityLog.Description (JSON) holds the flat
# errorMessage plus, once Core's async handler has run, errorDetail {componentFailures, testFailures,
# errorMessage, ...} or errorDetailUnavailable. Waits up to DETAIL_WAIT seconds for either marker.
ACT_MSG=""; ACT_DETAIL=null; ACT_UNAVAIL=false
fetch_failure_detail() {
  [ -n "$DRI_ID" ] || return 0
  local waited=0 q desc
  # No target-org deploy job (failed before the target, e.g. RETRIEVE_METADATA): Core will never add
  # errorDetail, and the flat message already says why, so do not wait.
  [ -n "$DEPLOY_ID" ] || DETAIL_WAIT=0
  while true; do
    q=$(sfq sf data query --target-org "$SOURCE_ORG" --json -q \
      "SELECT Description FROM DevopsActivityLog WHERE ActivityType = 'DEPLOYMENT_COMPLETED' AND DevopsRequestInfoId = '${DRI_ID}' LIMIT 1" 2>/dev/null) || q=""
    desc=$(printf '%s' "$q" | jq -r '.result.records[0].Description // empty' 2>/dev/null || true)
    if [ -n "$desc" ] && printf '%s' "$desc" | jq -e . >/dev/null 2>&1; then
      ACT_MSG=$(printf '%s' "$desc" | jq -r '.errorMessage // empty')
      ACT_DETAIL=$(printf '%s' "$desc" | jq -c '.errorDetail // null')
      ACT_UNAVAIL=$(printf '%s' "$desc" | jq -r 'if .errorDetailUnavailable then "true" else "false" end')
      if [ "$ACT_DETAIL" != "null" ] || [ "$ACT_UNAVAIL" = "true" ]; then return 0; fi
    fi
    [ "$waited" -ge "$DETAIL_WAIT" ] && return 0
    echo "waiting for Core to attach the failure detail (${waited}s/${DETAIL_WAIT}s)" >&2
    sleep 2; waited=$((waited + 2))
  done
}

# Emit the final JSON and exit. $1 outcome, $2 exit code, $3 decidedBy.
finish() {
  [ "$1" = "FAILED" ] && fetch_failure_detail
  jq -n \
    --arg outcome "$1" --arg decidedBy "$3" --arg requestId "$REQUEST_ID" \
    --arg status "$STATUS" --arg step "$STEP" --arg deployId "$DEPLOY_ID" \
    --arg errorMessage "$ERR_MSG" --arg logUrl "$LOG_URL" \
    --arg message "$DRI_MSG" --arg errorDetails "$DRI_ERR" --arg completedAt "$DRI_DONE" \
    --arg activityMessage "$ACT_MSG" --argjson errorDetail "$ACT_DETAIL" --argjson unavailable "$ACT_UNAVAIL" \
    --argjson response "${RESP_JSON:-null}" \
    '{requestId:$requestId, outcome:$outcome, status:$status, step:$step, deployId:$deployId,
      message:$message, errorMessage:$errorMessage, errorDetails:$errorDetails,
      activityMessage:$activityMessage, errorDetail:$errorDetail, errorDetailUnavailable:$unavailable,
      deployJobLogURL:$logUrl, completedAt:$completedAt, decidedBy:$decidedBy, response:$response}'
  exit "$2"
}

while true; do
  # --- source 1: Simple Deploy status endpoint
  EP_OK=1; RESP_JSON=null
  ERRF=$(mktemp)
  if OUT=$(sfq sf api request rest "$PATH_URL" --method GET --target-org "$SOURCE_ORG" 2>"$ERRF"); then
    RESP_JSON=$(printf '%s' "$OUT" | jq -c '.response // null' 2>/dev/null || echo null)
  else
    EP_OK=0
    echo "Status endpoint call failed: $(printf '%s%s' "$OUT" "$(cat "$ERRF")" | head -c 300)" >&2
  fi
  rm -f "$ERRF"

  jqr() { printf '%s' "$RESP_JSON" | jq -r "$1" 2>/dev/null || true; }
  STATUS=$(jqr '(.status // empty) | ascii_upcase')
  STEP=$(jqr '.step // empty')
  DEPLOY_ID=$(jqr '.metadata.deployId // empty')
  ERR_MSG=$(jqr '.errorMessage // empty')
  LOG_URL=$(jqr '.metadata.deployJobLogURL // empty')
  LOG_URL="${LOG_URL//\{version\}/${API_VERSION#v}}"  # the API returns a literal v{version}
  META=$(jqr '(.metadata.status // empty) | ascii_upcase')

  # --- source 2: DevopsRequestInfo (same record commit polling reads)
  DRI_ID=""; DRI_STATUS=""; DRI_MSG=""; DRI_ERR=""; DRI_DONE=""
  if DRI=$(sfq sf data query --target-org "$SOURCE_ORG" --json -q "$SOQL" 2>/dev/null); then
    DRI_ID=$(printf '%s' "$DRI" | jq -r '.result.records[0].Id // empty' 2>/dev/null || true)
    DRI_STATUS=$(printf '%s' "$DRI" | jq -r '(.result.records[0].Status // empty) | ascii_upcase' 2>/dev/null || true)
    DRI_MSG=$(printf '%s' "$DRI" | jq -r '.result.records[0].Message // empty' 2>/dev/null || true)
    DRI_ERR=$(printf '%s' "$DRI" | jq -r '.result.records[0].ErrorDetails // empty' 2>/dev/null || true)
    DRI_DONE=$(printf '%s' "$DRI" | jq -r '.result.records[0].RequestCompletionDate // empty' 2>/dev/null || true)
  fi

  if [ "$EP_OK" -eq 0 ] && [ -z "$DRI_STATUS" ]; then
    echo "Both status sources failed for requestId=${REQUEST_ID}" >&2
    exit 1
  fi

  # --- decide: a terminal state from either source wins
  case "$DRI_STATUS" in
    SUCCESS) STATUS=SUCCEEDED; finish SUCCEEDED 0 request-info ;;
    ERROR)   STATUS=FAILED; finish FAILED 2 request-info ;;
  esac
  case "$META" in
    SUCCEEDED|SUCCEEDEDPARTIAL|SUCCESS) [ "$STATUS" = "FAILED" ] || STATUS=SUCCEEDED ;;
    FAILED|CANCELED|CANCELLED) STATUS=FAILED ;;
  esac
  case "$STATUS" in
    SUCCEEDED|COMPLETED|SUCCESS|SUCCEEDED_PARTIAL) finish SUCCEEDED 0 endpoint ;;
    FAILED|ERROR|CANCELED|CANCELLED) finish FAILED 2 endpoint ;;
    NOT_FOUND)
      NOT_FOUND_COUNT=$((NOT_FOUND_COUNT + 1))
      if [ "$ONCE" -eq 1 ] || [ "$NOT_FOUND_COUNT" -gt "$NOT_FOUND_GRACE" ]; then
        finish NOT_FOUND 2 endpoint
      fi ;;
    QUEUED|STARTED|IN_PROGRESS|INPROGRESS|PENDING|CANCELING|"") ;;
    *)
      echo "Unexpected status '${STATUS}': ${RESP_JSON}" | head -c 500 >&2; echo >&2
      exit 1 ;;
  esac

  if [ "$ONCE" -eq 1 ]; then
    finish IN_PROGRESS 4 endpoint
  fi

  ELAPSED=$(( $(date +%s) - START ))
  if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
    echo "Timed out after ${TIMEOUT}s. requestId=${REQUEST_ID} status=${STATUS:-unknown} step=${STEP:-n/a}" >&2
    finish TIMEOUT 3 none
  fi
  REMAINING=$(( TIMEOUT - ELAPSED ))
  POLLS=$((POLLS + 1))
  # Quick early checks (fast deploys finish in seconds), then settle to INTERVAL.
  STEP_SLEEP=$INTERVAL
  if [ "$POLLS" -le 3 ] && [ "$INTERVAL" -gt 3 ]; then STEP_SLEEP=3
  elif [ "$POLLS" -le 6 ] && [ "$INTERVAL" -gt 5 ]; then STEP_SLEEP=5
  fi
  SLEEP=$(( STEP_SLEEP < REMAINING ? STEP_SLEEP : REMAINING ))
  echo "status=${STATUS:-pending} step=${STEP:-n/a} request-info=${DRI_STATUS:-none}; next check in ${SLEEP}s" >&2
  sleep "$SLEEP"
done
