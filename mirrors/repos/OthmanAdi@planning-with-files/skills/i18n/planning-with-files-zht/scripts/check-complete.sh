#!/usr/bin/env bash
# 檢查 task_plan.md 中所有階段是否完成
# 始終以退出碼 0 結束 — 使用標準輸出回報狀態
# 由 Stop 鉤子呼叫以回報任務完成狀態

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
        /^### 階段([ \t]|$)/ {
            finish_phase()
            phases++
            in_phase = 1
            statuses = 0
        }
        !/^### 階段([ \t]|$)/ && /^#[ \t]|^##[ \t]|^###[ \t]/ {
            finish_phase()
            in_phase = 0
        }
        in_phase {
            line = $0
            statuses += gsub(/\*\*狀態：\*\*[ \t]+(pending|in_progress|complete)([^[:alnum:]_]|$)/, "&", line)
            line = $0
            statuses += gsub(/\[(pending|in_progress|complete)\]/, "&", line)
        }
        END {
            finish_phase()
            if (!phases || invalid) {
                print "[planning-with-files] Plan format invalid: use ### 階段 headings with exactly one native status per phase."
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
    echo "[planning-with-files] 未找到 task_plan.md — 沒有進行中的規劃會話。"
    exit 0
fi

# 計算階段總數
TOTAL=$(grep -c "### 階段" "$PLAN_FILE" || true)

# 先檢查 **狀態：** 格式
COMPLETE=$(grep -cF "**狀態：** complete" "$PLAN_FILE" || true)
IN_PROGRESS=$(grep -cF "**狀態：** in_progress" "$PLAN_FILE" || true)
PENDING=$(grep -cF "**狀態：** pending" "$PLAN_FILE" || true)

# 備用：如果未找到 **狀態：** 則檢查 [complete] 行內格式
if [ "$COMPLETE" -eq 0 ] && [ "$IN_PROGRESS" -eq 0 ] && [ "$PENDING" -eq 0 ]; then
    COMPLETE=$(grep -c "\[complete\]" "$PLAN_FILE" || true)
    IN_PROGRESS=$(grep -c "\[in_progress\]" "$PLAN_FILE" || true)
    PENDING=$(grep -c "\[pending\]" "$PLAN_FILE" || true)
fi

# 預設為 0（如果為空）
: "${TOTAL:=0}"
: "${COMPLETE:=0}"
: "${IN_PROGRESS:=0}"
: "${PENDING:=0}"

# 回報狀態（始終以退出碼 0 結束 — 未完成的任務是正常狀態）
# issue #191: TOTAL=0 -> not phase-structured, stay silent
if [ "$TOTAL" -eq 0 ]; then
    exit 0
fi

if [ "$COMPLETE" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
    echo "[planning-with-files] 所有階段已完成（$COMPLETE/$TOTAL）。如果使用者有額外工作，請在開始前於 task_plan.md 中新增階段。"
else
    echo "[planning-with-files] 任務進行中（$COMPLETE/$TOTAL 個階段已完成）。停止前請更新 progress.md。"
    if [ "$IN_PROGRESS" -gt 0 ]; then
        echo "[planning-with-files] $IN_PROGRESS 個階段仍在進行中。"
    fi
    if [ "$PENDING" -gt 0 ]; then
        echo "[planning-with-files] $PENDING 個階段待處理。"
    fi
fi
exit 0
