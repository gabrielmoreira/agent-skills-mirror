---
name: mcm-o-guide
description: MCM/ICM 优秀论文写作全流程指南——基于 502 篇历年获奖论文（2004–2024）语料库的结构化分析与评委点评提炼。覆盖：摘要逐句模板、6 类题型模型选择矩阵、25 页页预算分配、图表黄金法则、灵敏度/稳健性分析范式、全文一致性检查清单。当用户准备美赛、写论文、打磨论文、查结构、选模型、做摘要、看评委标准、读优秀论文时使用。也适用于任何需要高质量数学建模论文写作的场景。
---

# MCM/ICM Award-Winning Paper Writing Guide

> [简体中文](SKILL.md) · **English**

> English edition. The canonical skill entry point is [SKILL.md](SKILL.md) (Chinese); this file is a full translation for English-speaking teams.

> Built from corpus statistics and close reading of 502 MCM/ICM award-winning papers
> (Outstanding / Finalist / Meritorious), plus three official judges' commentaries (2009 A/B, 2021 Tips).
> Core goal: help a team produce, within four days, a paper "the judges are willing to read to page 25".

## 0 Quick start

```
Input:  problem letter (A–F), the six sub-questions, the attached data
Output: paper skeleton (with page budget) + summary draft + model list + figure plan
```

Always do this first: **decompose the problem → fill the model-selection matrix → draw the page budget.** See [references/model-matrix.md](references/model-matrix.md).

---

## 1 The judges' view: a three-round knockout

MCM judging runs in three rounds; a paper must survive each one:

| Round | Time per paper | Focus | Top 3 reasons for elimination |
|---|---|---|---|
| **Initial screen** | < 5 min | Is the summary complete + is the paper readable | No numeric conclusion in the summary / broken grammar / no Summary |
| **Screening** | 15–30 min | Whole-paper consistency + model soundness + sensitivity | Assumptions disconnected from the model / no sensitivity / figures not interpreted |
| **Final round** | 1–2 h | Depth of innovation + credibility of results + writing quality | Conclusions without quantitative support / figures inconsistent with the text / no discussion of limitations |

> Judges' own words (2009 A): *"It is absolutely essential that a paper be well written and have a clear, concise summary to make it past the initial round."*

**Strategy: round one reads the summary; round two checks whether summary and body agree; round three judges model depth. The summary decides your fate.**

---

## 2 The Summary — one page decides everything

### 2.1 Corpus baselines

| Metric | Median | p25–p75 | Outstanding preference |
|---|---|---|---|
| Summary length (words) | 437 | 350–520 | 400–500, with 20–35 concrete numbers |
| Sentences containing numbers | ≥ 6 | 4–9 | at least one quantitative result per task |
| Keywords | 4–5 | 3–6 | include the model name (e.g. GIID, CA, BDS) |

### 2.2 Sentence-by-sentence template (the 10-sentence golden structure)

```
Sentence 1:  background pain point + name this paper's goal (1 sentence)
Sentence 2:  data preprocessing / classification / parameter estimation (1–2 sentences)
Sentences 3-4: Task 1: model name + method chain + core result (with numbers)
Sentences 5-6: Task 2: method + core result (with numbers)
Sentence 7:  Task 3: method + core result (with numbers)
Sentence 8:  Task 4/N: method + core result (with numbers)
Sentence 9:  sensitivity-analysis conclusion
Sentence 10: strengths / limitations / conclusion (1 sentence)
```

**Anatomy of a 2023 A Outstanding summary (real example):**

| Sentence | Rhetorical move | Numbers | Delivered in |
|---|---|---|---|
| 1 | Field pain point → naming this paper's model (GIID) | none | Sec 3 |
| 2 | Data preprocessing | 5 species, 3 categories | Sec 2.3 |
| 3-4 | Task 1: LV model → validation result | "shown in Figure 7" | Sec 3.4 |
| 5-6 | Task 2: TV/CoV/SW/Pielou → trends | "increases then decreases", "at least two" | Sec 4.1 |
| 7 | Task 3: comparison of 3 combinations | "moderate differences" | Sec 4.2 |
| 8 | Task 4: drought frequency/intensity | "complementary effect becomes stronger" | Sec 5.1 |
| 9 | Task 5-6: habitat/pollution → conservation measures | — | Sec 5.2–5.3 |
| 10 | Sensitivity + strengths/weaknesses + conclusion | — | Sec 6–7 |

### 2.3 Pitfalls in summary writing

| Pitfall | What to do instead |
|---|---|
| Long background buildup | 1–2 sentences of setup, then straight into the method |
| "The results are shown in Figure X" with no numbers | State the key value (e.g. "CoV decreased by 58.5%") |
| Naming a model without saying what it solved | "For Task 2, we calculated total biomass, CoV and the S-W index to evaluate vigor, stability and evenness respectively" |
| No keywords | 4–5 keywords, including the model name |

---

## 3 Paper skeleton and page budget

### 3.1 The golden 25-page split (median of 2021–2024 Outstanding papers)

| Section | Pages | Share | Function | Must contain |
|---|---|---|---|---|
| Summary + contents | 1.5–2 | 8% | First impression | numeric conclusions, method chain, keywords |
| Introduction (background + restatement + literature) | 2–3 | 10% | Show understanding | problem restatement, literature map |
| Assumptions + notation + data | 2–3 | 10% | Legitimise the model | assumptions with reasons, parameter-source table |
| **Core model + results** | **10–13** | **45%** | Answer the question | equations, algorithms, figures, conclusions |
| Sensitivity analysis | 1–2 | 6% | Model credibility | parameter perturbation + change in results |
| Strengths & weaknesses + conclusion | 1–1.5 | 5% | Self-assessment | ≥ 3 strengths + 2 limitations |
| References + appendix | 1–2 | 8% | Citation compliance | one-to-one with in-text citations |
| Memo/Letter (if required) | 0.5–1 | 4% | Mandatory for policy problems | the format the prompt requires |

### 3.2 Figure and table quotas

| Problem type | Median figures | Median tables | Median equations | Median references |
|---|---|---|---|---|
| A (continuous) | 12 | 3 | 8 | 10 |
| B (discrete) | 8 | 2 | 1 | 10 |
| C (data) | 10 | 5 | 6 | 8 |
| D (network) | 10 | 3 | 9 | 11 |
| E (environment) | 8 | 4 | 16 | 12 |
| F (policy) | 11 | 3 | 6 | 12 |

**Golden rule: at least one figure or table every two pages, and every figure must be explicitly interpreted in the text.**

---

## 4 Model-selection matrix

Details in [references/model-matrix.md](references/model-matrix.md). Quick reference:

| Problem type | Primary model family | Supporting models | Validation |
|---|---|---|---|
| A continuous / mechanistic | ODE/PDE / cellular automata | optimisation + numerical simulation | analytic-solution comparison + sensitivity |
| B discrete / combinatorial | graph theory / integer programming / Markov | heuristics | comparison with exact solutions on small instances |
| C data insight | ML (XGBoost/LSTM/CNN) + statistics | feature engineering + cross-validation | benchmark comparison + AUROC/RMSE |
| D network / operations | network flow / community detection / AHP / TOPSIS | optimisation + simulation | scenario comparison + sensitivity |
| E environmental assessment | entropy weighting / TOPSIS / AHP / composite index | scenario simulation + PCA | weight sensitivity + cross-validation |
| F policy analysis | game theory / system dynamics / AHP | scenario analysis + cost-benefit | scenario stress test + sensitivity |

### 4.1 Principles for designing a model chain

1. **At most two independent model families per sub-question**; different approximation orders of the same mechanism count as one family
2. **Models must be coupled**: the output of one is the input of the next, or they share parameters/data
3. **A baseline is mandatory**: a simple model as a control group, proving the added value of the complex one
4. **Name your model**: e.g. GIID, BDS — judges like a memorable label

---

## 5 Assumptions and data

### 5.1 Assumption-writing template (used by 94%+ of Outstanding papers in the corpus)

```
**Assumption N: [statement]**
Justification: [literature / logic / reason for simplification]
Where used: [which model or equation it enters]
```

**Key rules:**
- 4–7 assumptions, each with a justification
- Global assumptions go in Sec 2; model-specific assumptions go in that model's subsection
- **Assumptions must be referenced in the body** ("According to Assumption 2, ...")
- The Strengths/Weaknesses section must discuss the limitations of the assumptions

### 5.2 Transparency of parameter sources

| Source type | How to write it | Example |
|---|---|---|
| Direct from the literature | "According to [7], parameter X = Y" | growth rate, mortality rate |
| Own estimate | give the estimation formula and process | "r = ΔVolume / (Volume × 30 days)" |
| Empirical setting | give the range and argue plausibility | "α ∈ [0.01, 0.1], tested in sensitivity" |
| Fitted | state the fitting method + R²/residuals | "fitted by least squares, R² = 0.94" |

---

## 6 Golden rules for figures and tables

### 6.1 Every figure must be interpreted in the text

**Wrong:** "The results are shown in Figure 5."
**Right (2023 A Outstanding paper):**

> *"With results in both figures, we can identify several remarkable phenomena:*
> *• The biomass of both plants are influenced by the periodic weather change...*
> *• During the recovery process of the drought, the H.nepalensis recovers relatively quickly..."*

### 6.2 Matching figure type to purpose

| What you must prove | Recommended chart | Quantity |
|---|---|---|
| Model validation (vs data / analytic solution) | overlaid line chart | ≥ 1 |
| Parameter sensitivity | multi-line chart / heatmap (3–5 parameter sets) | ≥ 1 group (3 charts) |
| Task conclusion (numeric comparison) | bar/box plot with value labels | ≥ 1 per task |
| Model framework / workflow | flow chart / mind map | ≥ 1 |
| Data exploration / distribution | scatter / map / histogram | ≥ 1 for C, D, E |
| Scenario comparison | side-by-side panels (baseline vs ours) | ≥ 1 group (2–3 charts) |

### 6.3 Figure checklist (all mandatory)

Every figure/table needs: a number + a caption + a citation in the text + an interpretation paragraph.
Corpus statistics: Outstanding papers average 14 figures (2021+); Meritorious papers only 6.

---

## 7 Sensitivity analysis — the ticket to Outstanding

### 7.1 Corpus data

| Metric | 2014–2016 | 2021–2024 |
|---|---|---|
| Has sensitivity analysis | 58–68% | 82–93% |
| Has robustness / validation | 11–42% | 32–49% |
| Discusses strengths/weaknesses | 50–73% | 62–84% |

> Judges' own words: *"Every year the judges explicitly discuss the issue of sensitivity and stability. The few teams that make a concerted effort to explore this aspect of their model will almost always stand out."*

### 7.2 Three patterns of sensitivity analysis

**Pattern A: single-parameter sweep (most common)**
```
Pick 3–5 key parameters → 3–5 values each (baseline ±20%, ±40%)
→ re-run the model → comparison figure → conclusion sentence: "The model is sensitive/robust to X"
```

**Pattern B: multi-scenario stress test**
```
Baseline scenario → severe scenario (×2 stress) → extreme scenario (×5 stress)
→ compare the rate of change of key metrics
```

**Pattern C: initial-condition perturbation + confidence intervals (advanced, common in problem C)**
```
Perturb the initial distribution/parameters N times → compute KL divergence / confidence intervals
→ conclusion: "The model is insensitive to reasonable perturbations"
```

**Must include:**
- which parameters were swept and why these
- the perturbation range and its basis
- how it is presented (figure + table)
- **a conclusion sentence**: "The model is sensitive/robust to X, so X must be measured accurately in practice"

---

## 8 Whole-paper consistency checklist

One of the qualities judges value most. Check every item before submitting:

### 8.1 Assumption consistency
- [ ] Assumptions mentioned in the summary exist in the body and match
- [ ] Every assumption used in the models appears in the assumption list
- [ ] Limitations discussed in Strengths/Weaknesses map to specific assumptions

### 8.2 Numeric consistency
- [ ] Numeric conclusions in the summary match the results section exactly
- [ ] Values in figures/tables match the values cited in the text
- [ ] Symbols in the notation table match their use in equations

### 8.3 Structural consistency
- [ ] The table of contents matches the actual section titles
- [ ] Figure/table numbering is continuous and correctly cited
- [ ] Every reference is cited in the text — no orphan citations

### 8.4 Task-coverage consistency
- [ ] Each sub-question has an explicit "Answer to Task N" paragraph
- [ ] No sub-question is missed (judges eliminate for this)
- [ ] Memo/Letter (if required) is its own section in the required format

---

## 9 Writing checkpoints

### Stage 1: skeleton (1–2 hours after the problem drops)
1. [ ] Break the six sub-questions into a sentence-level checklist
2. [ ] Fill in the model-selection matrix (Sec 4)
3. [ ] Draw the page-budget table (Sec 3)
4. [ ] Write the summary draft (structure only, numbers left blank)

### Stage 2: models landed (once the coder has results)
1. [ ] ≥ 1 conclusion figure + 1 interpretation paragraph per task
2. [ ] Parameter-source table complete
3. [ ] Assumptions + justifications complete
4. [ ] Summary filled with concrete numbers

### Stage 3: validation and polish (6–8 hours before submission)
1. [ ] Sensitivity analysis complete (≥ 3 parameters × 3 values)
2. [ ] Whole-paper consistency check (Sec 8 list)
3. [ ] ≥ 3 strengths + ≥ 2 weaknesses
4. [ ] Uniform reference format, one-to-one in-text citations
5. [ ] Final summary review: model name, one quantitative conclusion per task, keywords

### Stage 4: compliance (1 hour before submission)
1. [ ] ≤ 25 pages (including summary/contents/appendix/references)
2. [ ] Team number + page number in every page header
3. [ ] No team name, school name or member names
4. [ ] PDF < 17 MB
5. [ ] File name = team-number.pdf
6. [ ] AI-use report (if AI tools were used)

---

## 10 Common fatal mistakes

| Mistake | Round eliminated | Frequency (all teams) |
|---|---|---|
| Summary without concrete numeric conclusions | Initial screen | ~40% |
| Missing sub-question | Screening | ~25% |
| Figures never interpreted in the text | Screening | ~30% |
| No sensitivity analysis | Screening | ~35% |
| Assumptions disconnected from the model | Final round | ~20% |
| Chaotic reference formatting | Final round | ~15% |
| Internal inconsistency (summary vs body numbers) | Final round | ~10% |

---

## 11 Advanced: the gap from Meritorious to Outstanding

Based on the corpus comparison, the key differences:

| Dimension | Meritorious | Outstanding |
|---|---|---|
| Numeric density in the summary | 10–15 numbers | 20–35 numbers |
| Share of figures interpreted | 60–70% | 90%+ |
| Depth of model coupling | independent models, results stitched together | data/parameter flow between models |
| Baseline comparison | none or trivial | baseline + quantified improvement |
| Depth of sensitivity | 1–2 parameters | 3–5 parameters + multiple scenarios + conclusion sentence |
| Honesty about limitations | generic | specific to assumptions/parameters/models + path forward |
| Model naming | none | yes (e.g. GIID, BDS) |
| Flow chart | optional | mandatory (Our Work / Model Framework) |

---

## 12 Advanced modules

### 12.1 Writing Strengths & Weaknesses

Details in [references/strengths-weaknesses.md](references/strengths-weaknesses.md)

**Key points:**
- ≥ 3 strengths, each in three parts: **what we did + effect + why it works**
- ≥ 2 weaknesses, each in three parts: **limitation + impact + path forward**
- 90%+ of weaknesses must include a path forward
- Assumptions mentioned in the strengths must match the assumption list

**Real Outstanding strength (2023 A):**
```
• We described the mechanics of the interaction between plant and environment in detail.
  Instead of making the too crude assumption that plant growth rates are directly proportional
  to precipitation, we modeled the interaction by assuming different plants absorb water from
  the soil at different rates. This makes our model more realistic and more convincing.
```

### 12.2 Writing the Introduction

Details in [references/introduction-guide.md](references/introduction-guide.md)

**Key points:**
- 2–3 pages, four subsections
- Problem Background: 1 figure + 1 concrete number + 1 sentence of motivation
- Restatement: list all six sub-questions as bullets
- Literature Review: a literature map (comparison of three method families)
- Our Work: flow chart + model list (3–5 bullets)

### 12.3 Memo / Letter (problem F)

Details in [references/memo-letter.md](references/memo-letter.md)

**Key points:**
- Memo/Letter must be its own section after the references
- Complete format: TO / FROM / DATE / RE
- ≥ 3 recommendations, each backed by data (citing results from the body)
- Recommendations must be actionable (place/time/action/effect)
- Sign as "Team #[number]", no personal information

### 12.4 Model-innovation strategies

Details in [references/model-innovation.md](references/model-innovation.md)

**Six innovation strategies:**
1. **Mechanism coupling**: couple the output of one model to the input of another (e.g. the population–environment coupling of 2023 A)
2. **Multi-scale modelling**: build models at different temporal/spatial scales (e.g. the micro–macro coupling of 2021 C)
3. **New indicators**: construct indicators for the problem (e.g. CoV, Shannon–Wiener index)
4. **Baseline comparison**: design a control group and quantify the improvement (e.g. the with/without comparison of 2024 A)
5. **Data-driven innovation**: let patterns found in the data drive the model (e.g. 2021 C fitting population from reported data)
6. **Algorithmic improvement**: targeted improvements to a classic algorithm (e.g. the reversed PageRank of 2021 D)

**The innovation gap from M to O:**
- Meritorious: 2–3 independent models, no naming, implicit innovation
- Outstanding: 3–5 coupled models, named (e.g. GIID), explicit innovation claims

---

## 13 Quick reference

### 13.1 Summary template (fill in the blanks)

```
[Background] As [phenomenon/problem] becomes [trend/severity], [subject] faces [challenge].
To explore this phenomenon, we develop the [model name] model to [goal].

Before modeling, we [data preprocessing: classified/estimated/collected].
Parameters are set based on [source].

For Task 1: We established [model name] based on [underlying theory], incorporating
[key innovation]. The results show that [concrete numeric conclusion].

For Task 2: We calculated [metric 1], [metric 2] and [metric 3] to evaluate
[dimension]. Results indicate that [concrete trend/value].

For Task 3: We compared [N] scenarios/combinations and found that
[concrete conclusion with numbers].

For Task 4: We varied [parameter] and the results show [concrete trend].

Finally, sensitivity analysis on [parameter] confirms model stability.
We also discuss strengths, weaknesses and [conclusion/recommendation].

Keywords: [model name], [keyword 2], [keyword 3], [keyword 4]
```

### 13.2 Sentence bank

| Situation | Sentence pattern |
|---|---|
| Introducing the model | "To simulate/predict/evaluate [X], we developed [model name] based on [theory]" |
| Linking tasks | "For Task N, we [action]. The results are shown in Figure/Table X." |
| Quantified conclusion | "The [metric] [increased/decreased] by [X]%, reaching [Y] under [conditions]" |
| Comparing results | "Compared with [baseline], our model achieves [X]% improvement in [metric]" |
| Sensitivity conclusion | "When [parameter] varies within [range], the output changes by [X]%, indicating the model is [sensitive/robust] to [parameter]" |
| Strength | "We [did X], which makes the model more [realistic/convincing/accurate]" |
| Limitation | "We [simplified X], which may cause [bias]. Future work could [improvement]" |
| Assumption | "Assumption N: [statement]. Justification: [reason]. This assumption is used in [model/equation]" |

### 13.3 Highlights from the judges' commentaries

- *"The summary is the first thing that a judge will read. It is the first impression, and it imparts the expectations for the whole paper."* — 2009 A
- *"Teams that managed to maintain some level of consistency stood out from the entries."* — 2009 A
- *"The few teams that examined a range of values for the parameters in their models immediately caught the judges' attention."* — 2009 A
- *"The best papers not only list trustworthy resources but also document their use throughout the paper."* — 2009 B
- *"The summary should motivate the reader to read the paper. It must not merely restate the problem, but indicate how it was modeled and what conclusions were reached."* — 2009 B

---

## Resource files

| File | Purpose |
|---|---|
| [references/model-matrix.md](references/model-matrix.md) | Model-selection matrix, baseline recommendations and validation for 6 problem types |
| [references/summary-template.md](references/summary-template.md) | Sentence-by-sentence summary template + full breakdowns of 5 Outstanding summaries |
| [references/checklist.md](references/checklist.md) | Whole-paper consistency checklist + pre-submission review list |
| [references/judge-commentary.md](references/judge-commentary.md) | Full text of 3 official judges' commentaries + structured extraction |
| [references/strengths-weaknesses.md](references/strengths-weaknesses.md) | Strengths/Weaknesses templates + Outstanding examples |
| [references/introduction-guide.md](references/introduction-guide.md) | Introduction guide + 4-subsection template |
| [references/memo-letter.md](references/memo-letter.md) | Memo/Letter format template + recommendation writing for problem F |
| [references/model-innovation.md](references/model-innovation.md) | 6 model-innovation strategies + the M-to-O gap |
| [references/end-to-end-case.md](references/end-to-end-case.md) | End-to-end case A: 2023 drought (continuous/mechanistic) |
| [references/end-to-end-case-B.md](references/end-to-end-case-B.md) | End-to-end case B: 2022 water resources (discrete/optimisation) |
| [references/end-to-end-case-C.md](references/end-to-end-case-C.md) | End-to-end case C: 2021 bumblebees (data insight) |
| [references/end-to-end-case-DEF.md](references/end-to-end-case-DEF.md) | End-to-end cases D/E/F: network/environment/policy (+ six-problem overview table) |
| [references/page-by-page.md](references/page-by-page.md) | 25-page dissection (modelled on the 2023 A Outstanding paper: what each page does/holds/earns) |
| [references/advanced-techniques.md](references/advanced-techniques.md) | Advanced handbook: 6 sensitivity methods / 6 validation methods / visualisation decision tree / equation conventions / technique combos per problem type |
| [references/top-award-strategy.md](references/top-award-strategy.md) | 🏆 Top-award strategy: data insights from 502 real papers (summary numbers / figures / sensitivity) |
| [references/top-paper-anatomy.md](references/top-paper-anatomy.md) | 🏆 Top-paper anatomy: 2022 C Bitcoin strategy (117 numbers, 17 figures, page by page) |
| [playbooks/modeling-playbook.md](playbooks/modeling-playbook.md) | 🧮 Modeller upskilling (problem decomposition / assumptions / model library / validation) |
| [playbooks/coding-playbook.md](playbooks/coding-playbook.md) | 💻 Coder upskilling (Python/Matlab/Lingo templates + figure conventions) |
| [playbooks/writing-playbook.md](playbooks/writing-playbook.md) | ✍️ Writer upskilling (summary first / academic English / typesetting) |
| [playbooks/research-playbook.md](playbooks/research-playbook.md) | 📚 Research upskilling (literature search / dataset sources / research ideas) |
| [templates/latex-template.tex](templates/latex-template.tex) | 📄 Ready-to-compile LaTeX skeleton (compliant 25 pages, with guiding comments) |
| [templates/markdown-template.md](templates/markdown-template.md) | 📄 Markdown skeleton (convert to DOCX/PDF with Pandoc) |
| [templates/README.md](templates/README.md) | Template usage notes |
| [references/quick-reference-card.md](references/quick-reference-card.md) | ⚡ Quick-reference card (the 30-minutes-before-submission check) |
| [references/team-workflow.md](references/team-workflow.md) | 👥 Team workflow guide (4-day contest) |
| [references/self-evaluation.md](references/self-evaluation.md) | 📊 Paper self-assessment rubric (100 points) |
| [references/sentence-patterns.md](references/sentence-patterns.md) | 📝 Academic sentence bank (mined from 498 papers) |
| [references/common-errors.md](references/common-errors.md) | ❌ Common-error gallery (what not to do) |
| [scripts/](scripts/) | 🔧 Automation scripts (PDF extraction + consistency check + parameter sweep + benchmarking) |

> Note: the topic files under `references/`, `playbooks/` and `templates/` are currently written in Chinese; this English edition covers the main skill file.

---

*This skill is built on a corpus of 502 papers (449 valid papers with ≥ 5 pages of body text) and official judges' commentaries.
Statistical baseline: Outstanding / Finalist / Meritorious papers, 2014–2024.
Last updated: 2026-01.*
