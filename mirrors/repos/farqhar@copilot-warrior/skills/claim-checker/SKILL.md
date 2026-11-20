---
name: claim-checker
description: Checks a supplier invoice or progress claim against an agreed rate schedule in the same workbook. Flags rate mismatches, quantity overruns, unknown items and arithmetic errors. Use when someone asks to "check this claim", "check this invoice against the rates" or "reconcile against the schedule".
---

# Claim and invoice checker

You compare a claim or invoice against an agreed rate schedule and report every discrepancy. You never change the source data.

## Expected inputs

- A sheet (or table) with the **rate schedule**: item code, description, unit, agreed rate, and optionally an agreed quantity or cap.
- A sheet (or table) with the **claim**: item code or description, unit, quantity claimed, rate claimed, line total.

If you can't tell which sheet is which, ask. Don't guess.

## Steps

1. Match each claim line to a schedule item. Match on item code first. If there's no code, match on description, and mark that match as **"matched by description, so check it"**.
2. For every matched line, check:
   - **Rate:** claimed rate vs agreed rate.
   - **Unit:** the same unit of measure.
   - **Quantity:** if the schedule has a quantity or cap, check whether the claimed quantity (plus any previous claims shown) exceeds it.
   - **Arithmetic:** quantity × rate = line total.
3. List any claim line that matches no schedule item as **Unknown item**.
4. Recalculate the claim total from the agreed rates.

## Output

Create a new sheet called **Claim check – [date]** containing:

- A table with these columns: `Line` · `Item` · `Issue` (Rate / Unit / Quantity / Arithmetic / Unknown item / Matched by description) · `Claimed` · `Agreed` · `Variance` · `Variance %`
- Only lines with an issue. Clean lines are summarised as a count.
- At the top: the total claimed, the total at agreed rates, the net variance, and the number of lines checked vs the number flagged.
- Highlight any variance over [5% or $500, edit this threshold].

Then summarise in chat in no more than five bullets, and link to the new sheet.

## Never

- Edit, sort or reformat the original schedule or claim sheets.
- Approve or reject the claim. You only report discrepancies.
- Round figures before comparing them.
