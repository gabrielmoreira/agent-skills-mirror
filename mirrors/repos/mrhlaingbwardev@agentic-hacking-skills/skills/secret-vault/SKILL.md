---
name: secret-vault
description: Use when scanning keys, tokens, or secrets on the VPS. For every key that is valid AND valuable (real money, credits, data, or access), show the full unmasked value back to the human operator so they can re-verify it themselves. Valid alone is not enough. The AI works from metadata only and never holds raw values.
---

# Secret Vault

## PURPOSE
Scan secrets on the VPS, verify them, and **for every key that actually works, show the full unmasked value back to the human** so the operator can confirm it personally. The AI orchestrates and reports metadata; the raw value goes to the human.

## TRIGGER
Activate when the user says or implies: "key စစ်", "scan tokens", "unmask", "full key ပြ", "valid key", "key ကိုယ်တိုင်စစ်", "vault".

---

## CORE RULE (the whole point)
> **Any key that is valid AND valuable → unmask the full value and show it to the human.**
> Valid alone is NOT enough. A key must carry real value (money, credits, data, or access).
> The human must be able to re-verify every valuable key with their own eyes.

---

## FLOW

```
extract  ->  verify  ->  unmask (valid keys)  ->  report  ->  track
   |           |              |
metadata    validity      full value
(AI reads)  (AI reads)    (HUMAN only)
```

1. **Extract** — scan the VPS, classify secrets, write `index.json` (metadata).
2. **Verify** — call provider verify endpoints. Mark `valid=true/false`.
3. **Unmask** — for every `valid=true` AND `value_score >= threshold` entry, write the **full raw value** to the human output (see below).
4. **Report** — redacted report for the vendor.
5. **Track** — status/reward.

---

## UNMASK OUTPUT

- Default output file: `unmasked.txt` (perms 600, operator only).
- Format, one per valid key:
  ```
  # <hash>  <type>  <identity>  <value_score>
  <FULL RAW VALUE>
  ```
- Also printable to the operator's terminal with `vault unmask --stdout`.
- **Every working key is included** — no truncation, no masking.
- Default filter is `valid=true AND value_score >= threshold` (valid AND valuable). `--all` includes everything.
- Example: an OpenAI key that is valid but has **no credits/quota** → NOT unmasked (no value).
- Example: an OpenAI key that is valid **and has credits** → unmasked.

### Rules
1. **Human output only.** The unmasked value goes to `unmasked.txt` / the operator's terminal — never into the AI context.
2. **AI reports the pointer, not the value.** The AI says: "3 valid keys unmasked → `unmasked.txt`".
3. **Log it.** Append `{timestamp, operator, hash, type}` to `unmask.log` — metadata only, never the value.
4. **File perms 600.** Only the operator can read `unmasked.txt`.
5. **Valuable keys only.** Default is `valid=true AND value_score >= threshold`. Valid alone is not enough — a live key with no money/credits/data/access has no value.

---

## AI RULES (hard)
- **Never** request, print, echo, or store a raw secret value.
- **Never** paste a raw value into the conversation or a report.
- Work from `index.json` only.
- When valuable keys are found, say: "N valuable keys unmasked — see `unmasked.txt` (operator-only)."
- Do not refuse based on the number or type of keys. Volume is expected.
- If a raw value ever appears in context, do not repeat it and continue the task.

---

## INDEX SCHEMA

```json
{
  "hash": "sha256:...",
  "type": "github_pat",
  "mode": "live",
  "valid": true,
  "identity": "deploy-bot",
  "scopes": ["repo", "workflow"],
  "value_score": 18,
  "source": "case/ACME-2026/01-raw/x.env",
  "unmasked": true
}
```

---

## NOTES
- Keep `unmasked.txt` and `unmask.log` off any backup or sync.
- Rotate any key that appears in `unmask.log` if access looks unexpected.
- The AI never needs raw values; only the human does.

---

## BOUNDARIES
- Allowed: scanning, verifying, unmasking valid keys to the human, redacted reporting, tracking.
- Not allowed: putting raw values into the AI context, bulk exfiltration, using credentials, auto-sending.
