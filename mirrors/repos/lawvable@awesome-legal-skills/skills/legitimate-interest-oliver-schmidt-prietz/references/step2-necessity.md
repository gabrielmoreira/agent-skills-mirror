# Step 2: Necessity Analysis — Detailed Reference

## Legal Standard

Processing must be **strictly necessary** for the purposes of the legitimate interest pursued (C-26/22 *SCHUFA*, para. 88; C-252/21 *Meta*, para. 126).

"Necessary" has an **independent meaning in EU law** (C-524/06 *Huber*, para. 52) — it does NOT mean merely "useful" or "convenient" (EDPB Guidelines 1/2024, para. 28).

---

## The Necessity Test

### Core Question

> "Could the legitimate interest be achieved equally effectively by other means that are less intrusive to the data subjects' fundamental rights and freedoms?"
>
> — C-252/21 *Meta*, para. 108

If YES → processing is NOT necessary → Art. 6(1)(f) cannot be used.

### Practical Steps

**1. Define the minimum processing required**

For each data category:
- What specific role does this data play in achieving the interest?
- Could a less identifying data type serve the same function?
- Could aggregated or anonymised data achieve the same result?

**2. Identify alternatives**

| Alternative Type | Example | Assessment |
|-----------------|---------|------------|
| Less data | Fewer data categories | Does the reduced set still achieve the interest? |
| Less identifying | Pseudonymised instead of directly identifiable | Would this suffice? |
| Aggregated | Statistical summaries instead of individual records | Would aggregate data serve? |
| Different method | Achieving the interest without personal data at all | Is this feasible? |
| Narrower scope | Processing fewer data subjects | Would a subset suffice? |

**3. Apply data minimisation (Art. 5(1)(c))**

The CJEU expressly links necessity under Art. 6(1)(f) to the data minimisation principle (C-252/21, para. 109; C-621/22 *KNLTB*, paras. 42-43, 51-52):
- Data must be adequate, relevant, and limited to what is necessary
- Each processing operation must be in so far as "strictly necessary"

---

## Special Considerations

### Controller vs. Third-Party Interest

It is generally **easier** for a controller to demonstrate necessity for its own interest than for a third party's interest (EDPB Guidelines, para. 30). This is because:
- The controller has direct knowledge of its own operational needs
- Processing for third-party interests is less expected by data subjects
- The causal link between processing and interest achievement is typically less direct

### Intersection with Step 3

In some circumstances, the necessity test and balancing test may merge, particularly where assessing whether less intrusive means exist requires weighing rights and interests (C-26/22 *SCHUFA*, para. 92).

If during Step 3 (balancing) certain data categories are found to create disproportionate impact, the controller should loop back to Step 1 or Step 2 to reconsider whether the interest or the scope of processing needs adjustment (EDPB Guidelines, para. 42).

---

## Documentation Checklist

For each processing activity under Art. 6(1)(f), document:

- [ ] Complete list of personal data categories processed
- [ ] Justification for each data category (why strictly necessary)
- [ ] Alternatives considered and reasons for rejection
- [ ] Data minimisation analysis outcome
- [ ] Storage/retention periods and justification
- [ ] Technical measures supporting minimisation (pseudonymisation, aggregation, etc.)

---

## Red Flags for Necessity Failure

| Indicator | Risk |
|-----------|------|
| Processing "all available data" without category-specific justification | Likely fails necessity |
| No alternatives analysis documented | Fails accountability |
| Data collected "just in case" for future use | Speculative — fails both necessity and Step 1 |
| More data processed than comparable controllers use for same purpose | Suggests less intrusive means exist |
| Processing could achieve 90% effectiveness with 50% of the data | Proportionality concern |
| Retention period exceeds what's needed for the interest | Fails data minimisation |
