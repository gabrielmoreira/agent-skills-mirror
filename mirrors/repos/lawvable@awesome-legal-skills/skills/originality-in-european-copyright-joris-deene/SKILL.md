---
name: "originality-in-european-copyright-joris-deene"
description: "a skill that determines whether a given subject matter qualifies for copyright protection under EU law by applying the Cofemel two-step test (concept of work + originality), grounded in fifteen CJEU judgments (including the most recent Mio/Konektra and Calinescu) and the four EU directive provisions on originality. It argues from one of two positions: pro-rightsholder (establishing that the work is original) or pro-alleged-infringer (contesting work status or originality via the four exclusion grounds — technical function, rule-dictated outcome, sweat of the brow, idea/functionality). It includes sector-specific modules for photography, software/GUI, sporting events, databases, applied art, functional texts, derivative works/critical editions, and multimedia works. "
metadata:
  author: "Joris Deene"
  license: "agpl-3.0"
  version: "2026-05-17"
---

# Skill: Originality and Concept of Work in European Copyright (CJEU)

## Purpose

To build a methodical analysis of the question whether a concrete object (text, photograph, software, database, utilitarian article, sound recording, design, …) is **protected by copyright** under EU law, based on the case law of the Court of Justice of the European Union. The skill produces a developed argumentation from one of two positions:

- **Pro-rightsholder** — argue why the object qualifies as a work and is original
- **Pro-alleged-infringer** — argue why the object does not qualify as a work or is not original

> **Version 1.0** — first public release. Integrates the **EU statutory harmonization framework for originality**: verbatim citations of the four directive provisions that explicitly address originality:
>
> - **Art. 1(3) Directive 2009/24/EC** (computer programs — *"author's own intellectual creation"* + *"no other criteria"*)
> - **Art. 3(1) Directive 96/9/EC** (databases — *"author's own intellectual creation"* by *"selection or arrangement"* + *"no other criteria"*)
> - **Art. 6 Directive 2006/116/EC** (photographs — *"author's own intellectual creation"* + *"no other criteria"* + optional protection of *"other photographs"*)
> - **Art. 14 Directive (EU) 2019/790 (DSM)** (works of visual art in the public domain — anti-reviving regime)
>
> These provisions constitute the **statutory floor** of the Cofemel two-step test. The common *"no other criteria shall be applied"* clause in three of the four provisions is the doctrinal basis for the Cofemel rule (C-683/17, paragraph 29) that Member States may not impose additional requirements. The skill makes the doctrinal connection between primary EU law and CJEU case law explicit in a dedicated section *"The EU harmonization framework for originality"* in `01-originality-test.md`. Verbatim texts are also included in the relevant sectoral modules (`02-photography.md`, `03-software.md`, `04-databases.md`, `07-derivative-works.md`).
>
> The doctrinal core consists of fifteen key CJEU judgments and one footnote judgment (Top System): Infopaq (C-5/08), Painer (C-145/10), BSA (C-393/09), FAPL (C-403/08 & C-429/08), Football Dataco (C-604/10), SAS Institute (C-406/10), Levola Hengelo (C-310/17), Cofemel (C-683/17), Brompton (C-833/18), Funke Medien (C-469/17), Renckhoff (C-161/17), Sony/Datel (C-159/23), Mio/Konektra (C-580/23 + C-795/23), Călinescu/FNSA (C-649/23) and Nintendo/PC Box (C-355/12), with Top System (C-13/20) as a footnote mention.

## Scope

| Within scope | Outside scope |
|---|---|
| Whether an object is protected by copyright | Infringement analysis (reproduction, communication to the public) |
| The originality requirement under EU law | Term of protection |
| The EU concept of work (objective identifiability) | Exceptions and limitations (quotation, parody, …) |
| Sector-specific refinements based on CJEU case law | Neighbouring rights |
| Two positions: pro-rightsholder and pro-alleged-infringer | Copyright contracts and licensing |
| | Sui generis database right |
| | Design protection as such (but: cumulation with copyright via Cofemel test is in scope) |
| | National implementation in Member States (this skill addresses EU-level harmonization only; national law must be consulted separately) |

## The two-step test

The CJEU has progressively built the EU concept of work. Since **Cofemel (C-683/17, paragraph 29)** the concept of work is explicitly tested in two cumulative steps.

### Step 1 — Objective identifiability (concept of work in the narrow sense)

Is the object **sufficiently precisely and objectively identifiable**? It must be an expression that is recognisable and unambiguously delimitable for third parties, even though this expression need not be permanent (**Levola Hengelo, C-310/17, paragraph 40**). Subjective, sensory or non-objectifiable experiences (taste, smell, fleeting impression) do not qualify (Levola operative part). The objectivity requirement serves a dual legal-certainty function: both the authorities responsible for enforcement and the third parties against whom protection is invoked must be able to clearly and precisely identify which object is protected (Cofemel paragraphs 32-33).

Full treatment in `methodology/00-work-concept.md`.

### Step 2 — Originality (author's own intellectual creation)

Is the object **original in the sense that it is the author's own intellectual creation** (**Infopaq, C-5/08, paragraph 37**; consolidated in **Cofemel paragraph 29**)? It must be the expression of free and creative choices that reflect the author's personality (**Painer, C-145/10, paragraphs 88-92**), not dictated by technical function (BSA, C-393/09, paragraphs 48-49; Brompton, C-833/18), external rules (FAPL, C-403/08 + C-429/08), convention or banality.

Operational sub-tests:

- **"Own"** — originating from the author, not derived
- **"Intellectual creation"** — the fruit of mental effort; no "sweat of the brow" (Football Dataco, C-604/10; Funke Medien, C-469/17)
- **"Selection, arrangement and combination"** in an original manner (Infopaq paragraph 45)
- **Free and creative choices** that reflect personality through a personal touch (Painer)
- **No exclusion ground**: not dictated by technical function, rules, sweat of the brow or idea/functionality

Full treatment in `methodology/01-originality-test.md`.

Both steps are **cumulative**: an object must satisfy both to qualify as a copyright-protected work (Cofemel paragraph 29).

## File structure

```
originality-in-european-copyright/
├── SKILL.md                                       (this file)
├── methodology/
│   ├── 00-work-concept.md                        [Levola Hengelo + confirmatory cross-references to Cofemel, Brompton, Funke Medien, Mio/Konektra, Călinescu, Nintendo]
│   ├── 01-originality-test.md                    [all 15 judgments + EU harmonization framework (art. 1(3) Dir. 2009/24, art. 3(1) Dir. 96/9, art. 6 Dir. 2006/116, art. 14 Dir. 2019/790 DSM) + Cofemel consolidation + Brompton + Funke Medien + Sony/Datel + Mio/Konektra uniqueness requirement + Călinescu anti-severability + skill irrelevant + public-domain safeguard]
│   ├── 02-photography.md                         [Painer + Renckhoff + Cofemel + verbatim art. 6 Dir. 2006/116]
│   ├── 03-software.md                            [BSA + SAS Institute + Sony/Datel + Nintendo outer limit + Top System footnote + verbatim art. 1(3) Dir. 2009/24]
│   ├── 04-databases.md                           [Football Dataco + verbatim art. 3(1) Dir. 96/9]
│   ├── 05-applied-art.md                         [Cofemel + Brompton + Mio/Konektra (three consolidated key judgments)]
│   ├── 06-text-and-fragments.md                  [Infopaq + Funke Medien + brief mention of Călinescu with cross-reference to 07]
│   ├── 07-derivative-works.md                    [Călinescu/FNSA as key judgment + verbatim art. 14 Dir. 2019/790 DSM anti-reviving regime; room for future case law on translations/adaptations/arrangements]
│   └── 08-multimedia-works.md                    [Nintendo/PC Box as key judgment for complex matter; room for future NFT/AR-VR/AI-multimedia case law]
├── case-law/
│   ├── infopaq-c-5-08.md
│   ├── painer-c-145-10.md
│   ├── bsa-c-393-09.md
│   ├── fapl-c-403-08.md
│   ├── football-dataco-c-604-10.md
│   ├── sas-institute-c-406-10.md
│   ├── levola-c-310-17.md
│   ├── cofemel-c-683-17.md
│   ├── brompton-c-833-18.md
│   ├── renckhoff-c-161-17.md
│   ├── funke-medien-c-469-17.md
│   ├── sony-datel-c-159-23.md
│   ├── mio-konektra-c-580-23-c-795-23.md
│   ├── calinescu-c-649-23.md
│   └── nintendo-c-355-12.md
├── positions/
│   ├── pro-rightsholder.md                       [concept of work + 8 sectors + horizontal lines of argument on the EU statutory floor (four argument lines A-D)]
│   └── pro-alleged-infringer.md                  [concept of work + 8 sectors + horizontal lines of attack on the EU statutory floor (four lines of attack F-I)]
└── workflow.md
```

## Methodology

1. **Identify the object and the sector**. What is it concretely (text, photograph, software, utilitarian article, …)? Which sectoral case law is relevant?
2. **Identify the position**. Is the user arguing from the standpoint of the author/rightsholder, or from the standpoint of the alleged infringer? In case of doubt: ask explicitly.
3. **Consult the relevant case-law files** in `case-law/` for the applicable judgments.
4. **Apply the two-step test** (concept of work → originality) according to `methodology/`.
5. **Develop the argumentation** following the corresponding position file in `positions/`.
6. **Anticipate the counter-argument** from the other position.

> For the detailed procedure see `workflow.md`.

## Anti-hallucination rule

This skill cites **exclusively** from judgments for which a reference file exists in `case-law/`. For each judgment referenced in the analysis, the corresponding file must exist and contain the cited paragraph. For other CJEU judgments or for national case law: write "case reference to be added" and provide only the legal principle.

## Citation form

Standard form for CJEU judgments:

> CJEU [date], C-[case number], *[short name]*, ECLI:[ECLI].

For example: CJEU 16 July 2009, C-5/08, *Infopaq International*, ECLI:EU:C:2009:465.

## Output form

Standard inline in chat. For developed legal argumentation (procedural document, advice, formal notice): offer a markdown artifact.

## Limitations

- **Version 1.0** — covers EU-level harmonization only. National implementation in each Member State is outside scope and must be consulted separately by the practitioner.
- **No factual assessment of the work itself** — the skill provides the legal argumentation structure; the factual assessment of whether an object is objectively identifiable or displays original choices remains the responsibility of the user and ultimately of the court.
- **Strict scope** — the skill addresses only the concept of work (step 1) and originality (step 2). Exploitation rights (reproduction, communication to the public, distribution, **modification right** — including the question left unanswered in Sony/Datel), exceptions and limitations (art. 5 Directive 2001/29, **decompilation under art. 6 Software Directive**), **anti-circumvention of TPMs** (art. 7(1)(c) Software Directive, art. 6 InfoSoc Directive) and the interplay with fundamental rights fall outside scope and belong in separate skills.
