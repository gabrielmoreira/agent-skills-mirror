#!/usr/bin/env bash
# 检查 task_plan.md 中所有阶段是否完成
# 始终以退出码 0 结束 — 使用标准输出报告状态
# 由 Stop 钩子调用以报告任务完成状态

# Explicit creation validation; the existing localized advisory path stays unchanged.
VALIDATE=0
VALIDATION_PLAN=""
for _arg in "$@"; do
    case "$_arg" in
        --validate) VALIDATE=1 ;;
        *) [ -z "$VALIDATION_PLAN" ] && VALIDATION_PLAN="$_arg" ;;
    esac
done
if [ "$VALIDATE" -eq 1 ]; then
    PLAN_FILE="${VALIDATION_PLAN:-task_plan.md}"
    [ -f "$PLAN_FILE" ] || { echo "[planning-with-files] Plan format invalid: task_plan.md was not found." >&2; exit 1; }
fi

# Creation validation is deliberately separate from advisory/gated completion.
# Keep one native status per phase, including the existing inline form. This
# never repairs or writes the plan, changes attestation, or weakens Stop guards.
if [ "$VALIDATE" -eq 1 ]; then
    awk '
        function finish_phase() {
            if (in_phase && statuses != 1) invalid = 1
        }
        /^### 阶段([ \t]|$)/ {
            finish_phase()
            phases++
            in_phase = 1
            statuses = 0
        }
        !/^### 阶段([ \t]|$)/ && /^#[ \t]|^##[ \t]|^###[ \t]/ {
            finish_phase()
            in_phase = 0
        }
        in_phase {
            line = $0
            statuses += gsub(/\*\*状态：\*\*[ \t]+(pending|in_progress|complete)([^[:alnum:]_]|$)/, "&", line)
            line = $0
            statuses += gsub(/\[(pending|in_progress|complete)\]/, "&", line)
        }
        END {
            finish_phase()
            if (!phases || invalid) {
                print "[planning-with-files] Plan format invalid: use ### 阶段 headings with exactly one native status per phase."
                exit 1
            }
            printf "[planning-with-files] Plan format valid (%d phases).\n", phases
        }
    ' "$PLAN_FILE"
    exit "$?"
fi

# issue #195: per-invocation opt-out (PLANNING_DISABLED=1) for one-shot/CI
# sessions that share a cwd with a plan but never opted into it.
[ "${PLANNING_DISABLED:-}" = "1" ] && exit 0

PLAN_FILE="${1:-task_plan.md}"

if [ ! -f "$PLAN_FILE" ]; then
    # Automatic gate checks have nothing to report without a plan (header:
    # "plans stay silent in --gate mode"); the explicit report keeps its notice.
    [ "$GATE" -eq 1 ] && exit 0
    echo "[planning-with-files] 未找到 task_plan.md — 没有进行中的规划会话。"
    exit 0
fi

# 计算阶段总数
TOTAL=$(grep -c "### 阶段" "$PLAN_FILE" || true)

# 先检查 **状态：** 格式
COMPLETE=$(grep -cF "**状态：** complete" "$PLAN_FILE" || true)
IN_PROGRESS=$(grep -cF "**状态：** in_progress" "$PLAN_FILE" || true)
PENDING=$(grep -cF "**状态：** pending" "$PLAN_FILE" || true)

# 备用：如果未找到 **状态：** 则检查 [complete] 行内格式
if [ "$COMPLETE" -eq 0 ] && [ "$IN_PROGRESS" -eq 0 ] && [ "$PENDING" -eq 0 ]; then
    COMPLETE=$(grep -c "\[complete\]" "$PLAN_FILE" || true)
    IN_PROGRESS=$(grep -c "\[in_progress\]" "$PLAN_FILE" || true)
    PENDING=$(grep -c "\[pending\]" "$PLAN_FILE" || true)
fi

# 默认为 0（如果为空）
: "${TOTAL:=0}"
: "${COMPLETE:=0}"
: "${IN_PROGRESS:=0}"
: "${PENDING:=0}"

# 报告状态（始终以退出码 0 结束 — 未完成的任务是正常状态）
# issue #191: TOTAL=0 -> not phase-structured, stay silent
if [ "$TOTAL" -eq 0 ]; then
    exit 0
fi

if [ "$COMPLETE" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
    echo "[planning-with-files] 所有阶段已完成（$COMPLETE/$TOTAL）。如果用户有额外工作，请在开始前于 task_plan.md 中新增阶段。"
else
    echo "[planning-with-files] 任务进行中（$COMPLETE/$TOTAL 个阶段已完成）。停止前请更新 progress.md。"
    if [ "$IN_PROGRESS" -gt 0 ]; then
        echo "[planning-with-files] $IN_PROGRESS 个阶段仍在进行中。"
    fi
    if [ "$PENDING" -gt 0 ]; then
        echo "[planning-with-files] $PENDING 个阶段待处理。"
    fi
fi
exit 0
