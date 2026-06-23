# Trade-secret three-step ladder

Articles 4(6) → 4(7) → 4(8) for user requests; 5(9) → 5(10) → 5(11) for third-party requests. Recital 31 sets the interpretive frame.

## Default position — disclose with measures

Recital 31 makes the principle explicit:

> "Data holders cannot, in principle, refuse a data access request under this Regulation solely on the basis that certain data is considered to be a trade secret, as this would subvert the intended effects of this Regulation."

The normal route is disclosure with confidentiality measures, not refusal.

## Step 1 — Identify and protect (Art. 4(6) / 5(9))

### Operative requirements

- **Identify** trade-secret data **before disclosure**, including in the relevant metadata.
- **Agree proportionate technical and organisational measures** with the user (or third party) to preserve confidentiality. Examples in the regulation: model contractual terms, confidentiality agreements, strict access protocols, technical standards, codes of conduct.
- **Default outcome:** disclose with the measures in place.

### Practical drafting

The confidentiality-measures agreement should:
- Identify each trade-secret-protected data element by name / category.
- Define permitted use, including any prohibition on derivatives.
- Restrict onward sharing absent further agreement.
- Set technical controls — encryption, access logging, role limits.
- Set organisational controls — role-based access, training, periodic audit.
- Specify breach-notification and remediation duties.

A starting-point template is at `assets/templates/trade-secret-confidentiality-agreement.md`.

## Step 2 — Withhold or suspend (Art. 4(7) / 5(10))

### Triggers (any one)

- No agreement on the measures referred to in 4(6) / 5(9).
- The user fails to implement agreed measures.
- The user undermines the confidentiality of the trade secrets.

### Required actions

- Decision must be **duly substantiated** and provided **in writing** to the user / third party **without undue delay**.
- **Notify the competent authority** designated under Art. 37, identifying:
  - which measures have not been agreed or implemented;
  - where relevant, which trade secrets have had their confidentiality undermined.

### Reversibility

Step 2 is reversible. Sharing resumes once measures are agreed or implemented.

### Practical drafting

The "withhold / suspend" letter should:
- Reference the specific measure(s) not agreed or breached.
- Identify the trade secrets withheld at the level of category, not individual data points.
- State that withholding will continue until measures are agreed or remediation occurs.
- Include the competent-authority notification reference.

Template: `assets/templates/trade-secret-withhold-suspend-letter.md`.

## Step 3 — Exceptional refusal (Art. 4(8) / 5(11))

### Threshold

The data holder must **demonstrate** that it is **highly likely to suffer serious economic damage** from the disclosure of trade secrets, **despite the technical and organisational measures taken by the user / third party** under 4(6) / 5(9).

Recital 31 defines "serious economic damage" as **"serious *and irreparable* economic loss."** The threshold is high.

### Substantiation requirements

The demonstration must be **duly substantiated on the basis of objective elements**, in particular:

- **Enforceability of trade-secret protection in third countries** — if onward disclosure to a non-EU jurisdiction is contemplated, weak enforceability there strengthens the case.
- **Nature and level of confidentiality of the data requested** — how sensitive, how non-public.
- **Uniqueness and novelty of the connected product** — closer to the IP core of the offering increases weight.
- **Cybersecurity impact** (Recital 31) — disclosure that would undermine product cybersecurity may be taken into account.

### Required actions

- **Case-by-case basis.** Never blanket refusal across a category.
- **In writing to the user / third party without undue delay.**
- **Notify competent authority** under Art. 37.

### Limits on Step 3

- Refusal does not displace data-subject GDPR rights (Recital 31 final sentence).
- Refusal must be specific to the data in question, not the request as a whole.
- The user / third party may complain to the competent authority, which decides whether and on what conditions sharing should start or resume.

## Decision flow

```
Request received
   │
   ▼
Are any data elements trade secrets?
   │ No → disclose normally
   │ Yes
   ▼
Step 1 — measures agreed and implemented?
   │ Yes → disclose with measures (default outcome)
   │ No / breached / undermined
   ▼
Step 2 — withhold / suspend in writing + notify CA
   │
   ▼
Are measures still not agreed AND highly likely serious + irreparable economic damage?
   │ No → reattempt Step 1
   │ Yes
   ▼
Step 3 — exceptional refusal in writing + notify CA, case by case
```

## Common defects in refusal letters

The skill flags these in any refusal-letter draft it produces:

1. Skipping Step 1 — refusing without first attempting to agree measures.
2. Skipping Step 2 — going directly to refusal without first withholding / suspending.
3. Citing "trade secret" generically without identifying the specific data elements.
4. Failing to substantiate "serious and irreparable economic loss" with objective elements.
5. Treating the FAQ as authoritative on the threshold.
6. Failing to notify the competent authority (Art. 37).
7. Refusing data-subject GDPR access rights on trade-secret grounds (impermissible per Recital 31).
8. Blanket refusal across a category rather than case-by-case.

## See also

- `references/gotchas.md` — Art. 4(2) safety/security cumulative conditions; interaction with Arts. 4(10), 4(13), 5(3)
