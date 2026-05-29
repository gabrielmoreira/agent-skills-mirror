#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  spec-init.sh [target_dir] [--here] [--name NAME] [--type TYPE] [--lang LANG] [--force]

Examples:
  spec-init.sh my-app
  spec-init.sh ./demo-service --type api
  spec-init.sh --here --name "Demo Project" --type web
  spec-init.sh my-cli --type cli --lang en
EOF
}

escape_replacement() {
  printf '%s' "$1" | sed -e 's/[\/&]/\\&/g'
}

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_ROOT="$SKILL_ROOT/assets/templates/project"

TARGET_DIR=""
PROJECT_NAME=""
PROJECT_TYPE=""
PROJECT_TYPE_REASON=""
LANGUAGE="zh"
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --here)
      TARGET_DIR="."
      shift
      ;;
    --name)
      PROJECT_NAME="${2:-}"
      shift 2
      ;;
    --name=*)
      PROJECT_NAME="${1#*=}"
      shift
      ;;
    --type)
      PROJECT_TYPE="${2:-}"
      shift 2
      ;;
    --type=*)
      PROJECT_TYPE="${1#*=}"
      shift
      ;;
    --lang)
      LANGUAGE="${2:-}"
      shift 2
      ;;
    --lang=*)
      LANGUAGE="${1#*=}"
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -z "$TARGET_DIR" ]]; then
        TARGET_DIR="$1"
        shift
      else
        printf 'Unexpected argument: %s\n\n' "$1" >&2
        usage >&2
        exit 1
      fi
      ;;
  esac
done

if [[ -z "$TARGET_DIR" ]]; then
  TARGET_DIR="."
fi

mkdir -p "$TARGET_DIR"
TARGET_DIR="$(cd -- "$TARGET_DIR" && pwd)"

if [[ -z "$PROJECT_NAME" ]]; then
  PROJECT_NAME="$(basename "$TARGET_DIR")"
fi

normalize_language() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]'
}

normalize_project_type() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]'
}

localized_text() {
  local zh_text="$1"
  local en_text="$2"

  if [[ "$LANGUAGE" == "en" ]]; then
    printf '%s' "$en_text"
    return
  fi

  printf '%s' "$zh_text"
}

is_supported_language() {
  case "$1" in
    zh|en)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

is_supported_project_type() {
  case "$1" in
    web|api|cli|library|service)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

LANGUAGE="$(normalize_language "$LANGUAGE")"

if ! is_supported_language "$LANGUAGE"; then
  printf 'Unsupported language: %s\n' "$LANGUAGE" >&2
  printf 'Supported languages: zh, en\n' >&2
  exit 1
fi

WORKFLOW_ROOT="docs/workflow"
KNOWLEDGE_ROOT="docs/knowledge"
CHANGES_ROOT="docs/changes"
RULES_ROOT="docs/rules"

INTAKE_DOC="$WORKFLOW_ROOT/00-intake/README.md"
REQUIREMENTS_DOC="$WORKFLOW_ROOT/01-requirements/README.md"
DESIGN_DOC="$WORKFLOW_ROOT/02-design/README.md"
IMPLEMENTATION_DOC="$WORKFLOW_ROOT/03-implementation/README.md"
VERIFICATION_DOC="$WORKFLOW_ROOT/04-verification/README.md"
TASKS_DOC="$WORKFLOW_ROOT/05-tasks/README.md"

CONTEXT_DOC="$KNOWLEDGE_ROOT/context/README.md"
STRUCTURE_DOC="$KNOWLEDGE_ROOT/structure/README.md"
BEHAVIOR_DOC="$KNOWLEDGE_ROOT/behavior/README.md"
REFERENCE_DOC="$KNOWLEDGE_ROOT/reference/README.md"

CHANGES_INDEX_DOC="$CHANGES_ROOT/README.md"
ADR_INDEX_DOC="docs/adr/README.md"
RULES_INDEX_DOC="$RULES_ROOT/README.md"
ROUTING_RULES_DOC="$RULES_ROOT/document-routing-rules.md"
TOPOLOGY_FILE="spec-init.topology.yml"

LANGUAGE_ROOT="$TEMPLATE_ROOT/$LANGUAGE"

infer_project_type() {
  local keywords
  keywords="$(normalize_project_type "$PROJECT_NAME $(basename "$TARGET_DIR")")"

  case "$keywords" in
    *cli*|*command*|*cmd*|*tool*)
      PROJECT_TYPE="cli"
      PROJECT_TYPE_REASON="$(localized_text '根据项目名或目录名中的关键词 cli/command/cmd/tool 推断为 cli。' 'Inferred as cli from project or directory keywords: cli/command/cmd/tool.')"
      ;;
    *api*|*backend*|*server*|*bff*)
      PROJECT_TYPE="api"
      PROJECT_TYPE_REASON="$(localized_text '根据项目名或目录名中的关键词 api/backend/server/bff 推断为 api。' 'Inferred as api from project or directory keywords: api/backend/server/bff.')"
      ;;
    *web*|*site*|*frontend*|*admin*|*dashboard*|*portal*|*ui*)
      PROJECT_TYPE="web"
      PROJECT_TYPE_REASON="$(localized_text '根据项目名或目录名中的关键词 web/site/frontend/admin/dashboard/portal/ui 推断为 web。' 'Inferred as web from project or directory keywords: web/site/frontend/admin/dashboard/portal/ui.')"
      ;;
    *sdk*|*lib*|*library*|*package*|*plugin*|*kit*)
      PROJECT_TYPE="library"
      PROJECT_TYPE_REASON="$(localized_text '根据项目名或目录名中的关键词 sdk/lib/library/package/plugin/kit 推断为 library。' 'Inferred as library from project or directory keywords: sdk/lib/library/package/plugin/kit.')"
      ;;
    *worker*|*consumer*|*queue*|*job*|*scheduler*|*daemon*|*service*)
      PROJECT_TYPE="service"
      PROJECT_TYPE_REASON="$(localized_text '根据项目名或目录名中的关键词 worker/consumer/queue/job/scheduler/daemon/service 推断为 service。' 'Inferred as service from project or directory keywords: worker/consumer/queue/job/scheduler/daemon/service.')"
      ;;
    *)
      PROJECT_TYPE="service"
      PROJECT_TYPE_REASON="$(localized_text "未提供项目类型，且无法从项目名或目录名稳定推断，默认按 service 初始化；请在 ${INTAKE_DOC} 中确认。" "No project type was provided and no stable keyword matched the project or directory name, so the scaffold defaults to service. Confirm this in ${INTAKE_DOC}.")"
      ;;
  esac
}

if [[ -n "$PROJECT_TYPE" ]]; then
  PROJECT_TYPE="$(normalize_project_type "$PROJECT_TYPE")"

  if ! is_supported_project_type "$PROJECT_TYPE"; then
    printf 'Unsupported project type: %s\n' "$PROJECT_TYPE" >&2
    printf 'Supported types: web, api, cli, library, service\n' >&2
    exit 1
  fi

  PROJECT_TYPE_REASON="$(localized_text "用户明确通过命令参数指定项目类型：${PROJECT_TYPE}。" "Project type explicitly provided via --type: ${PROJECT_TYPE}.")"
else
  infer_project_type
fi

TODAY="$(date +%F)"

render_template() {
  local source_path="$1"
  local destination_path="$2"

  if [[ -e "$destination_path" && "$FORCE" -ne 1 ]]; then
    printf 'skip  %s (already exists)\n' "$destination_path"
    return
  fi

  mkdir -p "$(dirname "$destination_path")"

  sed \
    -e "s/__PROJECT_NAME__/$(escape_replacement "$PROJECT_NAME")/g" \
    -e "s/__PROJECT_TYPE__/$(escape_replacement "$PROJECT_TYPE")/g" \
    -e "s/__PROJECT_TYPE_REASON__/$(escape_replacement "$PROJECT_TYPE_REASON")/g" \
    -e "s/__DATE__/$(escape_replacement "$TODAY")/g" \
    "$source_path" > "$destination_path"

  printf 'write %s\n' "$destination_path"
}

resolve_template_path() {
  local relative_path="$1"
  local type_specific_path="$LANGUAGE_ROOT/types/$PROJECT_TYPE/$relative_path"
  local default_path="$LANGUAGE_ROOT/$relative_path"

  if [[ -f "$type_specific_path" ]]; then
    printf '%s' "$type_specific_path"
    return
  fi

  printf '%s' "$default_path"
}

render_project_template() {
  local relative_path="$1"
  local destination_path="$2"

  render_template "$(resolve_template_path "$relative_path")" "$destination_path"
}

ensure_placeholder_file() {
  local file_path="$1"

  if [[ -e "$file_path" ]]; then
    return
  fi

  mkdir -p "$(dirname "$file_path")"
  : > "$file_path"
  printf 'write %s\n' "$file_path"
}

cleanup_legacy_scaffold() {
  local target_root="$1"

  rm -rf \
    "$target_root/docs/00-intake" \
    "$target_root/docs/01-requirements" \
    "$target_root/docs/02-design" \
    "$target_root/docs/03-implementation" \
    "$target_root/docs/04-tdd" \
    "$target_root/docs/05-tasks" \
    "$target_root/docs/changes/CR-0001-template.md" \
    "$target_root/docs/changes/BUG-0001-template.md"
}

if [[ "$FORCE" -eq 1 ]]; then
  cleanup_legacy_scaffold "$TARGET_DIR"
fi

mkdir -p \
  "$TARGET_DIR/$WORKFLOW_ROOT/00-intake" \
  "$TARGET_DIR/$WORKFLOW_ROOT/01-requirements" \
  "$TARGET_DIR/$WORKFLOW_ROOT/02-design" \
  "$TARGET_DIR/$WORKFLOW_ROOT/03-implementation" \
  "$TARGET_DIR/$WORKFLOW_ROOT/04-verification" \
  "$TARGET_DIR/$WORKFLOW_ROOT/05-tasks" \
  "$TARGET_DIR/$KNOWLEDGE_ROOT/context" \
  "$TARGET_DIR/$KNOWLEDGE_ROOT/structure" \
  "$TARGET_DIR/$KNOWLEDGE_ROOT/behavior" \
  "$TARGET_DIR/$KNOWLEDGE_ROOT/reference" \
  "$TARGET_DIR/docs/issues" \
  "$TARGET_DIR/$CHANGES_ROOT/active/CHG-0001-template" \
  "$TARGET_DIR/$CHANGES_ROOT/completed" \
  "$TARGET_DIR/$CHANGES_ROOT/legacy" \
  "$TARGET_DIR/docs/releases" \
  "$TARGET_DIR/docs/archive" \
  "$TARGET_DIR/docs/adr" \
  "$TARGET_DIR/docs/rules" \
  "$TARGET_DIR/src" \
  "$TARGET_DIR/tests" \
  "$TARGET_DIR/scripts"

ensure_placeholder_file "$TARGET_DIR/src/.gitkeep"
ensure_placeholder_file "$TARGET_DIR/tests/.gitkeep"
ensure_placeholder_file "$TARGET_DIR/scripts/.gitkeep"

render_project_template "spec-init.topology.yml.tmpl" "$TARGET_DIR/$TOPOLOGY_FILE"
render_project_template "README.md.tmpl" "$TARGET_DIR/README.md"
render_project_template "AGENTS.md.tmpl" "$TARGET_DIR/AGENTS.md"
render_project_template "docs/00-intake/README.md.tmpl" "$TARGET_DIR/$INTAKE_DOC"
render_project_template "docs/01-requirements/README.md.tmpl" "$TARGET_DIR/$REQUIREMENTS_DOC"
render_project_template "docs/02-design/README.md.tmpl" "$TARGET_DIR/$DESIGN_DOC"
render_project_template "docs/03-implementation/README.md.tmpl" "$TARGET_DIR/$IMPLEMENTATION_DOC"
render_project_template "docs/04-tdd/README.md.tmpl" "$TARGET_DIR/$VERIFICATION_DOC"
render_project_template "docs/05-tasks/README.md.tmpl" "$TARGET_DIR/$TASKS_DOC"
render_project_template "docs/knowledge/context/README.md.tmpl" "$TARGET_DIR/$CONTEXT_DOC"
render_project_template "docs/knowledge/structure/README.md.tmpl" "$TARGET_DIR/$STRUCTURE_DOC"
render_project_template "docs/knowledge/behavior/README.md.tmpl" "$TARGET_DIR/$BEHAVIOR_DOC"
render_project_template "docs/knowledge/reference/README.md.tmpl" "$TARGET_DIR/$REFERENCE_DOC"
render_project_template "docs/issues/README.md.tmpl" "$TARGET_DIR/docs/issues/README.md"
render_project_template "docs/changes/README.md.tmpl" "$TARGET_DIR/$CHANGES_INDEX_DOC"
render_project_template "docs/changes/active/CHG-0001-template/overview.md.tmpl" "$TARGET_DIR/$CHANGES_ROOT/active/CHG-0001-template/overview.md"
render_project_template "docs/changes/active/CHG-0001-template/design.md.tmpl" "$TARGET_DIR/$CHANGES_ROOT/active/CHG-0001-template/design.md"
render_project_template "docs/changes/active/CHG-0001-template/verification.md.tmpl" "$TARGET_DIR/$CHANGES_ROOT/active/CHG-0001-template/verification.md"
render_project_template "docs/changes/active/CHG-0001-template/tasks.md.tmpl" "$TARGET_DIR/$CHANGES_ROOT/active/CHG-0001-template/tasks.md"
render_project_template "docs/changes/active/CHG-0001-template/impact.md.tmpl" "$TARGET_DIR/$CHANGES_ROOT/active/CHG-0001-template/impact.md"
render_project_template "docs/changes/completed/README.md.tmpl" "$TARGET_DIR/$CHANGES_ROOT/completed/README.md"
render_project_template "docs/changes/legacy/README.md.tmpl" "$TARGET_DIR/$CHANGES_ROOT/legacy/README.md"
render_project_template "docs/releases/README.md.tmpl" "$TARGET_DIR/docs/releases/README.md"
render_project_template "docs/releases/v0.1.0-template.md.tmpl" "$TARGET_DIR/docs/releases/v0.1.0-template.md"
render_project_template "docs/archive/README.md.tmpl" "$TARGET_DIR/docs/archive/README.md"
render_project_template "docs/adr/README.md.tmpl" "$TARGET_DIR/$ADR_INDEX_DOC"
render_project_template "docs/adr/0000-record-template.md.tmpl" "$TARGET_DIR/docs/adr/0000-record-template.md"
render_project_template "docs/rules/README.md.tmpl" "$TARGET_DIR/$RULES_INDEX_DOC"
render_project_template "docs/rules/clarification-rules.md.tmpl" "$TARGET_DIR/docs/rules/clarification-rules.md"
render_project_template "docs/rules/coding-standards.md.tmpl" "$TARGET_DIR/docs/rules/coding-standards.md"
render_project_template "docs/rules/testing-standards.md.tmpl" "$TARGET_DIR/docs/rules/testing-standards.md"
render_project_template "docs/rules/bug-fix-rules.md.tmpl" "$TARGET_DIR/docs/rules/bug-fix-rules.md"
render_project_template "docs/rules/doc-sync-rules.md.tmpl" "$TARGET_DIR/docs/rules/doc-sync-rules.md"
render_project_template "docs/rules/change-management-rules.md.tmpl" "$TARGET_DIR/docs/rules/change-management-rules.md"
render_project_template "docs/rules/issue-management-rules.md.tmpl" "$TARGET_DIR/docs/rules/issue-management-rules.md"
render_project_template "docs/rules/definition-of-done.md.tmpl" "$TARGET_DIR/docs/rules/definition-of-done.md"
render_project_template "docs/rules/document-routing-rules.md.tmpl" "$TARGET_DIR/$ROUTING_RULES_DOC"

printf '\n%s %s\n' "$(localized_text '已初始化目录：' 'Initialized project scaffold in:')" "$TARGET_DIR"
printf '%s %s\n' "$(localized_text '项目名：' 'Project name:')" "$PROJECT_NAME"
printf '%s %s\n' "$(localized_text '项目类型：' 'Project type:')" "$PROJECT_TYPE"
printf '%s %s\n' "$(localized_text '输出语言：' 'Output language:')" "$LANGUAGE"
printf '%s %s\n\n' "$(localized_text '类型依据：' 'Type reason:')" "$PROJECT_TYPE_REASON"

printf '%s\n' "$(localized_text '建议下一步：' 'Recommended next steps:')"
printf '1. %s\n' "$(localized_text "补齐 ${INTAKE_DOC}" "Complete ${INTAKE_DOC}")"
printf '2. %s\n' "$(localized_text "把目标整理为 ${REQUIREMENTS_DOC}" "Turn the project goals into ${REQUIREMENTS_DOC}")"
printf '3. %s\n' "$(localized_text "在编码前完成 ${DESIGN_DOC}" "Complete ${DESIGN_DOC} before coding")"
printf '4. %s\n' "$(localized_text "先定义 ${VERIFICATION_DOC} 中的验证方式" "Define the verification approach in ${VERIFICATION_DOC} first")"
printf '5. %s\n' "$(localized_text "补齐 ${CONTEXT_DOC}、${STRUCTURE_DOC}、${BEHAVIOR_DOC}、${REFERENCE_DOC} 中的长期真相" "Capture long-lived truth in ${CONTEXT_DOC}, ${STRUCTURE_DOC}, ${BEHAVIOR_DOC}, and ${REFERENCE_DOC}")"
printf '6. %s\n' "$(localized_text "检查 ${TOPOLOGY_FILE} 与 ${ROUTING_RULES_DOC}，再把首个 change 拆进 ${CHANGES_ROOT}/active/CHG-0001-template/" "Review ${TOPOLOGY_FILE} and ${ROUTING_RULES_DOC}, then break the first change into ${CHANGES_ROOT}/active/CHG-0001-template/")"
