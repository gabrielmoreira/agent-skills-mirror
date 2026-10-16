#!/usr/bin/env bash
# Lists the DevOps Center environments of a source org and resolves an optional
# identifier (alias, username, My Domain URL, 15/18-char org id, or environment name)
# to one of them. Read-only. Prints one JSON document on stdout.
#
# Usage: resolve-environment.sh <source-org-alias> [identifier] [--rows-file <file>]
#   --rows-file  read the DevopsEnvironment query result JSON from a file (tests)
#
# Exit codes: 0 ok (check .match / .matchStatus), 1 usage or call error.
set -uo pipefail

command -v jq >/dev/null || { echo "jq required" >&2; exit 1; }
SRC="${1:-}"
[ -n "$SRC" ] || { echo "usage: resolve-environment.sh <source-org-alias> [identifier] [--rows-file <file>]" >&2; exit 1; }
shift
IDENT=""; ROWS_FILE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --rows-file) [ $# -ge 2 ] || { echo "--rows-file needs a value" >&2; exit 1; }; ROWS_FILE="$2"; shift 2 ;;
    *) IDENT="$1"; shift ;;
  esac
done

sfj() { env FORCE_COLOR=0 SF_CLI_DISABLE_AUTOUPDATE=true "$@" 2>/dev/null; }

# Source org (the org the user built in).
src_json=$(sfj sf org display --target-org "$SRC" --json) \
  || { echo "cannot read source org '$SRC'" >&2; exit 1; }
source_obj=$(printf '%s' "$src_json" | jq -c --arg a "$SRC" \
  '{alias:$a, username:.result.username, orgId:.result.id, instanceUrl:.result.instanceUrl}')

# DevopsEnvironment rows.
if [ -n "$ROWS_FILE" ]; then
  rows_json=$(cat "$ROWS_FILE")
else
  rows_json=$(sfj sf data query --target-org "$SRC" --json --query \
    "SELECT Id, Name, NamedCredential, OrgType, IsExpired, OrgUrl, OrgIdentifier FROM DevopsEnvironment ORDER BY Name") \
    || {
      # sf prints its JSON error on stdout; tell "not enabled" apart from an expired session or other failure.
      qmsg=$(printf '%s' "$rows_json" | jq -r '[.name, .message] | map(select(. != null)) | join(": ")' 2>/dev/null)
      case "$qmsg" in
        *INVALID_TYPE*|*"sObject type"*|*"not supported"*|*INSUFFICIENT_ACCESS*)
          echo "DevOps Center not enabled or no access: DevopsEnvironment is unavailable ($qmsg)" >&2 ;;
        *) echo "DevopsEnvironment query failed, not an enablement problem: ${qmsg:-unknown error}" >&2 ;;
      esac
      exit 1
    }
fi
printf '%s' "$rows_json" | jq -e '.result.records' >/dev/null 2>&1 \
  || { echo "unexpected query result" >&2; exit 1; }

# Identifier -> comparable keys: org id (first 15), host, and a lowercase name.
# Local alias or username: expand through `sf org display` to its org id and host.
id15=""; host=""; name=""
if [ -n "$IDENT" ]; then
  if printf '%s' "$IDENT" | grep -Eq '^00D[A-Za-z0-9]{12}([A-Za-z0-9]{3})?$'; then
    id15="${IDENT:0:15}"
  elif printf '%s' "$IDENT" | grep -Eiq '^https?://' \
       || printf '%s' "$IDENT" | grep -Eiq '^[A-Za-z0-9.-]+\.(salesforce\.com|salesforce-setup\.com|force\.com|pc-rnd\.salesforce\.com)(/.*)?$'; then
    host=$(printf '%s' "$IDENT" | sed -E 's#^[Hh][Tt][Tt][Pp][Ss]?://##; s#[/?].*$##' | tr 'A-Z' 'a-z')
  else
    # Environment name, alias, or username. An authorized alias also yields an org id and host.
    name=$(printf '%s' "$IDENT" | tr 'A-Z' 'a-z')
    exp=$(sfj sf org display --target-org "$IDENT" --json) && {
      id15=$(printf '%s' "$exp" | jq -r '.result.id // empty | .[0:15]')
      host=$(printf '%s' "$exp" | jq -r '.result.instanceUrl // empty' | sed -E 's#^https?://##')
      # A resolved org is matched by identity only: an environment that merely shares its name is another org.
      [ -n "$id15" ] && name=""
    }
  fi
fi

jq -n \
  --argjson source "$source_obj" \
  --argjson rows "$rows_json" \
  --arg ident "$IDENT" --arg id15 "$id15" --arg host "$host" --arg name "$name" '
  # setup and lightning hosts point at the same org as the My Domain host
  def norm: ascii_downcase | sub("^https?://"; "") | sub("[/?].*$"; "")
            | sub("\\.salesforce-setup\\.com$"; ".salesforce.com")
            | sub("\\.lightning\\.force\\.com$"; ".my.salesforce.com");
  # expired = retired or replaced by an environment swap (not an OAuth expiry).
  # unauthenticated = connect never finished: the PATCH fills OrgUrl and OrgIdentifier.
  # The DevOps Center hub row is created with only the fixed hub NC (no OrgUrl) and is the control
  # plane, not a deploy target, so it is dropped before listing or matching (also by its fixed
  # name while it has no OrgUrl, in case its credential was removed).
  # NamedCredential is plain text in the API; strip an <a> wrapper in case a UI layer added one.
  def ncname: ((.NamedCredential // "") | gsub("<[^>]*>"; "") | gsub("^\\s+|\\s+$"; ""));
  def state: if (.IsExpired == true) then "expired"
             elif ((ncname == "") or (.OrgUrl // "") == "" or (.OrgIdentifier // "") == "") then "unauthenticated"
             else "selectable" end;
  [ ($rows.result.records // [])[] | select(ncname != "ALMDevOpsCenterHub" and ((.Name // "") != "Doce Hub Environment" or (.OrgUrl // "") != "")) ] as $recs
  | ($host | if . == "" then "" else norm end) as $h
  | [ $recs[] | {
        id: .Id, name: .Name, orgType: .OrgType,
        orgUrl: (.OrgUrl // null),
        orgId: (.OrgIdentifier // null),
        namedCredential: (ncname | if . == "" then null else . end),
        state: state,
        isSource: ((.OrgIdentifier // "")[0:15] == ($source.orgId // "")[0:15] and (.OrgIdentifier // "") != "")
    } ] as $envs
  | ( if $ident == "" then []
      else [ $envs[] | select(
               ($id15 != "" and ((.orgId // "")[0:15] == $id15))
            or ($h != "" and ((.orgUrl // "") != "") and ((.orgUrl | norm) == $h))
            or ($name != "" and ((.name | ascii_downcase) == $name))) ]
      end ) as $m
  | { source: $source,
      environments: $envs,
      identifier: $ident,
      matchStatus: ( if $ident == "" then "none-requested"
                     elif ($m | length) == 0 then "not-connected"
                     elif ($m | length) > 1 then "ambiguous"
                     else "matched" end ),
      matches: $m,
      match: (if ($m | length) == 1 then $m[0] else null end),
      sourceMatched: ( $ident != "" and
        ( ($id15 != "" and $id15 == ($source.orgId // "")[0:15])
       or ($h != "" and (($source.instanceUrl // "") | norm) == $h)
       or ($name != "" and $name == ($source.alias | ascii_downcase))
       or (($m | length) == 1 and $m[0].isSource) ) ) }'
