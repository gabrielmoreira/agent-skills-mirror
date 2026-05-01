---
name: technical-research
description: "Research a technology, library, API, or approach to inform an architecture or implementation decision. Use when the user says 'research this technology', 'evaluate this library', or 'investigate this approach'."
---

# Technical Research Workflow

## Goal

Produce a structured technical evaluation that gives the team enough information to make a confident build / buy / adopt / reject decision.

---

## Step 1: Define the Research Question

Ask:
1. What technology, library, or approach are we evaluating?
2. What problem is it solving?
3. What are the alternatives we should compare against?
4. Who will use the decision — architect, developer, or product?

---

## Step 2: Evaluation Dimensions

Assess the technology across:

### Maturity & Ecosystem
- Version, release cadence, age of project
- GitHub stars, downloads/week, last commit
- Community size (Stack Overflow, Discord, forums)
- Commercial backing vs. community-only

### Fit Assessment
- Does it solve the stated problem? Fully / partially / needs workaround?
- Known integrations with our current stack
- License compatibility

### Performance & Scale
- Benchmark data (if available) or credible community reports
- Known limits: throughput, latency, memory footprint
- Scale stories: who uses it at production scale?

### Security
- CVE history — any critical vulnerabilities in last 2 years?
- Active security patch cadence
- Compliance considerations (GDPR, SOC 2, HIPAA, etc.)

### Developer Experience
- Time to first working example
- Quality of documentation
- Local dev setup complexity

### Cost
- Licence cost (open source, commercial, seat-based, usage-based)
- Hosting / infrastructure cost implications

---

## Step 3: Comparison Table

| Dimension           | Option A | Option B | Option C |
|---------------------|----------|----------|----------|
| Maturity            |          |          |          |
| Fit                 |          |          |          |
| Performance         |          |          |          |
| Security            |          |          |          |
| Developer XP        |          |          |          |
| Cost                |          |          |          |
| **Overall**         |          |          |          |

---

## Step 4: Recommendation

State clearly:
- **Recommended option** and why
- **Conditions / caveats** that could change the recommendation
- **Risks** to monitor if adopted
- **Suggested next step** (spike, POC, ADR, direct adoption)

---

## Step 5: Output

Save to `{docsPath}/analysis/technical-research-{slug}.md`.
