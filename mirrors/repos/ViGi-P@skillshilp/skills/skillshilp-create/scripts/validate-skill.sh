#!/usr/bin/env bash
set -u

usage() {
  echo "Usage: $0 <skill-dir>" >&2
}

error_count=0
warning_count=0

error() {
  printf 'ERROR: %s\n' "$*" >&2
  error_count=$((error_count + 1))
}

warn() {
  printf 'WARN: %s\n' "$*" >&2
  warning_count=$((warning_count + 1))
}

trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

strip_scalar() {
  local value
  value="$(trim "$1")"
  if [[ "$value" == \"*\" && "$value" == *\" && ${#value} -ge 2 ]]; then
    value="${value:1:${#value}-2}"
  elif [[ "$value" == \'*\' && "$value" == *\' && ${#value} -ge 2 ]]; then
    value="${value:1:${#value}-2}"
  fi
  printf '%s' "$value"
}

if [[ $# -ne 1 ]]; then
  usage
  exit 2
fi

skill_dir="${1%/}"
skill_md="$skill_dir/SKILL.md"

if [[ ! -d "$skill_dir" ]]; then
  error "Skill directory not found: $skill_dir"
  exit 1
fi

if [[ ! -f "$skill_md" ]]; then
  error "SKILL.md not found in $skill_dir"
  exit 1
fi

if [[ "$(sed -n '1p' "$skill_md")" != "---" ]]; then
  error "SKILL.md must start with YAML frontmatter"
fi

frontmatter="$(awk 'NR==1 { next } $0=="---" { found=1; exit 0 } { print } END { if (!found) exit 1 }' "$skill_md")"
if [[ $? -ne 0 ]]; then
  error "SKILL.md frontmatter is missing a closing ---"
  frontmatter=""
fi

allowed_keys=" name description license compatibility metadata allowed-tools "
while IFS= read -r key; do
  [[ -z "$key" ]] && continue
  if [[ "$allowed_keys" != *" $key "* ]]; then
    error "Unsupported portable frontmatter field: $key"
  fi
done < <(printf '%s\n' "$frontmatter" | sed -n 's/^\([A-Za-z][A-Za-z0-9_-]*\):.*/\1/p')

name_line="$(printf '%s\n' "$frontmatter" | sed -n 's/^name:[[:space:]]*//p' | head -n 1)"
description_line="$(printf '%s\n' "$frontmatter" | sed -n 's/^description:[[:space:]]*//p' | head -n 1)"
compatibility_line="$(printf '%s\n' "$frontmatter" | sed -n 's/^compatibility:[[:space:]]*//p' | head -n 1)"
allowed_tools_line="$(printf '%s\n' "$frontmatter" | sed -n 's/^allowed-tools:[[:space:]]*//p' | head -n 1)"

name="$(strip_scalar "$name_line")"
description="$(strip_scalar "$description_line")"
compatibility="$(strip_scalar "$compatibility_line")"
allowed_tools="$(strip_scalar "$allowed_tools_line")"

if [[ -z "$name" ]]; then
  error "Missing required frontmatter field: name"
elif [[ ! "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  error "Invalid skill name: $name"
elif [[ ${#name} -gt 64 ]]; then
  error "Skill name exceeds 64 characters: $name"
fi

expected_name="$(basename "$skill_dir")"
if [[ -n "$name" && "$name" != "$expected_name" ]]; then
  error "Frontmatter name '$name' does not match directory '$expected_name'"
fi

if [[ -z "$description" ]]; then
  error "Missing required frontmatter field: description"
elif [[ "$description" == ">" || "$description" == "|" ]]; then
  error "Description should be a single-line scalar for portable validation"
elif [[ ${#description} -gt 1024 ]]; then
  error "Description exceeds 1024 characters"
elif ! printf '%s\n' "$description" | grep -Eiq '(use|when|for|mentions?|tasks?|files?)'; then
  warn "Description may lack clear activation criteria"
fi

if [[ -n "$compatibility" && ${#compatibility} -gt 500 ]]; then
  error "Compatibility exceeds 500 characters"
fi

if printf '%s\n' "$frontmatter" | grep -q '^allowed-tools:' && [[ -z "$allowed_tools" ]]; then
  error "allowed-tools must be a space-separated string, not a YAML list or empty value"
fi

line_count="$(wc -l < "$skill_md" | tr -d ' ')"
if [[ "$line_count" -gt 500 ]]; then
  warn "SKILL.md is over 500 lines; move conditional detail into references"
fi

for optional_dir in references scripts assets; do
  if [[ -d "$skill_dir/$optional_dir" ]] && ! find "$skill_dir/$optional_dir" -mindepth 1 -print -quit | grep -q .; then
    error "Optional directory is empty: $optional_dir"
  fi
done

scan_files=("$skill_md")
if [[ -d "$skill_dir/references" ]]; then
  while IFS= read -r reference_file; do
    scan_files+=("$reference_file")
  done < <(find "$skill_dir/references" -type f -name '*.md' | sort)
fi

while IFS= read -r ref; do
  [[ -z "$ref" ]] && continue
  ref="${ref%%#*}"
  if [[ ! -e "$skill_dir/$ref" ]]; then
    error "Broken relative reference: $ref"
  fi
done < <(grep -hEo '((references|scripts|assets)/[A-Za-z0-9._/-]+)' "${scan_files[@]}" 2>/dev/null | sort -u)

if [[ "$error_count" -gt 0 ]]; then
  printf 'Skill validation failed: %d error(s), %d warning(s)\n' "$error_count" "$warning_count" >&2
  exit 1
fi

printf 'Skill validation passed: %d warning(s)\n' "$warning_count"
