#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bridge-skill.sh link <skill-name-or-path>
  bridge-skill.sh unlink <skill-name-or-path>
  bridge-skill.sh status <skill-name-or-path>

Examples:
  bridge-skill.sh link dbs-hook
  bridge-skill.sh link skills/dbs-hook
  bridge-skill.sh link skills
  bridge-skill.sh status /absolute/path/to/skill
USAGE
}

die() {
  echo "✗ $*" >&2
  exit 1
}

repo_root() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "$script_dir/../../.." && pwd
}

resolve_candidate() {
  local input="$1"
  local root="$2"
  local candidate

  if [[ "$input" = /* ]]; then
    candidate="$input"
  elif [[ -d "$PWD/$input" ]]; then
    candidate="$PWD/$input"
  elif [[ -d "$root/$input" ]]; then
    candidate="$root/$input"
  elif [[ -d "$root/skills/$input" ]]; then
    candidate="$root/skills/$input"
  else
    die "找不到 skill 或 skill 集合目录：$input"
  fi

  candidate="$(cd "$candidate" && pwd)"
  printf '%s\n' "$candidate"
}

list_skill_sources() {
  local candidate="$1"
  local found=0

  if [[ -f "$candidate/SKILL.md" ]]; then
    printf '%s\n' "$candidate"
    return 0
  fi

  while IFS= read -r skill_dir; do
    found=1
    printf '%s\n' "$(dirname "$skill_dir")"
  done < <(find "$candidate" -mindepth 2 -maxdepth 2 -name SKILL.md -type f | sort)

  [[ "$found" -eq 1 ]] || die "$candidate 里没有 SKILL.md，也没有包含 SKILL.md 的一级子目录"
}

ensure_target_parent() {
  mkdir -p "$HOME/.claude/skills" "$HOME/.codex/skills"
}

link_one() {
  local src="$1"
  local dest_dir="$2"
  local name="$3"
  local link="$dest_dir/$name"

  if [[ -e "$link" && ! -L "$link" ]]; then
    echo "✗ $link 是真实目录或文件，已跳过"
    return 2
  fi

  ln -sfn "$src" "$link"
  echo "✓ $link -> $(readlink "$link")"
}

unlink_one() {
  local dest_dir="$1"
  local name="$2"
  local link="$dest_dir/$name"

  if [[ -L "$link" ]]; then
    rm "$link"
    echo "✓ 已移除软链 $link"
  elif [[ -e "$link" ]]; then
    echo "✗ $link 是真实目录或文件，已保留"
    return 2
  else
    echo "· $link 不存在，跳过"
  fi
}

status_one() {
  local dest_dir="$1"
  local name="$2"
  local link="$dest_dir/$name"

  if [[ -L "$link" ]]; then
    echo "✓ $link -> $(readlink "$link")"
  elif [[ -e "$link" ]]; then
    echo "✗ $link 存在，但不是软链"
    return 2
  else
    echo "· $link 未桥接"
  fi
}

main() {
  if [[ $# -ne 2 ]]; then
    usage
    exit 1
  fi

  local action="$1"
  local input="$2"
  local root candidate src name failed

  root="$(repo_root)"
  candidate="$(resolve_candidate "$input" "$root")"

  ensure_target_parent
  failed=0

  while IFS= read -r src; do
    name="$(basename "$src")"
    echo "== $name =="

    case "$action" in
      link)
        link_one "$src" "$HOME/.claude/skills" "$name" || failed=1
        link_one "$src" "$HOME/.codex/skills" "$name" || failed=1
        ;;
      unlink)
        unlink_one "$HOME/.claude/skills" "$name" || failed=1
        unlink_one "$HOME/.codex/skills" "$name" || failed=1
        ;;
      status)
        status_one "$HOME/.claude/skills" "$name" || failed=1
        status_one "$HOME/.codex/skills" "$name" || failed=1
        ;;
      *)
        usage
        exit 1
        ;;
    esac
  done < <(list_skill_sources "$candidate")

  exit "$failed"
}

main "$@"
