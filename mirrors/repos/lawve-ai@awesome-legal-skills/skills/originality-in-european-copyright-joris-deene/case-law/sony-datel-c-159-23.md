# Sony Computer Entertainment Europe Ltd v. Datel Design and Development Ltd e.a.

## Identification

- **Case number**: C-159/23
- **ECLI**: ECLI:EU:C:2024:887
- **CELEX**: 62023CJ0159
- **Date**: 17 October 2024
- **Court**: CJEU (First Chamber)
- **Reporting judge**: I. Ziemele
- **Advocate General**: M. Szpunar (opinion 25 April 2024)
- **Language of the case**: German
- **Referring court**: Bundesgerichtshof (Germany)
- **Short name**: Sony/Datel, PSP-cheating, Action Replay
- **EUR-Lex (EN)**: https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:62023CJ0159

## Status within this skill — REFINEMENT JUDGMENT for software

> **Scope delimitation**: Sony/Datel addresses two preliminary questions:
>
> 1. Do runtime variables in working memory fall under the protection of art. 1(1)-(3) Directive 2009/24 (the Software Directive)?
> 2. Does modifying those runtime variables constitute "alteration" within the meaning of art. 4(1)(b) of that directive?
>
> Question 1 falls **within** the scope of this skill: it touches the work concept / scope of application of the Software Directive — what is a "form of expression" of a computer program. The Court answers this question negatively and thereby refines the **idea/expression dichotomy for software** as developed by BSA (C-393/09) and SAS Institute (C-406/10).
>
> Question 2 (alteration right, art. 4(1)(b)) was **not answered** by the Court because question 1 was answered negatively. If the content does not fall under protection, modifying it logically cannot constitute infringement. A detailed discussion of exploitation rights is therefore absent. Sony/Datel is therefore for this skill not an exploitation-rights judgment but a scope-of-application judgment.
>
> The judgment introduces no new doctrine. It is an **application and refinement judgment** of the SAS Institute / BSA line. Addressed in the skill as a supporting judgment for the software module, not as a core judgment at the level of BSA or SAS Institute itself.

## Subject matter and category

- **Main category**: software / computer programs — refinement of the "form of expression" test
- **Special contribution**:
  - **The "reproducibility test"** ⭐ (paragraph 37): only elements that allow the program to be **reproduced or subsequently created** are forms of expression
  - **Literal-expression formula** (paragraph 38): protection is limited to "the literal expression of the computer program in those codes"
  - **Runtime variables excluded** (paragraph 51): variables in working memory are elements through which users "make optimal use" of the program — not a form of expression
  - **Anti-monopolisation confirmed** (paragraphs 36, 48): no monopolies on ideas, rules or principles obstructing independent development
- **Applicable legislation**: art. 1(1)-(3) and art. 4(1)(b) Directive 2009/24/EC (Software Directive, previously 91/250/EEC)
- **Relevance for the skill**: ★★★ — *operationally very useful for modern software files (gaming-modding, cheating tools, hooks, plugins, runtime modifications); confirms and refines SAS Institute and BSA*

## Facts in four lines

Sony Computer Entertainment Europe Ltd is the exclusive licensee of the PlayStation consoles and games. Datel Design and Development Ltd developed and sold **Action Replay PSP** (USB software giving users extra game options, e.g., unlimited use of the "turbo" function or early availability of drivers normally accessible only after earning points) and **Tilt FX** (a hardware sensor with software that lets the PSP console be controlled by motion). Both products do **not** modify the source or object code of Sony's games — they only modify the **content of variables** that the games store during execution in working memory. Sony alleged that this was an unauthorised "alteration" of the program; Datel disputed this. The Bundesgerichtshof referred the case.

## Legal questions

1. **Scope of application**: Does modifying runtime variables — without modifying source or object code — constitute infringement of the protection of a computer program under art. 1(1)-(3) Directive 2009/24?
2. **Alteration right**: If so, does this modification constitute "alteration" within the meaning of art. 4(1)(b) Directive 2009/24?

## Operative part

> Article 1(1) to (3) of Directive 2009/24/EC of the European Parliament and of the Council of 23 April 2009 on the legal protection of computer programs must be interpreted as meaning that **the content of the variable data transferred by a protected computer program to the RAM of a computer and used by that program in its running does not fall within the protection conferred by that directive, in so far as that content does not enable such a program to be reproduced or subsequently created**.

Question 2 not answered (see paragraph 53).

## Key reasoning

### Paragraph 33 — *the work-concept test for software confirmed*

> "It is thus apparent from the wording of Article 1 of Directive 2009/24, in particular of paragraphs 2 and 3 thereof, that **'expression in any form' of a computer program is protected, apart from ideas and principles which underlie its constituent elements, provided that such a program is original, in the sense that it is the author's own intellectual creation**."

The software test remains: **form of expression + originality**, with express exclusion of ideas and principles.

### Paragraph 34 — *source and object code as forms of expression* (cross-ref BSA)

> "[T]he Court has held, having regard to Article 1(2) of Directive 91/250, the wording of which is identical to that of Article 1(2) of Directive 2009/24 and the interpretation of which is, therefore, transposable to the latter provision, that **the 'expression in any form' of a computer program is that which permits reproduction in different computer languages, such as the source code and the object code** (judgment of 22 December 2010, Bezpečnostní softwarová asociace, C‑393/09, EU:C:2010:816, paragraph 35)."

### Paragraph 35 — *GUI excluded* (cross-ref BSA)

> "On the other hand, the Court has held that **the graphic user interface of a computer program, which does not enable the reproduction of that program, but merely constitutes one element of that program by means of which users make use of the features of that program, does not constitute a form of expression of a computer program** within the meaning of that provision (see, to that effect, judgment of 22 December 2010, Bezpečnostní softwarová asociace, C‑393/09, EU:C:2010:816, paragraphs 41 and 42)."

### Paragraph 36 — *functionality, programming language and file format excluded* (cross-ref SAS Institute)

> "Likewise, it has found that **neither the functionality of a computer program nor the programming language and the format of data files used in a computer program in order to exploit certain of its functions constitute a form of expression of that program** for the purposes of that provision. **To accept that the functionality of a computer program can be protected by copyright would amount to making it possible to monopolise ideas, to the detriment of technological progress and industrial development** (see, to that effect, judgment of 2 May 2012, SAS Institute, C‑406/10, EU:C:2012:259, paragraphs 39 and 40)."

### Paragraph 37 — *the reproducibility test* ⭐⭐⭐ CORE

> "[I]t is apparent from the wording of Article 1(2) of Directive 2009/24 that **the source code and the object code fall within the concept of 'forms of expression' of a computer program, within the meaning of that provision, since they allow that program to be reproduced or subsequently created, whereas other elements of that program, such as, inter alia, its functionalities, are not protected by that directive**. Nor does that directive protect the elements by means of which users make use of such functionalities, without, however, allowing such reproduction or subsequent creation of the said program."

This is *the* operational core of Sony/Datel: the **reproducibility test**. For an element to qualify as a "form of expression" it must allow the program to be **reproduced** or **subsequently created**. Elements through which the user merely "makes optimal use" of the program, without allowing reproduction, fall outside protection.

### Paragraph 38 — *literal-expression formula*

> "[T]he protection guaranteed by Directive 2009/24 is **limited to the intellectual creation as it is reflected in the text of the source code and object code and, therefore, to the literal expression of the computer program in those codes**, which constitute, respectively, a set of instructions according to which the computer must perform the tasks set by the author of the program."

Important: software protection is a **literal-protection** regime. Non-literal elements (behaviour, logic, algorithms, functionality) fall outside.

### Paragraph 48 — *anti-monopolisation confirmed* (cross-ref 1989 proposal recitals)

> "[T]he legal regime for the protection of computer programs **does not grant monopolies hindering independent development and does not therefore block technical progress**. Moreover, **the competitors of the author of a computer program are free, once they establish through independent analysis which ideas, rules or principles are being used, to create their own implementation of them in order to create compatible products. They may, moreover, build on the identical idea, but may not use the same expression as that of other protected programs**."

This paragraph confirms the **clean-room reverse engineering** doctrine: ideas, rules and principles underlying a program may be studied and reused for compatible products, provided the form of expression is not taken.

### Paragraph 51 — *application to runtime variables*

> "[I]t is apparent that Datel's software, in so far as it changes only the content of the variables transferred by a protected computer program to a computer's RAM and used by that program in its running, **does not, as such, enable that program or a part of it to be reproduced, but presupposes, on the contrary, that that program will be run at the same time**. As the Advocate General stated, in essence, in point 48 of his Opinion, **the content of the variables is therefore an element of the said program by means of which users make use of its features, which is not protected as a 'form of expression' of a computer program** within the meaning of Article 1(2) of Directive 2009/24, which it is for the referring court to verify."

## Doctrinal significance for this skill

### 1. Place in the software doctrine

Sony/Datel fits into a coherent line:

| What is not a form of expression? | Judgment | Paragraph |
|---|---|---|
| Graphical user interface (GUI) | BSA (C-393/09) | 41-42 |
| Functionality | SAS Institute (C-406/10) | 39-40 |
| Programming language | SAS Institute | 39-40 |
| Format of data files (file format) | SAS Institute | 39-40 |
| **Runtime variables in working memory** | **Sony/Datel (C-159/23)** | **37, 51** |

What **is** a form of expression: **source and object code** (BSA paragraph 35, Sony/Datel paragraph 34) + preparatory design material (art. 1(1) in fine Software Directive).

### 2. The reproducibility test as operational criterion

Sony/Datel generalises the doctrine into one workable test (paragraph 37):

> An element is a "form of expression" of a computer program **if and only if** it allows the program to be **reproduced or subsequently created**.

Practical application:

| Type of element | Reproducibility? | Form of expression? |
|---|---|---|
| Source code | Yes | ✅ Protected |
| Object code | Yes | ✅ Protected |
| Preparatory design material (if it can lead to a program) | Indirect (Art. 1.1) | ✅ Protected |
| GUI | No | ❌ Not protected under Software Directive (possibly via InfoSoc) |
| Functionality | No | ❌ Not protected |
| Programming language | No | ❌ Not protected |
| File format | No | ❌ Not protected |
| Runtime variables working memory | No | ❌ Not protected |
| Behaviour of the program | No | ❌ Not protected |
| Algorithms | No | ❌ Not protected (idea) |
| API signatures (function names, parameters) | Debatable | ❌ Generally not protected after SAS Institute |
| Data structures in memory | No | ❌ Not protected |

### 3. Relevance for modern software files

Sony/Datel is operationally particularly relevant for:

- **Gaming modding** and cheating tools (like Datel itself)
- **Game trainers**, plugins, hooks
- **Memory-editing tools**
- **Compatible software** that "grafts" onto another program (cheats, scripts, runtime modifiers)
- **Bot scripts** for games and applications
- **Macro recorders** and automation tools
- **Browser extensions** that manipulate someone else's website via DOM runtime
- **AI tooling** that extracts data from a runtime program

For all such cases Sony/Datel provides the **reproducibility test** as a defence anchor: as long as the tool does not reproduce the source/object code and does not allow subsequent creation of the protected program, it falls outside Software Directive protection.

### 4. What Sony/Datel does not say

Important limitations:

- **Question 2 (alteration right art. 4(1)(b)) was not answered** — what exactly constitutes an "alteration" within the meaning of that provision remains unclear. The Court did not need that question
- **InfoSoc Directive (2001/29) not discussed**: the Commission had argued that art. 2(a) of that directive might also be relevant (reproduction right), but the Court does not address that (paragraphs 26-29). Any protection via the InfoSoc Directive for non-software elements around a computer program remains possible
- **Other legal grounds unaffected**: contractual restrictions (EULA), unfair commercial practices, anti-circumvention of technological protection measures (art. 6 InfoSoc, art. 7(1)(c) Software Directive) can independently constitute infringement
- **Reproduction itself not discussed**: paragraph 29 expressly notes that the Bundesgerichtshof indicated reproduction was not at issue in the main proceedings

### 5. Relationship with clean-room reverse engineering

Sony/Datel paragraph 48 confirms the doctrine that was set out in the recitals of the 1989 proposal:

> "[T]he competitors of the author of a computer program are free, once they establish through independent analysis which ideas, rules or principles are being used, to create their own implementation of them in order to create compatible products."

Cross-references: SAS Institute paragraphs 39-40, recital 15 Software Directive (interoperability), art. 6 Software Directive (decompilation for interoperability).

## Argumentative consequences

### For those wishing to establish copyright protection of an element of a computer program (pro-rightholder)

Sony/Datel raises the burden of proof: only elements that allow the program to be **reproduced or subsequently created** fall under the Software Directive.

Strategies:

1. **Identify source- or object-code taking**: direct or indirect reproduction of code is the safe harbour for the claim
2. **Preparatory design material**: design documents, architectural schemas, pseudocode may fall under art. 1(1) provided they **can later lead to the program** (recital 7)
3. **Consider the InfoSoc Directive**: for non-strict-software elements (manuals, documentation, design documents as literary work, screenshots as artistic work), the InfoSoc Directive is an alternative protection regime — see SAS Institute paragraphs 65-67 for manuals
4. **Consider other legal grounds outside copyright**: contractual restrictions (EULA), unfair commercial practices, anti-circumvention protection, sui generis database right
5. **Contest the "optimal use" classification**: if the opposing party's element does allow reproduction (even partial), it falls under protection

### For those wishing to contest copyright protection (pro-alleged-infringer)

Sony/Datel is for the defence a valuable strengthening of the SAS Institute doctrine.

Attack lines:

#### Attack line 1 — The reproducibility test (paragraph 37) ⭐

Show that the contested element **cannot reproduce** or **subsequently create** the protected program:

- The software/tool/script merely modifies runtime behaviour without copying the code
- The element enables users to **make optimal use** of the program — that falls categorically outside protection
- The analogy with Datel: runtime modifications that only change variables, not the code

#### Attack line 2 — Anti-monopolisation (paragraphs 36, 48)

Rely on the structural argument: copyright must not create monopolies that obstruct independent development or technological progress. Cross-references: SAS Institute paragraphs 39-40, BSA paragraphs 48-49, Brompton paragraph 27.

#### Attack line 3 — Literal-expression boundary (paragraph 38)

Protection is limited to the **literal expression of source and object code**. Non-literal similarities (corresponding behaviour, comparable logic, equivalent functionality) do not lead to infringement.

#### Attack line 4 — Clean-room evidence

Show that the competing product was independently developed on the basis of an analysis of **ideas, rules and principles** — not by taking forms of expression. That is a legitimate development route (paragraph 48).

### Examples of software claims that are weak after Sony/Datel

- **Cheats and game trainers** for commercial games
- **Memory editors** that manipulate runtime data
- **Browser extensions** that modify someone else's website DOM
- **Userscripts** (Greasemonkey-type) for someone else's web services
- **Macro tools** and automation that drive someone else's software
- **Plugins** running in a host program without reproducing the host
- **Bot scripts** and automation for games
- **AI agents** interacting with someone else's interface
- **Anti-cheat circumventors** (caution: art. 6 InfoSoc and art. 7(1)(c) Software Directive on anti-circumvention may apply)
- **Compatible software** developed via clean-room reverse engineering

## Citation form

> CJEU 17 October 2024, C-159/23, *Sony Computer Entertainment Europe / Datel*, ECLI:EU:C:2024:887, paragraph 33 (work-concept test for software: form of expression + originality), paragraph 37 (reproducibility test), paragraph 38 (literal-expression formula), paragraph 48 (clean-room reverse engineering), or the operative part (runtime variables not protected).

## Related case-law

- **BSA** (C-393/09, EU:C:2010:816) — foundational judgment for "form of expression" of software; GUI excluded (Sony/Datel paragraphs 34-35 cite expressly)
- **SAS Institute** (C-406/10, EU:C:2012:259) — functionality, programming language and file format not a form of expression; anti-monopolisation (Sony/Datel paragraph 36 cites expressly)
- **Levola Hengelo** (C-310/17, EU:C:2018:899) — general idea/expression dichotomy (Sony/Datel paragraph 41 cites expressly via TRIPS Agreement)
- **Brompton** (C-833/18, EU:C:2020:461) — anti-monopolisation for physical useful articles (parallel with Sony/Datel paragraph 48)
- **Top System** (C-13/20, EU:C:2021:811) — decompilation of software for error correction; full elaboration outside skill scope (exceptions to exploitation rights)
