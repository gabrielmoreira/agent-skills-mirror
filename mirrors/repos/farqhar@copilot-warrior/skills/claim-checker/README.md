# S3 · Claim and invoice checker

**What it does:** compares a supplier invoice or progress claim against your agreed rate schedule, line by line. It writes the discrepancies (rate, unit, quantity, arithmetic and unknown items) to a new sheet without touching your source data.

**Licence:** Microsoft 365 Copilot · **App:** Copilot in Excel · **Status:** draft, pending live test · **Last verified:** pending re-test

## When to use it
- Monthly progress claims from subcontractors or suppliers.
- Invoices against a framework agreement or price list.
- Any time someone currently does a manual two-screen check of "claimed vs agreed".

## Setup
1. Download [`SKILL.md`](SKILL.md) and set your highlight threshold (it's in square brackets).
2. Save it in a folder called `claim-checker` inside the **Skills** folder in your OneDrive.
3. Put the rate schedule and the claim as two sheets in the **same workbook**, each formatted as a table with headers. Save the workbook to OneDrive or SharePoint.
4. In the Copilot pane, go to **+ → Skills → claim-checker**, or just ask *"check this claim against the rates"*.
5. **Click every link in Copilot's reply** to see exactly what it created (see [P4](../../prompts/finance-and-commercial.md#add-a-calculated-column-then-click-through-every-change-copilot-made)).

## Limits
- **It is a first pass, not an approval.** A person still signs off the claim.
- It depends on clean tables. A PDF claim needs converting first. [W3](../../workflows/invoice-reader.md) shows how to extract invoice fields automatically.
- Matching by description is fuzzy and is always flagged. Use item codes on both sides if you can.
- It can only check cumulative quantities if previous claims are in the workbook.
- For a recurring, high-volume version, build it as a Copilot Studio agent (attachments now accept Excel files up to 16 MB). Note that it bills on usage.

See [`example-output.md`](example-output.md).
