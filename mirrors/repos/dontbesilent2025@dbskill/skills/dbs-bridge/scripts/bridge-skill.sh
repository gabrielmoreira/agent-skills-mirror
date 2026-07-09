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
  mkdir -p "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.agents/skills" "$HOME/.grok/skills"
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

link_grok_one() {
  local src="$1"
  local name="$2"
  local dir="$HOME/.grok/skills/$name"
  local skill_file="$dir/SKILL.md"

  if [[ -L "$dir" ]]; then
    rm "$dir"
  elif [[ -e "$dir" && ! -d "$dir" ]]; then
    echo "✗ $dir 是真实文件，已跳过"
    return 2
  elif [[ -d "$dir" && -f "$skill_file" ]] && ! grep -q '^## Grok Bridge$' "$skill_file"; then
    echo "✗ $dir 是真实 Grok skill，已跳过"
    return 2
  elif [[ -d "$dir" && ! -f "$skill_file" ]]; then
    echo "✗ $dir 是真实目录，已跳过"
    return 2
  fi

  mkdir -p "$dir"
  cat > "$skill_file" <<EOF
---
name: $name
user_invocable: true
description: |
  $name bridge。在 Grok TUI 中可通过 /$name 触发；触发后必须先读取项目真源 SKILL.md。
---
# $name

## Grok Bridge

- Source of truth: $src/SKILL.md
- Read the source-of-truth file before executing this skill.
- Follow the source file's workflow, constraints, examples, and output format.
- Treat this file as a thin Grok bridge only; do not maintain long-form logic here.

## 使用说明

1. 在 Grok TUI 中输入 \`/$name\` 即可触发。
2. Grok 会优先使用本 bridge 指向的真源。
3. 如需更新，直接修改真源。
EOF
  echo "✓ $dir -> $src"
}

unlink_grok_one() {
  local name="$1"
  local dir="$HOME/.grok/skills/$name"
  local skill_file="$dir/SKILL.md"

  if [[ -L "$dir" ]]; then
    rm "$dir"
    echo "✓ 已移除软链 $dir"
  elif [[ -d "$dir" && -f "$skill_file" ]] && grep -q '^## Grok Bridge$' "$skill_file"; then
    rm -rf "$dir"
    echo "✓ 已移除 Grok bridge $dir"
  elif [[ -e "$dir" ]]; then
    echo "✗ $dir 是真实目录或文件，已保留"
    return 2
  else
    echo "· $dir 不存在，跳过"
  fi
}

status_grok_one() {
  local name="$1"
  local dir="$HOME/.grok/skills/$name"
  local skill_file="$dir/SKILL.md"
  local source user_invocable

  if [[ -L "$dir" ]]; then
    echo "✓ $dir -> $(readlink "$dir")"
  elif [[ -d "$dir" && -f "$skill_file" ]] && grep -q '^## Grok Bridge$' "$skill_file"; then
    source="$(grep -m 1 '^- Source of truth:' "$skill_file" | sed 's/^- Source of truth: //')"
    if grep -q '^user_invocable: true$' "$skill_file"; then
      user_invocable="user_invocable: true"
    else
      user_invocable="缺 user_invocable: true"
      echo "✗ $dir -> $source ($user_invocable)"
      return 2
    fi
    echo "✓ $dir -> $source ($user_invocable)"
  elif [[ -e "$dir" ]]; then
    echo "✗ $dir 存在，但不是 dbs-bridge 生成的 Grok bridge"
    return 2
  else
    echo "· $dir 未桥接"
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
  local target_dirs=("$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.agents/skills")

  root="$(repo_root)"
  candidate="$(resolve_candidate "$input" "$root")"

  ensure_target_parent
  failed=0

  while IFS= read -r src; do
    name="$(basename "$src")"
    echo "== $name =="

    case "$action" in
      link)
        for target_dir in "${target_dirs[@]}"; do
          link_one "$src" "$target_dir" "$name" || failed=1
        done
        link_grok_one "$src" "$name" || failed=1
        ;;
      unlink)
        for target_dir in "${target_dirs[@]}"; do
          unlink_one "$target_dir" "$name" || failed=1
        done
        unlink_grok_one "$name" || failed=1
        ;;
      status)
        for target_dir in "${target_dirs[@]}"; do
          status_one "$target_dir" "$name" || failed=1
        done
        status_grok_one "$name" || failed=1
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
