#!/usr/bin/env bash
#
# devhub.sh — Enable Dev Hub and view scratch org allocation for a Salesforce
#             org, via the Salesforce CLI (sf).
#
# Dev Hub is the org feature that lets you create and manage scratch orgs and
# second-generation (2GP)/unlocked packages. This script reports whether Dev Hub
# is enabled, shows the org's scratch org ALLOCATION (Active/Daily limits and how
# many remain, with pre-flight warnings), reports the org EDITION, reads the
# current DevHubSettings PREFERENCES, ENABLES Dev Hub (or configures its
# sub-preferences) via a Metadata API deploy, and lists the active scratch orgs
# created from the Dev Hub. It can also list the authenticated orgs on this
# machine. It does NOT authenticate new orgs — that is a precondition; the script
# only prints the login command as guidance.
#
# How enablement works: the Dev Hub master switch is the deployable metadata
# field DevHubSettings.enableScratchOrgManagementPref (there is NO "enableDevHub"
# field, and no dedicated `sf` command). Deploying it true is exactly what the
# Setup toggle does. This script builds a DevHub.settings-meta.xml and deploys
# it. Enabling requires a user with ModifyAllData or ModifyMetadata (System
# Administrator has these); the org must NOT have a registered namespace and must
# NOT be a sandbox; and once on, Dev Hub CANNOT be turned off.
#
# How enablement is detected: the standard object ScratchOrgInfo is provisioned
# and becomes queryable only when Dev Hub is enabled. A successful "SELECT
# COUNT() FROM ScratchOrgInfo" means Dev Hub is ON; an INVALID_TYPE error means
# it is OFF. (Note: `sf org list limits` reports ActiveScratchOrgs/
# DailyScratchOrgs rows even on non-Dev-Hub orgs, so limits alone are NOT a
# reliable enablement test.)
#
# Usage:
#   devhub.sh [org]                     # status: is Dev Hub on? + edition + allocation
#   devhub.sh [org] --allocation        # scratch org allocation only (with warnings)
#   devhub.sh [org] --show-settings     # read current DevHubSettings preferences
#   devhub.sh [org] --list-scratch      # list this Dev Hub's active scratch orgs
#   devhub.sh --list-orgs               # list authenticated orgs on this machine
#   devhub.sh [org] --enable            # validate enabling Dev Hub (dry run)
#   devhub.sh [org] --enable --apply    # actually enable Dev Hub (irreversible)
#   devhub.sh [org] --enable --packaging --apply       # enable + turn on 2GP
#   devhub.sh [org] --configure --snapshots --apply    # set a sub-pref (Dev Hub already on)
#   devhub.sh [org] --json              # machine-readable status
#   devhub.sh --fail-if-disabled        # exit 3 if Dev Hub is not enabled (CI gate)
#
# "org" is an alias or username. If omitted, the default target-org is used, and
# if that is unset, the default target-dev-hub. If neither is set, the script
# lists the authenticated orgs and asks you to pass one or set a default.
#
# Options:
#   --allocation, -A        Show only the scratch org allocation (Active/Daily),
#                           with a WARN when <2 remain and a NOTE above 80% usage.
#   --show-settings, -s     Read and show which DevHubSettings preferences are
#                           currently enabled/disabled (Tooling API). Dev Hub must
#                           be on.
#   --list-scratch, -l      List active scratch orgs created from this Dev Hub.
#   --list-orgs             List the orgs authenticated with the Salesforce CLI.
#   --enable, -e            Enable Dev Hub (deploys enableScratchOrgManagementPref
#                           =true). Defaults to a validate-only dry run; add
#                           --apply to actually enable. May be combined with the
#                           sub-pref flags below to enable and configure at once.
#   --configure, -c         Configure Dev Hub sub-preferences without (re)enabling
#                           the master switch. Pair with one or more pref flags.
#                           Defaults to a dry run; add --apply to deploy.
#     --packaging             enablePackaging2=true  (Unlocked + 2GP packages)
#     --snapshots             enableScratchOrgSnapshotPref=true
#     --shape                 enableShapeExportPref=true
#     --scratch-management    enableScratchOrgManagementPref=true (the Dev Hub switch)
#     --pref KEY=VALUE        Any DevHubSettings sub-pref (KEY must start with
#                             "enable"; VALUE is true|false). Repeatable.
#   --apply                 Actually deploy (default for --enable/--configure is a
#                           validate-only dry run).
#   --json                  Emit machine-readable JSON.
#   --fail-if-disabled      Exit 3 if Dev Hub is not enabled on the target org.
#   --help, -h              Show this help.
#
# Authentication is a precondition. If an org is not authenticated, the script
# prints the exact `sf org login web` command to run — it never opens a browser
# or logs in for you.
#
# Exit codes:
#   0  success
#   1  the org could not be queried, or a deploy failed (auth/connection/deploy)
#   2  bad usage / missing dependency (sf or jq)
#   3  Dev Hub is not enabled (only when --fail-if-disabled is set)

set -uo pipefail

die() { echo "Error: $*" >&2; exit 2; }

# The skill must be invoked by ABSOLUTE path (see SKILL.md): a relative path like
# ./scripts/devhub.sh resolves against the caller's CWD and can run the wrong
# file. Enforce it here so the guarantee is deterministic and not left to the
# model. (A leading "/" is the portable test for an absolute path.)
case "$0" in
  /*) : ;;
  *) die "Run this script by its absolute path (got: '$0'). Example: bash \"/abs/path/to/skills/dx-org-devhub-configure/scripts/devhub.sh\"" ;;
esac

command -v sf >/dev/null 2>&1 || die "Salesforce CLI ('sf') not found on PATH."
command -v jq >/dev/null 2>&1 || die "'jq' not found on PATH."

# Keep CLI update chatter out of captured JSON/stdout.
export SF_AUTOUPDATE_DISABLE=true

# --- constants -----------------------------------------------------------
SETTINGS_API_VERSION="62.0"          # DevHubSettings: base fields >=47.0, but
                                     # enableShapeExportPref needs >=55.0 and
                                     # enableScratchOrgSnapshotPref needs >=61.0,
                                     # so read/deploy at a version that has them all.
DEVHUB_SWITCH="enableScratchOrgManagementPref"

# --- option state --------------------------------------------------------
TARGET=""                   # org alias/username (positional or resolved default)
TARGET_EXPLICIT=0            # 1 when the caller supplied an org alias/username
MODE="status"               # status | allocation | settings | list | listorgs | deploy
ENABLING=0                  # 1 when --enable was passed (seeds the master switch)
OUTPUT="human"              # human | json
APPLY=0                     # deploy: 0 = dry run (validate only), 1 = real deploy
FAIL_IF_DISABLED=0
PREFS=()                    # requested DevHubSettings prefs (KEY=VALUE)

# --- run state -----------------------------------------------------------
DEVHUB_STATE=""             # enabled | disabled | auth_error
DEVHUB_ERRNAME=""           # error .name when auth_error
DEVHUB_ERRMSG=""
SCRATCH_COUNT=""            # ScratchOrgInfo count when enabled
INSTANCE_URL=""             # resolved org instance URL (for the Setup deep link)
ORG_EDITION=""              # Organization.OrganizationType (best effort)
ORG_IS_SANDBOX=""           # true|false (best effort)
ORG_FACTS_DONE=0            # 1 once org_facts has run

usage() {
  sed -n '2,/^set -uo/p' "$0" | sed '/^set -uo/d; s/^# \{0,1\}//; s/^#//'
}

# Set MODE, rejecting a second conflicting mode selection.
set_mode() {
  if [ "$MODE" != "status" ] && [ "$MODE" != "$1" ]; then
    die "Choose only one of --allocation, --show-settings, --list-scratch, --list-orgs, --enable/--configure."
  fi
  MODE="$1"
}

# True if PREFS already contains a KEY (any value).
has_pref_key() {
  local p
  for p in "${PREFS[@]:-}"; do
    [ -n "$p" ] || continue
    [ "${p%%=*}" = "$1" ] && return 0
  done
  return 1
}

# Register a pref for deploy, validating shape and giving actionable guidance
# for the common wrong field name. De-dupes on key (later value wins).
add_pref() {
  local kv="$1" key val existing kept
  key="${kv%%=*}"; val="${kv#*=}"
  case "$key" in
    enableDevHub)
      die "There is no 'enableDevHub' field. Use --enable (which sets $DEVHUB_SWITCH=true)." ;;
    "$DEVHUB_SWITCH")
      [ "$val" = "true" ] || die "$DEVHUB_SWITCH cannot be set to false because Dev Hub enablement is irreversible."
      ENABLING=1 ;;
    enable*) : ;;
    *) die "--pref key must be a DevHubSettings field starting with 'enable' (got: '$key')." ;;
  esac
  case "$val" in
    true|false) : ;;
    *) die "--pref value must be true or false (got: '$key=$val')." ;;
  esac
  kept=()
  for existing in "${PREFS[@]:-}"; do
    [ -n "$existing" ] || continue
    [ "${existing%%=*}" = "$key" ] && continue
    kept+=("$existing")
  done
  kept+=("$key=$val")
  PREFS=("${kept[@]}")
}

# --- argument parsing ----------------------------------------------------
while [ $# -gt 0 ]; do
  case "$1" in
    --allocation|-A)      set_mode allocation; shift ;;
    --show-settings|-s)   set_mode settings; shift ;;
    --list-scratch|-l)    set_mode list; shift ;;
    --list-orgs)          set_mode listorgs; shift ;;
    --enable|-e)          ENABLING=1; set_mode deploy; shift ;;
    --configure|-c)       set_mode deploy; shift ;;
    --packaging)          add_pref "enablePackaging2=true"; set_mode deploy; shift ;;
    --snapshots)          add_pref "enableScratchOrgSnapshotPref=true"; set_mode deploy; shift ;;
    --shape)              add_pref "enableShapeExportPref=true"; set_mode deploy; shift ;;
    --scratch-management) add_pref "$DEVHUB_SWITCH=true"; set_mode deploy; shift ;;
    --pref)
      shift
      [ $# -gt 0 ] || die "--pref requires a KEY=VALUE argument (e.g. --pref enablePackaging2=true)."
      case "$1" in *=*) : ;; *) die "--pref expects KEY=VALUE (got: '$1')." ;; esac
      add_pref "$1"; set_mode deploy; shift ;;
    --pref=*)
      kv="${1#*=}"
      case "$kv" in *=*) : ;; *) die "--pref expects KEY=VALUE (got: '$kv')." ;; esac
      add_pref "$kv"; set_mode deploy; shift ;;
    --apply)              APPLY=1; shift ;;
    --json)               OUTPUT="json"; shift ;;
    --fail-if-disabled)   FAIL_IF_DISABLED=1; shift ;;
    --help|-h)            usage; exit 0 ;;
    --)                   shift; break ;;
    -*)                   die "Unknown option: $1 (try --help)" ;;
    *)
      [ -n "$TARGET" ] && die "Specify only one org. Got extra: $1"
      TARGET="$1"; TARGET_EXPLICIT=1; shift ;;
  esac
done

# --enable always includes the master switch.
if [ "$ENABLING" -eq 1 ] && ! has_pref_key "$DEVHUB_SWITCH"; then
  add_pref "$DEVHUB_SWITCH=true"
fi

if [ "$MODE" = "deploy" ] && [ "${#PREFS[@]}" -eq 0 ]; then
  die "--configure needs at least one preference (e.g. --packaging, --snapshots, or --pref KEY=VALUE). To enable Dev Hub, use --enable."
fi

if [ "$APPLY" -eq 1 ] && [ "$MODE" != "deploy" ]; then
  die "--apply is valid only with --enable, --configure, or a preference flag."
fi

if [ "$APPLY" -eq 1 ] && [ "$TARGET_EXPLICIT" -ne 1 ]; then
  die "--apply requires an explicit org alias or username; refusing to mutate an implicit default org."
fi

# Bound one Salesforce CLI call. `sf org list` can wait on a keychain or
# network prompt longer than the eval harness tool timeout, and the agent
# then stops before it writes report.md. A parent-side wait is used because
# an alarm set before exec is not reliable on every platform.
sf_bounded() {
  local out_file pid i
  out_file="$(mktemp)"
  sf "$@" >"$out_file" 2>/dev/null &
  pid=$!
  i=0
  while [ "$i" -lt 20 ]; do
    if ! kill -0 "$pid" 2>/dev/null; then
      wait "$pid"
      local rc=$?
      cat "$out_file"
      rm -f "$out_file"
      return "$rc"
    fi
    sleep 1
    i=$((i + 1))
  done
  kill "$pid" 2>/dev/null || true
  pkill -P "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  rm -f "$out_file"
  return 142
}

# --- org discovery -------------------------------------------------------
# List the orgs authenticated with the Salesforce CLI. Handles both the newer
# {result:{nonScratchOrgs,scratchOrgs}} shape and the older {result:[...]}.
list_orgs() {
  local out
  out="$(sf_bounded org list --json 2>/dev/null)" || { echo "Could not list authenticated orgs (is the Salesforce CLI installed and working?)." >&2; return 1; }
  local norm
  norm="$(printf '%s' "$out" | jq -c '
    [ ((.result.nonScratchOrgs // []) + (.result.scratchOrgs // []) + (.result.other // []) +
       (if (.result|type)=="array" then .result else [] end))[]
      | {alias:(.alias // null), username:(.username // null),
         connectedStatus:(.connectedStatus // .status // null),
         isDefault:((.isDefaultUsername // .isDefault) // false)} ]' 2>/dev/null)"
  if [ "$OUTPUT" = "json" ]; then
    printf '%s\n' "${norm:-[]}"
    return 0
  fi
  local n
  n="$(printf '%s' "${norm:-[]}" | jq 'length' 2>/dev/null)"
  if [ -z "$n" ] || [ "$n" = "0" ]; then
    echo "No orgs are authenticated with the Salesforce CLI."
    echo "  Log in with:  sf org login web --alias <my-alias>"
    return 0
  fi
  echo "Authenticated orgs:"
  printf '%s' "$norm" | jq -r '.[]
    | "  \(.alias // .username // "?")\t\(.username // "?")\t\(.connectedStatus // "?")\(if .isDefault then "  (default)" else "" end)"' \
    | while IFS=$'\t' read -r a u s; do printf "  %-24s %-32s %s\n" "$a" "$u" "$s"; done
}

# --- org resolution ------------------------------------------------------
resolve_target() {
  [ -n "$TARGET" ] && return 0
  TARGET="$(sf config get target-org --json 2>/dev/null | jq -r '.result[0].value // empty')"
  [ -n "$TARGET" ] && return 0
  TARGET="$(sf config get target-dev-hub --json 2>/dev/null | jq -r '.result[0].value // empty')"
  [ -n "$TARGET" ] && return 0
  echo "No org specified and no default target-org / target-dev-hub is set." >&2
  echo >&2
  if [ "$OUTPUT" != "json" ]; then
    list_orgs >&2 || true
    echo >&2
  fi
  echo "Pass an org alias/username, or set a default:" >&2
  echo "    sf org login web --alias <my-alias>      # authenticate an org" >&2
  echo "    sf config set target-org <my-alias>      # make it the default" >&2
  exit 2
}

# Render one dynamic value as a safe, copy-pasteable shell argument.
shell_quote() {
  printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"
}

# --- Dev Hub detection ---------------------------------------------------
# Sets DEVHUB_STATE (+ SCRATCH_COUNT when enabled, or error fields on failure).
# ScratchOrgInfo is queryable ONLY on a Dev Hub, so a clean COUNT == enabled and
# INVALID_TYPE == not enabled; any other failure is treated as an auth/conn error.
detect_devhub() {
  local out rc
  out="$(sf data query --query "SELECT COUNT() FROM ScratchOrgInfo" \
          --target-org "$TARGET" --json 2>/dev/null)"
  rc=$?
  if [ "$rc" -eq 0 ]; then
    DEVHUB_STATE="enabled"
    SCRATCH_COUNT="$(printf '%s' "$out" | jq -r '.result.totalSize // empty')"
    return 0
  fi
  local ename emsg
  ename="$(printf '%s' "$out" | jq -r '.name // empty' 2>/dev/null)"
  emsg="$(printf '%s' "$out" | jq -r '.message // empty' 2>/dev/null | tr '\t\n' '  ')"
  case "$ename" in
    INVALID_TYPE)
      DEVHUB_STATE="disabled"; return 0 ;;
    *)
      DEVHUB_STATE="auth_error"; DEVHUB_ERRNAME="$ename"; DEVHUB_ERRMSG="$emsg"; return 1 ;;
  esac
}

# --- org facts (edition / sandbox) ---------------------------------------
# Best effort: populate ORG_EDITION, ORG_IS_SANDBOX. Never aborts.
org_facts() {
  [ "$ORG_FACTS_DONE" -eq 1 ] && return 0
  ORG_FACTS_DONE=1
  local out
  out="$(sf data query --query "SELECT OrganizationType, IsSandbox FROM Organization" \
          --target-org "$TARGET" --json 2>/dev/null)" || return 0
  ORG_EDITION="$(printf '%s' "$out" | jq -r '.result.records[0].OrganizationType // empty' 2>/dev/null)"
  # Use an explicit null-check rather than `// empty`: IsSandbox is a boolean, and
  # `false // empty` would drop a legitimate `false`, reporting a non-sandbox org
  # as "unknown" (isSandbox:null) instead of false.
  ORG_IS_SANDBOX="$(printf '%s' "$out" | jq -r '(.result.records[0].IsSandbox) as $s | if $s==null then empty else ($s|tostring) end' 2>/dev/null)"
  return 0
}

# --- DevHubSettings preferences read -------------------------------------
# Reads the current DevHubSettings via the Tooling API and echoes TSV rows
# "key<TAB>true|false" for each enable* preference. Returns non-zero on failure.
read_devhub_settings() {
  local out
  out="$(sf api request rest "/services/data/v${SETTINGS_API_VERSION}/tooling/sobjects/DevHubSettings/DevHub" \
          --target-org "$TARGET" --json 2>/dev/null)" || return 1
  # `sf api request rest --json` returns the raw REST body; be robust to a
  # possible {result:{...}} wrapper too.
  printf '%s' "$out" | jq -r '
    (.Metadata // .result.Metadata // {})
    | to_entries[]? | select(.key|startswith("enable"))
    | [.key, (.value|tostring)] | @tsv' 2>/dev/null
}

render_settings() {
  local rows
  rows="$(read_devhub_settings)"
  if [ -z "$rows" ]; then
    if [ "$OUTPUT" = "json" ]; then
      jq -n --arg org "$TARGET" '{org:$org, settings:{}, note:"Could not read DevHubSettings (Dev Hub may be off, or you lack access)."}'
    else
      echo "Could not read DevHubSettings for '$TARGET' — Dev Hub may be off, or you may lack access." >&2
    fi
    return 1
  fi
  if [ "$OUTPUT" = "json" ]; then
    printf '%s\n' "$rows" | jq -R -s --arg org "$TARGET" '
      {org:$org,
       settings:( [ split("\n")[] | select(length>0) | split("\t") | {(.[0]): (.[1]=="true")} ] | add // {} )}'
    return 0
  fi
  echo "DevHub preferences for '$TARGET':"
  printf '%s\n' "$rows" | while IFS=$'\t' read -r k v; do
    [ -n "$k" ] || continue
    if [ "$v" = "true" ]; then printf "  %-34s ON\n" "$k"; else printf "  %-34s OFF\n" "$k"; fi
  done
}

# Echoes TSV rows "name<TAB>remaining<TAB>max" for the two scratch org limits,
# or nothing if the org could not be queried.
allocation_rows() {
  local out
  out="$(sf org list limits --target-org "$TARGET" --json 2>/dev/null)" || return 1
  printf '%s' "$out" | jq -r '
    .result[]?
    | select(.name=="ActiveScratchOrgs" or .name=="DailyScratchOrgs")
    | [.name, (.remaining|tostring), (.max|tostring)] | @tsv'
}

# Integer percentage used = (max-rem)*100/max, or empty when max is empty/0.
pct_used() {
  local max="$1" rem="$2"
  { [ -n "$max" ] && [ "$max" -gt 0 ] 2>/dev/null; } || { echo ""; return; }
  echo $(( (max - rem) * 100 / max ))
}

# Resolve the org instance URL for the Setup deep link (best effort).
resolve_instance_url() {
  [ -n "$INSTANCE_URL" ] && return 0
  INSTANCE_URL="$(sf org display --target-org "$TARGET" --json 2>/dev/null \
    | jq -r '.result.instanceUrl // empty')"
}

# --- auth error reporting ------------------------------------------------
# Guidance only: print the exact login command to run. Never logs in.
print_auth_error() {
  if [ "$OUTPUT" = "json" ]; then
    jq -n --arg org "$TARGET" --arg name "$DEVHUB_ERRNAME" --arg msg "$DEVHUB_ERRMSG" \
      '{org:$org, devHubEnabled:null, status:"auth_error", error:{name:$name, message:$msg}}'
    return
  fi
  printf "  %-30s  could not query org (%s)\n" "$TARGET" "${DEVHUB_ERRNAME:-error}"
  [ -n "$DEVHUB_ERRMSG" ] && printf "  %-30s  (%s)\n" "" "$DEVHUB_ERRMSG"
  echo
  echo "  This org is not authenticated (or the session expired). Authentication is"
  echo "  a precondition for this skill — run one of these yourself, then re-run:"
  echo "    sf org login web --alias $(shell_quote "$TARGET")                                             # prod / DE / trial"
  echo "    sf org login web --alias <my-alias> --instance-url https://MYDOMAIN.my.salesforce.com   # sandbox / My Domain"
  echo "  List existing logins with:  sf org list"
}

# --- Setup UI fallback text ----------------------------------------------
print_ui_fallback() {
  resolve_instance_url
  echo "  Manual alternative (Setup UI):"
  echo "    1. Log in as a System Administrator."
  echo "    2. Setup > Quick Find > \"Dev Hub\" > Dev Hub > turn Enable Dev Hub On."
  if [ -n "$INSTANCE_URL" ]; then
    echo "    Open it directly: sf org open --path \"lightning/setup/DevHub/home\" --target-org \"$TARGET\""
  fi
}

# --- allocation rendering ------------------------------------------------
render_allocation() {
  local rows a_max a_rem d_max d_rem a_pct d_pct
  rows="$(allocation_rows)" || { echo "Could not read org limits for '$TARGET'." >&2; return 1; }
  a_rem="$(printf '%s\n' "$rows" | awk -F'\t' '$1=="ActiveScratchOrgs"{print $2}')"
  a_max="$(printf '%s\n' "$rows" | awk -F'\t' '$1=="ActiveScratchOrgs"{print $3}')"
  d_rem="$(printf '%s\n' "$rows" | awk -F'\t' '$1=="DailyScratchOrgs"{print $2}')"
  d_max="$(printf '%s\n' "$rows" | awk -F'\t' '$1=="DailyScratchOrgs"{print $3}')"
  a_pct="$(pct_used "$a_max" "$a_rem")"
  d_pct="$(pct_used "$d_max" "$d_rem")"

  if [ "$OUTPUT" = "json" ]; then
    local warns=()
    if [ -n "$a_max" ] && [ "$a_max" -gt 0 ] 2>/dev/null && [ "$a_rem" -lt 2 ] 2>/dev/null; then
      warns+=("only $a_rem active scratch org(s) remaining")
    fi
    { [ -n "$a_pct" ] && [ "$a_pct" -gt 80 ] 2>/dev/null; } && warns+=("Active scratch org usage at ${a_pct}%")
    { [ -n "$d_pct" ] && [ "$d_pct" -gt 80 ] 2>/dev/null; } && warns+=("Daily scratch org usage at ${d_pct}%")
    local warn_json="[]"
    if [ "${#warns[@]}" -gt 0 ]; then
      warn_json="$(printf '%s\n' "${warns[@]}" | jq -R . | jq -s .)"
    fi
    jq -n --arg org "$TARGET" \
      --argjson am "${a_max:-null}" --argjson ar "${a_rem:-null}" --argjson ap "${a_pct:-null}" \
      --argjson dm "${d_max:-null}" --argjson dr "${d_rem:-null}" --argjson dp "${d_pct:-null}" \
      --argjson warnings "$warn_json" '
      {org:$org,
       allocation:{
         activeScratchOrgs:{max:$am, remaining:$ar, used:(if $am!=null and $ar!=null then ($am-$ar) else null end), usedPct:$ap},
         dailyScratchOrgs:{max:$dm, remaining:$dr, used:(if $dm!=null and $dr!=null then ($dm-$dr) else null end), usedPct:$dp}
       },
       warnings:$warnings}'
    return 0
  fi

  echo "Scratch org allocation for '$TARGET':"
  if [ -z "$a_max" ] && [ -z "$d_max" ]; then
    echo "  No scratch org limits reported (org may not be a Dev Hub, or could not be queried)."
    return 0
  fi
  printf "  %-22s %10s %10s %10s\n" "Limit" "Used" "Remaining" "Max"
  [ -n "$a_max" ] && printf "  %-22s %10s %10s %10s\n" "Active scratch orgs" "$(( a_max - a_rem ))" "$a_rem" "$a_max"
  [ -n "$d_max" ] && printf "  %-22s %10s %10s %10s\n" "Daily scratch orgs" "$(( d_max - d_rem ))" "$d_rem" "$d_max"
  # Pre-flight warnings.
  if [ -n "$a_max" ] && [ "$a_max" -gt 0 ] 2>/dev/null && [ "$a_rem" -lt 2 ] 2>/dev/null; then
    echo "  WARN: only $a_rem active scratch org(s) remaining."
  fi
  { [ -n "$a_pct" ] && [ "$a_pct" -gt 80 ] 2>/dev/null; } && echo "  NOTE: Active scratch org usage at ${a_pct}% ($(( a_max - a_rem ))/$a_max)."
  { [ -n "$d_pct" ] && [ "$d_pct" -gt 80 ] 2>/dev/null; } && echo "  NOTE: Daily scratch org usage at ${d_pct}% ($(( d_max - d_rem ))/$d_max)."
  echo
  echo "  Active = orgs alive right now; Daily = successful creations in a rolling 24h window."
  echo "  Allocation is set by the Dev Hub's edition (e.g. Developer/trial 3 & 6;"
  echo "  Enterprise 40 & 80; Unlimited/Performance 100 & 200) plus any purchased add-on."
}

# --- active scratch org listing ------------------------------------------
render_list() {
  local out rc
  out="$(sf data query --target-org "$TARGET" \
      --query "SELECT SignupUsername, OrgName, Edition, ExpirationDate, ScratchOrg FROM ActiveScratchOrg ORDER BY ExpirationDate NULLS LAST" \
      --json 2>/dev/null)"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    if [ "$OUTPUT" = "json" ]; then echo "[]"; else
      echo "Could not list scratch orgs for '$TARGET' — is Dev Hub enabled and the org authenticated?" >&2
    fi
    return 1
  fi
  if [ "$OUTPUT" = "json" ]; then
    printf '%s' "$out" | jq '[.result.records[]? | {signupUsername:.SignupUsername, orgName:.OrgName, edition:.Edition, expirationDate:.ExpirationDate, scratchOrgId:.ScratchOrg}]'
    return 0
  fi
  local total
  total="$(printf '%s' "$out" | jq -r '.result.totalSize // 0')"
  echo "Active scratch orgs on Dev Hub '$TARGET': $total"
  if [ "$total" = "0" ]; then
    echo "  (none active)"
    return 0
  fi
  printf '%s' "$out" | jq -r '.result.records[]?
    | "  \(.SignupUsername // "?")  edition=\(.Edition // "?")  expires=\(.ExpirationDate // "?")  id=\(.ScratchOrg // "?")"'
}

# --- deploy (enable / configure sub-prefs) -------------------------------
DEPLOY_TEMP_DIR=""
cleanup_deploy_temp() {
  [ -n "$DEPLOY_TEMP_DIR" ] && rm -rf -- "$DEPLOY_TEMP_DIR"
}

render_deploy() {
  # Enabling Dev Hub cannot happen on a sandbox. When actually applying an
  # enablement, verify eligibility first and refuse before touching the org.
  if [ "$ENABLING" -eq 1 ] && [ "$APPLY" -eq 1 ]; then
    org_facts
    if [ "$ORG_IS_SANDBOX" = "true" ]; then
      if [ "$OUTPUT" = "json" ]; then
        jq -n --arg org "$TARGET" '{applied:false, enabling:true, success:false, message:"Refused: Dev Hub cannot be enabled on a sandbox. Use a production, Developer Edition, or trial org."}'
      else
        echo "Refused — '$TARGET' is a sandbox, and Dev Hub cannot be enabled on a sandbox."
        echo "  Dev Hub must be a production/business org (or a Developer Edition / trial org)."
        echo
        print_ui_fallback
      fi
      return 1
    fi
  fi

  # Sub-prefs (packaging, snapshots, shape) require Dev Hub to be on. If the
  # user is configuring one without also enabling, and Dev Hub is off, warn.
  if [ "$ENABLING" -eq 0 ] && [ "$DEVHUB_STATE" = "disabled" ] && [ "$OUTPUT" != "json" ]; then
    echo "Note: Dev Hub is not enabled on '$TARGET'. Sub-preferences require Dev Hub — add --enable, or run --enable first." >&2
    echo >&2
  fi

  local tmp
  tmp="$(mktemp -d 2>/dev/null)" || die "Could not create a temporary directory for the deploy."
  DEPLOY_TEMP_DIR="$tmp"
  trap cleanup_deploy_temp EXIT

  mkdir -p "$tmp/force-app/main/default/settings"
  cat > "$tmp/sfdx-project.json" <<JSON
{ "packageDirectories": [{ "path": "force-app", "default": true }], "sourceApiVersion": "$SETTINGS_API_VERSION" }
JSON
  {
    echo '<?xml version="1.0" encoding="UTF-8"?>'
    echo '<DevHubSettings xmlns="http://soap.sforce.com/2006/04/metadata">'
    local kv key val
    for kv in "${PREFS[@]}"; do
      key="${kv%%=*}"; val="${kv#*=}"
      echo "    <$key>$val</$key>"
    done
    echo '</DevHubSettings>'
  } > "$tmp/force-app/main/default/settings/DevHub.settings-meta.xml"

  local dry="--dry-run" action="Validating (dry run)"
  if [ "$APPLY" -eq 1 ]; then dry=""; action="Deploying"; fi

  if [ "$OUTPUT" != "json" ]; then
    if [ "$ENABLING" -eq 1 ]; then
      echo "$action Dev Hub enablement on '$TARGET':"
    else
      echo "$action DevHubSettings on '$TARGET':"
    fi
    local kv2; for kv2 in "${PREFS[@]}"; do echo "    $kv2"; done
    if [ "$ENABLING" -eq 1 ] && [ "$APPLY" -eq 1 ]; then
      echo
      echo "  WARNING: enabling Dev Hub is IRREVERSIBLE — it cannot be turned off."
      echo "  Requires ModifyAllData or ModifyMetadata (System Administrator)."
      echo "  Not allowed in a sandbox, or in an org with a registered namespace."
    fi
    echo
  fi

  local out ok verified="unknown"
  out="$( cd "$tmp" && sf project deploy start $dry --source-dir force-app \
            --target-org "$TARGET" --json 2>/dev/null )"
  ok="$(printf '%s' "$out" | jq -r '.result.success // false')"

  # On a real, successful enablement, re-detect so we report verified state.
  if [ "$APPLY" -eq 1 ] && [ "$ENABLING" -eq 1 ] && [ "$ok" = "true" ]; then
    detect_devhub >/dev/null 2>&1
    verified="$DEVHUB_STATE"
  fi

  if [ "$OUTPUT" = "json" ]; then
    printf '%s' "$out" | jq \
      --arg applied "$([ "$APPLY" -eq 1 ] && echo true || echo false)" \
      --arg enabling "$([ "$ENABLING" -eq 1 ] && echo true || echo false)" \
      --arg verified "$verified" '
      {applied:($applied=="true"),
       enabling:($enabling=="true"),
       success:(.result.success // false),
       checkOnly:(.result.checkOnly // null),
       devHubVerifiedState:(if $verified=="unknown" then null else $verified end),
       failures:[.result.details.componentFailures[]? | {fullName, problem}],
       message:(.message // null)}'
    [ "$ok" = "true" ] && return 0 || return 1
  fi

  if [ "$ok" = "true" ]; then
    if [ "$APPLY" -eq 1 ]; then
      if [ "$ENABLING" -eq 1 ]; then
        echo "  Success — Dev Hub enabled (deploy succeeded)."
        if [ "$verified" = "enabled" ]; then
          echo "  Verified: ScratchOrgInfo is now queryable."
        else
          echo "  Note: provisioning may take a moment; re-run 'devhub.sh \"$TARGET\"' to confirm."
        fi
        echo "  Set it as your default Dev Hub:  sf config set target-dev-hub \"$TARGET\""
      else
        echo "  Success — Dev Hub preferences deployed."
      fi
    else
      echo "  Dry run passed — valid. Re-run with --apply to deploy."
      [ "$ENABLING" -eq 1 ] && echo "  (Enabling Dev Hub is irreversible; --apply commits it.)"
    fi
    return 0
  fi

  echo "  Deployment did not succeed:"
  printf '%s' "$out" | jq -r '.result.details.componentFailures[]? | "    - \(.fullName): \(.problem)"' 2>/dev/null
  printf '%s' "$out" | jq -r '.message // empty' 2>/dev/null | sed 's/^/    /'
  # Common cause: missing perms. Offer the UI route.
  if printf '%s' "$out" | grep -qi "INSUFFICIENT_ACCESS\|ModifyAllData\|ModifyMetadata"; then
    echo
    echo "  This looks like a permissions issue — the deploy needs ModifyAllData or ModifyMetadata."
    [ "$ENABLING" -eq 1 ] && print_ui_fallback
  fi
  return 1
}

# --- status (default) ----------------------------------------------------
render_status() {
  if [ "$OUTPUT" = "json" ]; then
    local rows a_max a_rem d_max d_rem
    rows="$(allocation_rows 2>/dev/null || true)"
    a_rem="$(printf '%s\n' "$rows" | awk -F'\t' '$1=="ActiveScratchOrgs"{print $2}')"
    a_max="$(printf '%s\n' "$rows" | awk -F'\t' '$1=="ActiveScratchOrgs"{print $3}')"
    d_rem="$(printf '%s\n' "$rows" | awk -F'\t' '$1=="DailyScratchOrgs"{print $2}')"
    d_max="$(printf '%s\n' "$rows" | awk -F'\t' '$1=="DailyScratchOrgs"{print $3}')"
    org_facts
    jq -n --arg org "$TARGET" --arg state "$DEVHUB_STATE" \
      --argjson count "${SCRATCH_COUNT:-null}" \
      --arg edition "${ORG_EDITION}" --arg sandbox "${ORG_IS_SANDBOX}" \
      --argjson am "${a_max:-null}" --argjson ar "${a_rem:-null}" \
      --argjson dm "${d_max:-null}" --argjson dr "${d_rem:-null}" '
      {org:$org,
       devHubEnabled:($state=="enabled"),
       status:$state,
       edition:(if $edition=="" then null else $edition end),
       isSandbox:(if $sandbox=="" then null else ($sandbox=="true") end),
       activeScratchOrgSignups:$count,
       allocation:{
         activeScratchOrgs:{max:$am, remaining:$ar},
         dailyScratchOrgs:{max:$dm, remaining:$dr}
       }}'
    return 0
  fi

  org_facts
  echo "Dev Hub status for '$TARGET':"
  if [ "$DEVHUB_STATE" = "enabled" ]; then
    echo "  Dev Hub: ENABLED  (ScratchOrgInfo is queryable)"
    echo "  Detection: ScratchOrgInfo is queryable only when Dev Hub is on. A successful count means ENABLED. An INVALID_TYPE error means NOT ENABLED. Scratch org limits are not used as the enablement check."
    [ -n "$ORG_EDITION" ] && echo "  Edition: $ORG_EDITION"
    [ "$ORG_IS_SANDBOX" = "true" ] && echo "  (Sandbox org)"
    [ -n "$SCRATCH_COUNT" ] && echo "  Scratch org signup records: $SCRATCH_COUNT"
    # Best-effort current-preference summary; never let it break status.
    local prefs
    prefs="$(read_devhub_settings 2>/dev/null | awk -F'\t' '$2=="true"{printf "%s ", $1}')"
    [ -n "$prefs" ] && echo "  Enabled preferences: $prefs"
    echo
    render_allocation
  else
    echo "  Dev Hub: NOT ENABLED"
    echo "  Detection: ScratchOrgInfo is queryable only when Dev Hub is on. A successful count means ENABLED. An INVALID_TYPE error means NOT ENABLED. Scratch org limits are not used, because they are reported even when Dev Hub is off."
    [ -n "$ORG_EDITION" ] && echo "  Edition: $ORG_EDITION"
    [ "$ORG_IS_SANDBOX" = "true" ] && echo "  (Sandbox org — cannot host Dev Hub)"
    echo
    echo "  Scratch org allocation, Dev Hub preferences, and the scratch org list are not available until Dev Hub is enabled. An empty allocation or a failed exit from those modes means Dev Hub is off, not that the org is unauthenticated."
    echo
    if [ "$ORG_IS_SANDBOX" = "true" ]; then
      echo "  This is a sandbox — Dev Hub cannot be enabled here. Use a production,"
      echo "  Developer Edition, or trial org instead."
      echo
    else
      echo "  Enable it (deploys $DEVHUB_SWITCH=true; irreversible):"
      echo "    devhub.sh \"$TARGET\" --enable            # validate first (dry run)"
      echo "    devhub.sh \"$TARGET\" --enable --apply    # actually enable"
      echo "  Requires ModifyAllData or ModifyMetadata (System Administrator);"
      echo "  not allowed in a sandbox or an org with a registered namespace."
      echo
    fi
    print_ui_fallback
  fi
}

# --- dispatch ------------------------------------------------------------
# --list-orgs needs no target and no auth check — handle it first.
if [ "$MODE" = "listorgs" ]; then
  list_orgs; exit $?
fi

resolve_target

# status/deploy/settings need the enablement state; allocation and list query
# the org directly and surface their own errors.
case "$MODE" in
  status|deploy|settings)
    if ! detect_devhub && [ "$DEVHUB_STATE" = "auth_error" ]; then
      print_auth_error
      exit 1
    fi
    ;;
esac

# --show-settings requires Dev Hub to be on.
if [ "$MODE" = "settings" ] && [ "$DEVHUB_STATE" != "enabled" ]; then
  if [ "$OUTPUT" = "json" ]; then
    jq -n --arg org "$TARGET" '{org:$org, settings:{}, note:"Dev Hub is not enabled; there are no DevHubSettings to read."}'
  else
    echo "Dev Hub is not enabled on '$TARGET' — there are no DevHubSettings to read." >&2
    echo "  Packaging (enablePackaging2), org shape export (enableShapeExportPref), and scratch org snapshots (enableScratchOrgSnapshotPref) cannot be read until Dev Hub is enabled. Do not guess ON or OFF." >&2
    echo "  Validate with a dry run first. Enabling is irreversible and needs a System Administrator (ModifyAllData or ModifyMetadata)." >&2
    echo "  Enable it first with:  devhub.sh \"$TARGET\" --enable --apply" >&2
  fi
  exit 1
fi

rc=0
case "$MODE" in
  status)     render_status || rc=1 ;;
  allocation) render_allocation || rc=1 ;;
  settings)   render_settings || rc=1 ;;
  list)       render_list || rc=1 ;;
  deploy)     render_deploy || rc=1 ;;
esac

# CI gate: exit 3 if Dev Hub is not enabled (takes precedence for alerting).
if [ "$FAIL_IF_DISABLED" -eq 1 ]; then
  [ -z "$DEVHUB_STATE" ] && detect_devhub >/dev/null 2>&1
  if [ "$DEVHUB_STATE" != "enabled" ]; then
    echo "ALERT: Dev Hub is not enabled on '$TARGET'." >&2
    exit 3
  fi
fi

exit "$rc"
