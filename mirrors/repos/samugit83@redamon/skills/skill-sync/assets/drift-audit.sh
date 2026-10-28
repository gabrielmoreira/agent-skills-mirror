#!/usr/bin/env bash
#
# drift-audit.sh - detection, no model. For every path cited by every SKILL.md
# AND every AGENTS.md, check the path still resolves. Prints the dead ones.
#
# AGENTS.md citations matter MORE than skill citations: an AGENTS.md is always
# in context, so a stale path there misleads every agent on every task. They
# are reported first and flagged [AGENTS].
#
# Flags:
#     --skill <name>   audit only skills/<name>/SKILL.md
#     --docs           audit every prose doc with the stricter DOCS MODE rules
#                      below: docs/readmes/**/*.md, README.md, CONTRIBUTING.md,
#                      the SKILL.md and AGENTS.md files, and the wiki checkout's
#                      pages (its two generated pages excepted).
#
# Exit: 0 when every citation resolves, 1 when any is dead (so cron/CI can tell).
#
# ---------------------------------------------------------------------------
# CONFIGURE HERE: component roots, relative to the repository root. Skills cite
# paths relative to a COMPONENT root, not the repo root, so a backticked path
# counts as live if it resolves under the citing file's own dir, the repo root,
# OR any root below. A markdown link must resolve from the citing file's dir.
# Leave this wrong and the audit floods with false positives.
# ---------------------------------------------------------------------------
ROOTS=(
  "."                    # repository root
  "webapp"               # scope: webapp
  "agentic"              # scope: agentic
  "recon"                # scope: recon
  "recon_orchestrator"   # scope: recon_orchestrator
  "scanners/capture_proxy"        # scope: capture_proxy
  "scanners/supply_chain_scan"    # scope: supply_chain (dir)
  "scanners/supply_chain_common"  # supply_chain shared lib
  "scanners/supply_chain_analyzer" # supply_chain analyzer
)
# ---------------------------------------------------------------------------

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || (cd "$SCRIPT_DIR/../../.." && pwd))"

ONLY_SKILL=""
DOCS=0
while [ $# -gt 0 ]; do
  case "$1" in
    --skill) shift; ONLY_SKILL="${1:-}" ;;
    --docs) DOCS=1 ;;
    -h|--help) sed -n '2,17p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "drift-audit.sh: unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

WIKI_DIR="redamon.wiki"
# Generated from code (section 3.1 of docs/readmes/README.DRIFT_MAP.md); their
# own generators' byte-compare tests own them.
WIKI_GENERATED=("MCP-API-Reference.md" "Project-Settings-Registry.md")

# --- files to audit --------------------------------------------------------
FILES=()
if [ "$DOCS" -eq 1 ]; then
  while IFS= read -r d; do
    [ -n "$d" ] && FILES+=("$REPO_ROOT/$d")
  done < <(git -C "$REPO_ROOT" ls-files --cached --others --exclude-standard \
             -- 'docs/readmes/*.md' README.md CONTRIBUTING.md 'skills/*/SKILL.md' 2>/dev/null)
  while IFS= read -r a; do
    [ -n "$a" ] && [ "$(basename "$a")" = "AGENTS.md" ] && FILES+=("$REPO_ROOT/$a")
  done < <(git -C "$REPO_ROOT" ls-files --cached --others --exclude-standard '*AGENTS.md' 2>/dev/null)
  if [ -f "$REPO_ROOT/$WIKI_DIR/Home.md" ]; then
    while IFS= read -r w; do
      [ -n "$w" ] || continue
      for g in "${WIKI_GENERATED[@]}"; do [ "$w" = "$g" ] && continue 2; done
      FILES+=("$REPO_ROOT/$WIKI_DIR/$w")
    done < <(git -C "$REPO_ROOT/$WIKI_DIR" ls-files --cached --others --exclude-standard \
               -- '*.md' 2>/dev/null)
  else
    echo "drift-audit: no wiki checkout at $WIKI_DIR/ (no Home.md); wiki pages not audited." >&2
  fi
elif [ -n "$ONLY_SKILL" ]; then
  f="$REPO_ROOT/skills/$ONLY_SKILL/SKILL.md"
  [ -f "$f" ] || { echo "no such skill: skills/$ONLY_SKILL/SKILL.md" >&2; exit 2; }
  FILES=("$f")
else
  shopt -s nullglob
  for f in "$REPO_ROOT"/skills/*/SKILL.md; do FILES+=("$f"); done
  # every AGENTS.md tracked in the repo (basename must be exactly AGENTS.md:
  # git's '*' spans '/', so '*AGENTS.md' would also match README.FOO_AGENTS.md)
  while IFS= read -r a; do
    [ -n "$a" ] && [ "$(basename "$a")" = "AGENTS.md" ] && FILES+=("$REPO_ROOT/$a")
  done < <(git -C "$REPO_ROOT" ls-files --cached --others --exclude-standard '*AGENTS.md' 2>/dev/null)
fi

# --- extract citations from one file --------------------------------------
# Emits "<origin><TAB><token>": origin L = markdown link ](target) (an explicit
# citation, always audited); origin B = backticked token (audited only if it is
# path-shaped, i.e. contains a "/", so bare identifiers in prose like `.py` or
# `sync.sh` are not mistaken for dead paths).
extract_citations() {
  awk '
    {
      line=$0
      s=line
      while (match(s, /\]\([^)]+\)/)) {
        print "L\t" substr(s, RSTART+2, RLENGTH-3)
        s=substr(s, RSTART+RLENGTH)
      }
      s=line
      while (match(s, /`[^`]+`/)) {
        print "B\t" substr(s, RSTART+1, RLENGTH-2)
        s=substr(s, RSTART+RLENGTH)
      }
    }
  ' "$1"
}

# does a candidate look like a repo path we can check? $1 token, $2 origin (L/B)
is_path_like() {
  case "$1" in
    http://*|https://*|mailto:*|\#*) return 1 ;;         # urls / anchors
    /*) return 1 ;;                                       # absolute -> HTTP endpoint (/defaults) or abs path, not a repo citation
    *" "*) return 1 ;;                                    # has a space -> prose/command
    *[{}\<\>\*\$,]*) return 1 ;;                          # placeholder/brace/glob -> illustrative, not a real path
    *:*) return 1 ;;                                      # colon -> volume spec (host:container), host:port, not a repo path
  esac
  # backticked tokens must be path-shaped (contain a slash); links are explicit.
  if [ "$2" = "B" ]; then
    case "$1" in */*) : ;; *) return 1 ;; esac
  fi
  return 0
}

# resolve a candidate against the citing file's dir, then every ROOT, then repo
# root. $3 is the origin: a markdown link (L) resolves against the citing file's
# dir only, because that is where a renderer sends the click; trying the roots
# made [AGENTS.md](../AGENTS.md) in skills/<name>/SKILL.md pass via
# webapp/../AGENTS.md although skills/AGENTS.md does not exist. Only the full
# cited path is tried, never its basename: a basename match is a different file.
resolves() {
  local cand="$1" fdir="$2" origin="$3" p="${1%%#*}"   # strip a trailing #anchor
  p="${p%\)}"                                     # stray close paren
  [ -n "$p" ] || return 0
  [ -e "$fdir/$p" ] && return 0
  [ "$origin" = "L" ] && return 1
  local r base
  for r in "${ROOTS[@]}"; do
    if [ "$r" = "." ]; then base="$REPO_ROOT"; else base="$REPO_ROOT/$r"; fi
    [ -e "$base/$p" ] && return 0
  done
  [ -e "$REPO_ROOT/$p" ] && return 0
  return 1
}

# --- DOCS MODE ---------------------------------------------------------------
# Prose docs hold far more backticked tokens with a "/" that are not repo paths
# (MIME types, model prefixes, workspace folders, paths on a target), and their
# citations rot differently, so --docs swaps in its own extraction and
# resolution; the default audit below (no --docs) is unchanged:
#   - fenced code blocks are skipped (example code, file-tree diagrams);
#   - `path:12` and `path::TestX` cite `path`;
#   - links to https://github.com/samugit83/redamon/{blob,tree}/<ref>/<path>
#     are repo citations too (origin G, resolved from the repo root);
#   - "exists" means git would commit it (tracked, or new and not ignored),
#     see known_paths;
#   - a backticked token is a path only if its first segment exists in the
#     citing dir, the repo root or a ROOT: `recon/port_scan.py` is audited,
#     `notes/`, `bedrock/` or `nginx/1.25` are not. A token starting with ".."
#     is a payload or shell context, never a citation;
#   - anything under _local/ is dead even where it exists: it is the
#     maintainer's private, gitignored folder, so no reader has it;
#   - a path git ignores (a runtime output or cache) is skipped, not reported;
#   - a token with [brackets] that does not resolve is a placeholder (`[tool].py`);
#     one that does is a real Next.js route folder;
#   - in wiki pages, extension-less links (wiki page links) and image embeds
#     are left to tests/test_docs_not_stale.py, which checks pages and images.
DOCS_EXCLUDE=(
  "docs/readmes/README.DRIFT_MAP.md"              # quotes dead paths as its evidence
  "docs/readmes/skills_management/templates/*"    # example paths of an imaginary project
  "$WIKI_DIR/xbench_sessions/*"                   # agent session exports: paths on the targets
  "$WIKI_DIR/hacklab/*"                           # agent session exports: paths on the targets
  "$WIKI_DIR/xbow-patches/*"                      # about the external validation-benchmarks repo
)

# Origins: B backtick, L link, I image embed, G GitHub URL into this repo.
extract_doc_citations() {
  awk '
    /^[ \t]*(```|~~~)/ { fence = !fence; next }
    fence { next }
    {
      t = $0
      while (match(t, /!\[[^]]*\]\([^)]+\)/)) {
        img = substr(t, RSTART, RLENGTH)
        sub(/^!\[[^]]*\]\(/, "", img); sub(/\)$/, "", img)
        print "I\t" img
        t = substr(t, 1, RSTART-1) substr(t, RSTART+RLENGTH)
      }
      s = t
      while (match(s, /\]\([^)]+\)/)) {
        tgt = substr(s, RSTART+2, RLENGTH-3)
        sub(/[ \t]+".*$/, "", tgt)
        gsub(/^<|>$/, "", tgt)
        if (tgt ~ /^https:\/\/github\.com\/samugit83\/redamon\/(blob|tree)\/[^\/]+\//) {
          sub(/^https:\/\/github\.com\/samugit83\/redamon\/(blob|tree)\/[^\/]+\//, "", tgt)
          print "G\t" tgt
        } else {
          print "L\t" tgt
        }
        s = substr(s, RSTART+RLENGTH)
      }
      s = $0
      while (match(s, /`[^`]+`/)) {
        tok = substr(s, RSTART+1, RLENGTH-2)
        if (index(tok, "/")) print "B\t" tok      # doc_path_of drops the rest anyway
        s = substr(s, RSTART+RLENGTH)
      }
    }
  ' "$1"
}

# Sets DOC_P to the path a citation names, or "" to skip it. Builtins only:
# this runs once per token across hundreds of files.
# $1 token, $2 origin, $3 1 when the citing file is a wiki page.
doc_path_of() {
  local p="$1" origin="$2" in_wiki="$3" last
  DOC_P=""
  case "$p" in
    *://*|mailto:*|\#*|/*|~*) return ;;
  esac
  p="${p%%#*}"; p="${p%%\?*}"
  if [ "$origin" = "B" ]; then
    p="${p%%::*}"
    case "$p" in *:[0-9]*) p="${p%%:[0-9]*}" ;; esac
    while [ "${p#./}" != "$p" ]; do p="${p#./}"; done
    case "$p" in ..*|.git/*) return ;; esac
    case "$p" in */*) : ;; *) return ;; esac
    # MCP JSON-RPC method names look exactly like relative paths.
    case "$p" in
      tools/list|tools/call|prompts/list|prompts/get|resources/list|resources/read|resources/templates/list) return ;;
    esac
  else
    p="${p//%5B/[}"; p="${p//%5D/]}"
  fi
  [ -n "$p" ] || return
  case "$p" in
    *" "*|*[{}\<\>\*\$,\|=\;\'\"\(\)]*|*...*|*…*|*:*) return ;;
  esac
  if [ "$in_wiki" -eq 1 ]; then
    [ "$origin" = "I" ] && return
    if [ "$origin" = "L" ]; then
      last="${p%/}"; last="${last##*/}"
      case "$p" in
        ../*|*/) : ;;
        *) case "$last" in *.*) : ;; *) return ;; esac ;;
      esac
    fi
  fi
  DOC_P="$p"
}

# Sets REL to $1 with ./ and ../ collapsed (no filesystem access: realpath -m
# is GNU-only), relative to the repo root: "." for the root itself, "" when the
# path escapes the repository.
repo_rel() {
  local parts=() out=() seg joined
  case "$1" in
    */.*|*//*) ;;
    "$REPO_ROOT"/*) REL="${1#"$REPO_ROOT"/}"; REL="${REL%/}"; return ;;
  esac
  IFS=/ read -ra parts <<< "$1"
  for seg in "${parts[@]}"; do
    case "$seg" in
      ''|.) ;;
      ..) [ "${#out[@]}" -gt 0 ] && unset 'out[${#out[@]}-1]' ;;
      *) out+=("$seg") ;;
    esac
  done
  joined=""
  for seg in "${out[@]+"${out[@]}"}"; do joined="$joined/$seg"; done
  REL=""
  if [ "$joined" = "$REPO_ROOT" ]; then
    REL="."
  elif [ "${joined#"$REPO_ROOT"/}" != "$joined" ]; then
    REL="${joined#"$REPO_ROOT"/}"
  fi
}

# Every path git would commit (tracked, or new and not ignored) and every
# parent dir of one, plus the wiki checkout's own. Existence on disk is not
# enough: a scan or a test container can leave an untracked, empty runtime dir
# at a path a doc cites as moved, and the audit must answer alike on every clone.
known_paths() {
  {
    git -C "$REPO_ROOT" ls-files --cached --others --exclude-standard 2>/dev/null
    if [ -f "$REPO_ROOT/$WIKI_DIR/Home.md" ]; then
      git -C "$REPO_ROOT/$WIKI_DIR" ls-files --cached --others --exclude-standard 2>/dev/null \
        | sed "s|^|$WIKI_DIR/|"
    fi
  } | awk -F/ '{ p = $1; print p; for (i = 2; i <= NF; i++) { p = p "/" $i; print p } }' | sort -u
}

# git check-ignore aborts the whole batch on a path beyond a symlink.
beyond_symlink() {
  local prefix="" seg parts=()
  IFS=/ read -ra parts <<< "$1"
  for seg in "${parts[@]}"; do
    prefix="${prefix:+$prefix/}$seg"
    [ "$prefix" = "$1" ] && return 1
    [ -L "$REPO_ROOT/$prefix" ] && return 0
  done
  return 1
}

if [ "$DOCS" -eq 1 ]; then
  work="$(mktemp -d)"
  trap 'rm -rf "$work"' EXIT
  known_paths > "$work/known"
  : > "$work/cites"; : > "$work/cands"
  idx=0
  audited=0
  for f in "${FILES[@]}"; do
    [ -f "$f" ] || continue
    rel="${f#$REPO_ROOT/}"
    for x in "${DOCS_EXCLUDE[@]}"; do
      # shellcheck disable=SC2254  # the entries are glob patterns
      case "$rel" in $x) continue 2 ;; esac
    done
    audited=$((audited+1))
    fdir="$(dirname "$f")"
    fdir_rel="${fdir#$REPO_ROOT}"; fdir_rel="${fdir_rel#/}"
    case "$rel" in "$WIKI_DIR"/*) in_wiki=1 ;; *) in_wiki=0 ;; esac
    while IFS=$'\t' read -r origin cand; do
      [ -n "$cand" ] || continue
      doc_path_of "$cand" "$origin" "$in_wiki"
      [ -n "$DOC_P" ] || continue
      case "$DOC_P" in *\[*\]*) br=1 ;; *) br=0 ;; esac
      printf '%s\t%s -> %s\t%s\n' "$idx" "$rel" "$DOC_P" "$br" >> "$work/cites"
      # A link or image resolves from the citing file's dir only (where a
      # renderer sends the click), a GitHub URL from the repo root, a
      # backticked path from the citing dir or any ROOT; F lines are where a
      # backticked token's first segment must exist for it to count as a path.
      {
        case "$origin" in
          G) repo_rel "$REPO_ROOT/$DOC_P"; printf '%s\tC\t%s\n' "$idx" "$REL" ;;
          L|I) repo_rel "$fdir/$DOC_P"; printf '%s\tC\t%s\n' "$idx" "$REL" ;;
          *)
            first="${DOC_P%%/*}"
            printf '%s\tF\t%s\n' "$idx" "${fdir_rel:+$fdir_rel/}$first"
            repo_rel "$fdir/$DOC_P"; printf '%s\tC\t%s\n' "$idx" "$REL"
            for r in "${ROOTS[@]}"; do
              if [ "$r" = "." ]; then
                printf '%s\tF\t%s\n' "$idx" "$first"
                repo_rel "$REPO_ROOT/$DOC_P"
              else
                printf '%s\tF\t%s\n' "$idx" "$r/$first"
                repo_rel "$REPO_ROOT/$r/$DOC_P"
              fi
              printf '%s\tC\t%s\n' "$idx" "$REL"
            done ;;
        esac
      } >> "$work/cands"
      idx=$((idx+1))
    done < <(extract_doc_citations "$f" | sort -u)
  done

  # Verdict per citation: "skip" (a backticked token whose first segment exists
  # nowhere, so not a path), "live", or "dead"; anything under _local/ never
  # counts as live.
  awk -F'\t' -v known="$work/known" -v cands="$work/cands" '
    BEGIN {
      while ((getline line < known) > 0) k[line] = 1
      while ((getline line < cands) > 0) {
        split(line, c, "\t")
        if (c[2] == "F") { hasF[c[1]] = 1; if ((c[3] in k) || c[3] == "_local") firstOk[c[1]] = 1; continue }
        if (c[3] == "" || c[3] == "_local" || index(c[3], "_local/") == 1) continue
        if (c[3] in k) live[c[1]] = 1
      }
    }
    {
      if (($1 in hasF) && !($1 in firstOk)) { print "skip\t" $0; next }
      print ((($1 in live) ? "live" : "dead") "\t" $0)
    }
  ' "$work/cites" > "$work/verdicts"
  checked=$(grep -vc '^skip' "$work/verdicts")

  # A dead citation that lands on a gitignored path is a runtime output, not
  # drift; so is an unresolved [placeholder]. One check-ignore for them all,
  # --no-index because none of these paths is tracked.
  : > "$work/ign_cands"
  while IFS=$'\t' read -r i c; do
    case "$c" in _local|_local/*|"$WIKI_DIR"|"$WIKI_DIR"/*) continue ;; esac
    beyond_symlink "$c" || printf '%s\t%s\n' "$i" "$c" >> "$work/ign_cands"
  done < <(awk -F'\t' 'NR == FNR { if ($1 == "dead" && $4 == "0") dead[$2] = 1; next }
                       ($1 in dead) && $2 == "C" && $3 != "" { print $1 "\t" $3 }' \
             "$work/verdicts" "$work/cands")
  cut -f2 "$work/ign_cands" | git -C "$REPO_ROOT" check-ignore --no-index --stdin 2>/dev/null \
    | awk -F'\t' 'NR == FNR { ign[$0] = 1; next } ($2 in ign) { print $1 }' - "$work/ign_cands" \
    | sort -u > "$work/ignored"
  awk -F'\t' -v ignf="$work/ignored" '
    BEGIN { while ((getline line < ignf) > 0) ign[line] = 1 }
    $1 == "dead" && $4 == "0" && !($2 in ign) { print $3 }
  ' "$work/verdicts" | sort -u > "$work/dead"

  echo "drift-audit --docs: $audited file(s), $checked citation(s) checked."
  if [ ! -s "$work/dead" ]; then
    echo "OK - every cited path resolves."
    exit 0
  fi
  echo
  echo "[docs] dead citations:"
  sed 's/^/  /' "$work/dead"
  exit 1
fi

# --- audit -----------------------------------------------------------------
agents_dead=()
skill_dead=()
checked=0
for f in "${FILES[@]}"; do
  [ -f "$f" ] || continue
  fdir="$(dirname "$f")"
  rel="${f#$REPO_ROOT/}"
  case "$rel" in *AGENTS.md) is_agents=1 ;; *) is_agents=0 ;; esac
  while IFS=$'\t' read -r origin cand; do
    [ -n "$cand" ] || continue
    is_path_like "$cand" "$origin" || continue
    checked=$((checked+1))
    if ! resolves "$cand" "$fdir" "$origin"; then
      if [ "$is_agents" -eq 1 ]; then
        agents_dead+=("$rel -> $cand")
      else
        skill_dead+=("$rel -> $cand")
      fi
    fi
  done < <(extract_citations "$f" | sort -u)
done

# --- report ----------------------------------------------------------------
dead=$(( ${#agents_dead[@]} + ${#skill_dead[@]} ))
echo "drift-audit: ${#FILES[@]} file(s), $checked citation(s) checked."
if [ "$dead" -eq 0 ]; then
  echo "OK - every cited path resolves."
  exit 0
fi
if [ "${#agents_dead[@]}" -gt 0 ]; then
  echo
  echo "[AGENTS] dead citations (always in context - fix first):"
  printf '  %s\n' "${agents_dead[@]}"
fi
if [ "${#skill_dead[@]}" -gt 0 ]; then
  echo
  echo "[skills] dead citations:"
  printf '  %s\n' "${skill_dead[@]}"
fi
exit 1
