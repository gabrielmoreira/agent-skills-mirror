---
type: skill
lifecycle: stable
inheritance: inheritable
name: survey-instrument-verification
description: Manuscripts evolve terminology that may not match what was actually administered:
tier: extended
applyTo: '**/*survey*,**/*instrument*,**/*verification*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Survey Instrument Verification

## The Problem

Manuscripts evolve terminology that may not match what was actually administered:

```
Manuscript says: "We measured perceived safety using a 5-point scale"
Raw data shows: 7-point scale with different anchors

Manuscript says: "Participants rated their agreement with 12 items"
Raw data shows: 14 items (2 were dropped but not documented)
```

## The Solution

Before editing survey-related content, verify against raw data.

### 1. Check Scale Parameters

| Manuscript Claims | Verify In Data |
|-------------------|----------------|
| Number of points | Actual min/max values |
| Anchor labels | Codebook or data dictionary |
| Number of items | Count of columns/variables |
| Response options | Unique values in data |

### 2. Verify Item Wording

```
Manuscript Appendix: "How safe do you feel walking at night?"
Actual survey item: "How safe do you feel walking alone at night?"
                                         ^^^^^
                                    Missing word!
```

Compare exact wording:

- Survey instrument file (if available)
- Qualtrics/SurveyMonkey export
- IRB-approved protocol

### 3. Check for "Exactly As Administered" Claims

If an appendix claims "items shown exactly as administered":

```bash
# Line-by-line comparison
diff manuscript-appendix.txt original-survey.txt
```

This claim is a testable hypothesis — test it.

## Verification Checklist

- [ ] Scale points match (5-point? 7-point? Likert?)
- [ ] Anchor labels match ("Strongly agree" vs "Completely agree")
- [ ] Item count matches (after exclusions?)
- [ ] Item wording is verbatim (if claimed)
- [ ] Response coding matches (1-5 vs 0-4)

## When to Apply

- Editing methods sections describing surveys
- Reviewing appendices with survey items
- Any manuscript with quantitative survey data

## Tags

`academic` `surveys` `verification` `data-quality`
