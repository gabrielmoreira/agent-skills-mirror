#!/usr/bin/env bash
# التحقق من اكتمال جميع المراحل في task_plan.md
# ينهي دائمًا برمز خروج 0 — يستخدم stdout للإبلاغ عن الحالة
# يُستدعى بواسطة خطاف Stop للإبلاغ عن حالة اكتمال المهمة

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
        /^### المرحلة([ \t]|$)/ {
            finish_phase()
            phases++
            in_phase = 1
            statuses = 0
        }
        !/^### المرحلة([ \t]|$)/ && /^#[ \t]|^##[ \t]|^###[ \t]/ {
            finish_phase()
            in_phase = 0
        }
        in_phase {
            line = $0
            statuses += gsub(/\*\*الحالة:\*\*[ \t]+(pending|in_progress|complete)([^[:alnum:]_]|$)/, "&", line)
            line = $0
            statuses += gsub(/\[(pending|in_progress|complete)\]/, "&", line)
        }
        END {
            finish_phase()
            if (!phases || invalid) {
                print "[planning-with-files] Plan format invalid: use ### المرحلة headings with exactly one native status per phase."
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
    echo "[planning-with-files-ar] لم يتم العثور على task_plan.md — لا توجد جلسة تخطيط نشطة."
    exit 0
fi

# حساب إجمالي عدد المراحل
TOTAL=$(grep -c "### المرحلة" "$PLAN_FILE" || true)

# التحقق أولاً من تنسيق **الحالة:**
COMPLETE=$(grep -cF "**الحالة:** complete" "$PLAN_FILE" || true)
IN_PROGRESS=$(grep -cF "**الحالة:** in_progress" "$PLAN_FILE" || true)
PENDING=$(grep -cF "**الحالة:** pending" "$PLAN_FILE" || true)

# بديل: إذا لم يتم العثور على **الحالة:** فتحقق من تنسيق [complete] المضمن
if [ "$COMPLETE" -eq 0 ] && [ "$IN_PROGRESS" -eq 0 ] && [ "$PENDING" -eq 0 ]; then
    COMPLETE=$(grep -c "\[complete\]" "$PLAN_FILE" || true)
    IN_PROGRESS=$(grep -c "\[in_progress\]" "$PLAN_FILE" || true)
    PENDING=$(grep -c "\[pending\]" "$PLAN_FILE" || true)
fi

# الافتراضي 0 (إذا كان فارغًا)
: "${TOTAL:=0}"
: "${COMPLETE:=0}"
: "${IN_PROGRESS:=0}"
: "${PENDING:=0}"

# الإبلاغ عن الحالة (ينهي دائمًا برمز خروج 0 — المهام غير المكتملة حالة طبيعية)
# issue #191: TOTAL=0 -> not phase-structured, stay silent
if [ "$TOTAL" -eq 0 ]; then
    exit 0
fi

if [ "$COMPLETE" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
    echo "[planning-with-files-ar] اكتملت جميع المراحل ($COMPLETE/$TOTAL). إذا كان لدى المستخدم عمل إضافي، أضف مراحل في task_plan.md قبل البدء."
else
    echo "[planning-with-files-ar] المهمة قيد التنفيذ ($COMPLETE/$TOTAL مرحلة مكتملة). حدّث progress.md قبل التوقف."
    if [ "$IN_PROGRESS" -gt 0 ]; then
        echo "[planning-with-files-ar] $IN_PROGRESS مرحلة/مراحل لا تزال قيد التنفيذ."
    fi
    if [ "$PENDING" -gt 0 ]; then
        echo "[planning-with-files-ar] $PENDING مرحلة/مراحل معلقة."
    fi
fi
exit 0
