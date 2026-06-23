# Methodology — Software and Graphical User Interfaces

> **Version 1.0** — based on BSA (C-393/09, ECLI:EU:C:2010:816), SAS Institute (C-406/10, ECLI:EU:C:2012:259), Sony/Datel (C-159/23, ECLI:EU:C:2024:887) and Nintendo / PC Box (C-355/12, ECLI:EU:C:2014:25, outer boundary Dir. 2009/24 — developed in `08-multimedia-works.md`), with a footnote mention of Top System v Belgian State (C-13/20, ECLI:EU:C:2021:811) and verbatim text of art. 1(3) Directive 2009/24/EC. For the EU harmonization framework for originality as a whole: see `01-originality-test.md`.

## Two-track system: lex specialis for the computer program, general copyright for the rest

For software outputs, EU law provides a **two-track system**:

### Track 1 — Software Directive (91/250/EEC, codified in 2009/24/EC)

Protects only **that which enables the reproduction of the computer program itself** (BSA paragraph 38):

- Source code
- Object code
- Preparatory design material, provided a program may result from it

**Originality threshold**: art. 1(3) Directive 91/250/2009/24:

> "A computer program shall be protected if it is original in the sense that it is the author's own intellectual creation. No other criteria shall be applied to determine its eligibility for protection."

Two operational components:

| Component | Content |
|---|---|
| **"Author's own intellectual creation"** | Originality test — expressly identified by the CJEU in Infopaq paragraph 35 as the basis for the horizontally harmonized formula |
| **"No other criteria"** | Member States cannot apply an additional threshold. Doctrinal basis for the Cofemel rule (overarching treatment in `01-originality-test.md`) |

**Idea/expression dichotomy expressly in the legislation** (art. 1(2) Directive 91/250/2009/24):

> "Protection in accordance with this Directive shall apply to the expression in any form of a computer program. Ideas and principles which underlie any element of a computer program, including those which underlie its interfaces, are not protected by copyright under this Directive."

### Track 2 — InfoSoc Directive (2001/29/EC)

Protects everything that **does not enable the reproduction of the program itself** but is nevertheless a work within the meaning of art. 2(a):

- Graphical user interface (GUI) — BSA operative part question 1
- Screen displays, layout, icon style
- Visual elements, animations, themes
- Documentation, manuals (as text)

**Originality threshold**: Infopaq + Painer — author's own intellectual creation; free creative choices; personal touch.

### Overview table

| Element | Track | Protection? |
|---|---|---|
| Source code | 1 (Software Directive) | Yes, if author's own creation |
| Object code | 1 | Yes, if author's own creation |
| Preparatory design material | 1 | Yes, if author's own creation and capable of resulting in a program |
| GUI | 2 (InfoSoc) | Yes, if author's own intellectual creation (BSA paragraph 46) |
| Icons / animations | 2 | Yes, if Infopaq/Painer test met |
| Programming language | None | No — idea, not expression (later: SAS Institute, C-406/10) |
| File format (general concept) | None | No — idea |
| API functions / functionality | None | No — idea (SAS) |
| Algorithm as such | None | No — principle (art. 1(2)) |
| Runtime variables in working memory | None | No — no reproduction of program possible (Sony/Datel) |
| Look & feel as a concept | None | No — idea |

## The SAS Institute doctrine: demarcating track 1

The SAS Institute judgment (C-406/10, EU:C:2012:259) builds on BSA and further extends the **negative demarcation** of track 1. SAS expressly answers the question what is **not an expression of a computer program**.

### The three key elements that are not an expression

> SAS paragraph 39 + operative part 1: **neither the functionality of a computer program, nor the programming language and the format of data files** used in a computer program in order to exploit certain of its functions, constitutes a form of expression of that program within the meaning of art. 1(2) Directive 91/250/2009/24.

| Element | Status under track 1 | Status under track 2 |
|---|---|---|
| **Functionality** | ❌ Not an expression (SAS) | ❌ Idea, not a work |
| **Programming language** | ❌ Not an expression (SAS) | ✅ Possibly as author's own intellectual creation (SAS paragraph 45) |
| **File format** | ❌ Not an expression (SAS) | ✅ Possibly as author's own intellectual creation (SAS paragraph 45) |

### The policy consideration (SAS paragraph 40)

The Court expressly explains why functionality cannot be protected:

> "[T]o accept that the functionality of a computer program can be protected by copyright would amount to making it possible to **monopolise ideas, to the detriment of technological progress and industrial development**."

This is a fundamental policy consideration that extends well beyond software: EU copyright seeks a **balance between protection and free competition/innovation**.

### Legitimisation of similar programs (SAS paragraph 41)

> "[T]he main advantage of protecting computer programs by copyright is that such protection covers only the individual expression of the work and thus **leaves other authors the desired latitude to create similar or even identical programs provided that they refrain from copying**."

Practical consequence: it is **permitted** to develop a competing program offering the same functionality, provided that there is no source-code appropriation or decompilation.

## Reverse engineering: the operational test (SAS paragraphs 50-61)

SAS Institute expressly legitimises **black-box reverse engineering** under art. 5(3) Directive 91/250/2009/24.

### Conditions for lawful reverse engineering

1. **Lawful licence** for the program (the "lawful acquirer")
2. **Observe, study, test** within acts covered by the licence
3. **No access to the source code** of the program
4. **No decompilation of the object code** — exceptions: (i) art. 6 Dir. 2009/24 for interoperability under strict conditions, and (ii) art. 5(1) Dir. 2009/24 for error correction by the lawful acquirer ⓘ
5. **No infringement of the exclusive rights** of the rightsholder

> ⓘ **Top System v Belgian State** (CJEU 6 October 2021, C-13/20, ECLI:EU:C:2021:811, preliminary reference from the Brussels Court of Appeal) clarifies that decompilation for **error correction** by the lawful acquirer is permissible under art. 5(1) Dir. 2009/24 (formerly Dir. 91/250), without the strict interoperability conditions of art. 6 needing to be satisfied — both provisions pursue different aims (paragraph 49). Specific requirements apply: (a) necessary for use in accordance with the intended purpose; (b) contractual limitations possible, but any possibility of error correction cannot be contractually excluded (paragraph 66); (c) the result of decompilation may be used exclusively for error correction (paragraphs 69-73). In addition, **paragraph 36** confirms the BSA doctrine that **both source code and object code** are forms of expression of a computer program (cross-ref BSA paragraph 34). The full treatment of exceptions to exploitation rights falls outside the scope of this skill (concept of work + originality) and belongs in a separate skill on exploitation rights + exceptions.

> SAS paragraph 61: "the copyright in a computer program cannot be infringed where, [...] the lawful acquirer of the licence did not have access to the source code of the computer program to which that licence relates, but merely studied, observed and tested that program in order to reproduce its functionality in a second program."

### Anti-circumvention: licence terms cannot exclude reverse engineering

> SAS paragraph 53 + art. 9(1) + art. 5(3) Directive 91/250/2009/24: contractual provisions contrary to the exception in art. 5(3) are **null and void**.

Practical consequence: a software producer cannot **contractually shield** itself against observation and testing by licence holders. Protection is available against acts falling outside observation/testing/study (e.g. redistribution).

### When reverse engineering does constitute infringement

SAS paragraph 43 draws a **sharp line**: as soon as a third party obtains a **portion of the source or object code** and uses it to create similar elements in their own program, there is **partial reproduction** under art. 4(a) Directive 91/250/2009/24.

The difference between permitted and not permitted thus lies in:

| Permitted | Not permitted |
|---|---|
| Buy program under licence, observe, test | Obtain source code (by whatever means) and use it |
| Emulate functionality via own code | Decompile (unless under art. 6 for interoperability or art. 5(1) for error correction — Top System) |
| Use the same programming language or file format | Reproduce literal source code or object code |
| Produce the same results | Copy code structure |

## Manuals for software under InfoSoc (SAS paragraphs 63-70)

SAS Institute expressly deals with **manuals** for software. These fall **outside the Software Directive** (they are not a program) but **within the scope of InfoSoc** as a literary work.

### The Infopaq formula applied to manuals

> SAS paragraph 67: "It is only through the **choice, sequence and combination** of those words, figures or mathematical concepts that the author may express his creativity in an original manner and achieve a result, namely the user manual for the computer program, **which is an intellectual creation**."

### What is not protected individually (SAS paragraph 66)

- Keywords (on their own)
- Syntactical elements (on their own)
- Commands (on their own)
- Combinations of commands (on their own)
- Options
- Default settings
- Iteration counts

These are "words, figures or mathematical concepts" which individually are **not an intellectual creation** — in line with the Infopaq doctrine on building blocks.

### What may be protected

The **substantive combination** of the above elements that forms the expression of the author's own intellectual creation. Tested under the Football Dataco formula (free creative choices + personal touch).

### Operative part 3: infringement via reproduction in a second program or manual

Where, in a **second program** or in a **manual for that second program**, elements from a copyright-protected **manual** of a first program are reproduced, this may constitute **infringement of the manual** — not of the program itself — if the reproduction is the expression of the author's own intellectual creation of the first manual.

## Updated overview table of software elements

| Element | Track | Protection? | Source judgment |
|---|---|---|---|
| Source code | 1 (Software Directive) | Yes, if author's own creation | BSA paragraph 35 |
| Object code | 1 | Yes, if author's own creation | BSA paragraph 35 |
| Preparatory design material | 1 | Yes, if author's own creation and capable of resulting in a program | Dir. 91/250/2009/24 art. 1(1) |
| GUI | 2 (InfoSoc) | Yes, if author's own intellectual creation | BSA paragraphs 44-46 |
| Icons / animations | 2 | Yes, if Infopaq/Painer test met | analogy with BSA |
| Programming language as such (as idea) | None | No | SAS paragraph 39 + operative part 1 |
| Programming language as a work | 2 (InfoSoc) | Possibly, if author's own intellectual creation | SAS paragraph 45 |
| File format as such (as idea) | None | No | SAS paragraph 39 + operative part 1 |
| File format as a work | 2 (InfoSoc) | Possibly, if author's own intellectual creation | SAS paragraph 45 |
| Functionality | None | No — idea | SAS paragraph 39 + operative part 1 |
| API functions / functional specifications | None | No — idea | SAS analogy |
| **Runtime variables in working memory** | **None** | **No — no reproduction of program possible** | **Sony/Datel paragraphs 37, 51 + operative part** |
| Algorithm as such | None | No — principle | recital 14 Dir. 91/250/2009/24 + SAS paragraph 32 |
| Logic | None | No — principle | recital 14 + SAS paragraph 32 |
| Look & feel as a concept | None | No — idea | BSA analogy |
| Manual for software | 2 (InfoSoc) | Yes, if author's own intellectual creation through selection/arrangement/combination | SAS paragraph 67 + operative part 3 |

## The Sony/Datel refinement: the reproducibility test

Sony/Datel (C-159/23, 17 October 2024) builds on BSA and SAS Institute and delivers a **general operational test** for the question whether an element is an "expression" of a computer program.

### Factual matrix

Datel sold **Action Replay PSP** and **Tilt FX**: software/hardware giving players additional options in PlayStation games (turbo without limits, all drivers immediately available). The mechanism: Datel software runs in parallel with the Sony game and modifies **runtime variables in the working memory** of the PSP. Sony's source and object code remain untouched. Sony alleged infringement; the Bundesgerichtshof referred the case for a preliminary ruling.

### The reproducibility test (Sony/Datel paragraph 37) ⭐

The Court formulates the **core test** for "expression":

> "It is thus apparent from the wording of Article 1(2) of Directive 2009/24 [...] that **the source code and the object code fall within the concept of 'forms of expression' of a computer program, within the meaning of that provision, since they allow that program to be reproduced or subsequently created**, whereas other elements of that program, such as, inter alia, its functionalities, are not protected by that directive. **Nor does that directive protect the elements by means of which users make use of such functionalities, without, however, allowing such reproduction or subsequent creation of the said program**."

**Operational criterion**: an element is an "expression" if and only if it **enables the program to be reproduced or subsequently produced**.

### The literal-expression formula (Sony/Datel paragraph 38)

> "[T]he protection guaranteed by Directive 2009/24 is **limited to the intellectual creation as it is reflected in the text of the source code and object code and, therefore, to the literal expression of the computer program in those codes**, which constitute, respectively, a set of instructions according to which the computer must perform the tasks set by the author of the program."

Important: software protection under track 1 is a **literal-protection** regime. Non-literal similarities (similar behaviour, comparable logic, identical functionality, runtime modifications) do not lead to infringement under the Software Directive.

### Three scenarios for software elements after Sony/Datel

| Type of element | Reproduction of program possible? | Expression? |
|---|---|---|
| Source/object code | Yes | ✅ Protected under track 1 |
| Preparatory design material | Yes (may lead to a program, recital 7) | ✅ Protected under track 1 |
| GUI (BSA) | No | ❌ Not under track 1; possibly track 2 (InfoSoc) |
| Functionality (SAS) | No | ❌ Not protected under track 1 |
| Programming language as such (SAS) | No | ❌ Not protected under track 1 |
| File format (SAS) | No | ❌ Not protected under track 1 |
| **Runtime variables in working memory (Sony/Datel)** | **No** | ❌ **Not protected under track 1** |
| API signatures, behavioural specifications | No | ❌ Not protected under track 1 |
| Algorithm as such | No | ❌ Principle — not protected |
| Data structures in memory | No | ❌ Not protected under track 1 |

### Confirmation of anti-monopolisation (Sony/Datel paragraph 48)

Sony/Datel expressly confirms the **clean-room reverse engineering** doctrine, founded on the Commission's 1989 proposal:

> "[T]he legal regime for the protection of computer programs **does not grant monopolies hindering independent development and does not therefore block technical progress**. Moreover, **the competitors of the author of a computer program are free, once they establish through independent analysis which ideas, rules or principles are being used, to create their own implementation of them in order to create compatible products. They may, moreover, build on the identical idea, but may not use the same expression as that of other protected programs**."

Cross-references: SAS Institute paragraphs 39-40, BSA paragraphs 48-49.

### Application to runtime modifications (Sony/Datel paragraph 51 + operative part)

> Sony/Datel paragraph 51: "the content of the variables is therefore an element of the said program **by means of which users make use of its features**, which is not protected as a 'form of expression' of a computer program". The operative part confirms: the content of variable data does not fall within the protection conferred by the directive "**in so far as that content does not enable such a program to be reproduced or subsequently created**".

### Operational reach

Sony/Datel is directly relevant to modern software types that "graft" onto someone else's program without reproducing the code:

- **Cheating tools** and game trainers (such as Datel itself)
- **Memory editors** that manipulate runtime data
- **Browser extensions** that modify someone else's website DOM
- **Userscripts** (Greasemonkey-style) for someone else's web services
- **Macro tools** and automation operating someone else's application
- **Plugins** and hooks running in a host program
- **Bot scripts** for games or web services
- **AI agents** interacting with someone else's interface
- **Mods** for games that modify only runtime behaviour
- **Compatible software** developed via clean-room reverse engineering

For all these cases: as long as the tool does not reproduce source/object code and does not enable production of the protected program, it falls **outside Software Directive protection**.

### Important limitations of Sony/Datel

- **Question 2 (modification right art. 4(1)(b)) was NOT answered** (paragraph 53). Because question 1 was answered in the negative, question 2 did not require an answer. The precise demarcation of "alteration" as an exploitation right thus remains open
- **InfoSoc Directive (2001/29) not addressed** (paragraphs 26-29). The Court does not address the Commission's suggestion that art. 2(a) InfoSoc might be relevant for reproduction of working-memory content. Protection via InfoSoc for non-software elements surrounding a computer program remains possible
- **Other legal grounds unaffected**: contractual restrictions (EULA), unfair commercial practices, anti-circumvention of technical protection measures (art. 6 InfoSoc, art. 7(1)(c) Software Directive), sui generis database right — all of these can independently constitute infringement, even if the Software Directive does not protect
- **Reproduction itself not at issue** (paragraph 29): the Bundesgerichtshof had expressly stated that reproduction was not a question. The judgment therefore deals solely with the demarcation of scope

### Two-step analysis (BSA paragraph 51)

1. **Step 1**: Does the element enable reproduction of the program itself?
   - YES → track 1 (Software Directive)
   - NO → go to step 2
2. **Step 2**: Is the element the author's own intellectual creation within the meaning of Infopaq?
   - YES → track 2 (InfoSoc)
   - NO → no protection

For a GUI, the answer to step 1 is always NO (BSA paragraphs 40-41): the GUI is an interaction interface, it enables use of the program, but it does not enable reproduction of the program.

### Originality assessment of a GUI (BSA paragraph 48)

For the step-2 test, the court considers:

> "...the **specific arrangement or configuration of all the components** which form part of the graphic user interface, in order to determine which meet the criterion of originality."

In concrete terms:

- **Layout and composition**: positioning of windows, panels, buttons, menus
- **Visual design**: colour scheme, typography, icon style, depth treatment
- **Animations and transitions**: movements between screens, hover effects, transitions
- **Interaction patterns**: although the general patterns (click, drag, swipe) are ideas, the specific execution may be original
- **Decorative elements**: backgrounds, illustrations, mascots

## The technical-function exclusion (BSA paragraphs 48-50)

This is the crucial part of BSA that operates well beyond the software context.

### Formulation

> "the criterion of originality cannot be met by components of the graphic user interface which are differentiated only by their technical function" (BSA paragraph 48).
>
> "where the expression of those components is dictated by their technical function, the criterion of originality is not met, **since the different methods of implementing an idea are so limited that the idea and the expression become indissociable**" (BSA paragraph 49).

### Operationally

- For each GUI element, identify the **technical function** it performs
- Ask: **did the author have real alternatives** in design without impairing the function?
  - Many alternatives → free creative choice possible → original
  - One or very few forms possible to perform the function → idea/expression merge → not original
- Examples of **functionally dictated** elements:
  - A rectangular input field for text entry (standard shape determined by function)
  - A round cursor icon (standard convention)
  - A magnifying-glass icon for a search function (universal convention)
  - The standard Windows/macOS button design for "OK / Cancel"
- Examples of **freely designed** elements:
  - Specific colour choice of a dashboard
  - Own animation style at transitions
  - Own icon family with a recognisable style
  - A specific arrangement of panels not dictated by function

### Idea/expression merger ("merger doctrine")

The formulation "the idea merges with its expression" (BSA paragraph 49) is the EU expression of what in the Anglo-American tradition is called the **merger doctrine**:

> Where an idea can be expressed in only one (or a few) ways, there is no protectable expression — protection of the expression would amount to protection of the idea, which is incompatible with the idea/expression dichotomy.

This doctrine now applies in all categories of works and is later expressly extended:

- **Cofemel** (C-683/17) — applied art / fashion items: same test, no additional aesthetic requirement but technical-function exclusion applies
- **Brompton** (C-833/18) — utilitarian articles: technically dictated form excludes copyright protection

## What is NOT protected, even if it feels "creative"

BSA teaches that the following elements are not protected:

- **An interaction concept as such** (e.g. swipe-to-delete, pull-to-refresh) — idea/method
- **Functional button types** (OK/Cancel/Reset) — function-dictated
- **Patterns enforced by UX conventions** (hamburger menu, FAB button) — merger of idea and expression
- **Look and feel as a general concept** ("flat design", "skeuomorphism") — style/idea

What may be protected is the **concrete elaboration** of those concepts in a specific GUI.

## The concept of work (step 1) for software

For source code, object code and GUI, **objective identifiability** (Levola test step 1) is not a problem: all three are objectively fixed in a digital or graphic expression. The Painer formulas (free creative choices, personal touch) and the BSA test (arrangement and specific configuration minus technical-function elements) handle step 2 (originality).

## Categories of software elements and their typical assessment

> *Indicative; the test must be applied to each concrete element.*

| Element | Typical assessment | Note |
|---|---|---|
| Complete application source code | Original (track 1) | Almost always; threshold is low |
| GUI of a complex application | Often original (track 2) | Arrangement and configuration of all elements together |
| A single input form with standard fields | Often NOT original | Function-dictated |
| Icon set of own house style | Original (track 2) | Provided own stylistic choices |
| Standard buttons following platform conventions | NOT original | Convention + function |
| Game UI with animations and theme | Often original | Strongly creative domain |
| API specification (functions + parameters) | NOT original | Idea/functionality |
| File format (technical specification) | NOT original | Idea |
| Documentation / manual | Often original (track 2) | Assessed as text, not as software |
| Wireframes / mockups (preparatory) | Possibly original via track 1 (preparatory material) or track 2 (visual work) | |
| Runtime variables in working memory | NOT protected under track 1 | No reproduction of program possible (Sony/Datel) |
| Cheating tools / game trainers (runtime) | NOT infringing under track 1 | Other grounds possible: contract (EULA), TPM circumvention, unfair commercial practices |
| Browser extensions / DOM manipulation | NOT infringing under track 1 | No reproduction of host program; only interaction during runtime |
| Plugins / hooks in host program | NOT infringing under track 1 | Provided no reproduction of source/object code of host |

## The Nintendo boundary: multimedia works fall outside the Software Directive ⭐

In addition to the **internal** scope demarcation of the Software Directive through BSA, SAS Institute and Sony/Datel (what is an expression of a computer program?), **Nintendo / PC Box** (C-355/12, EU:C:2014:25, 23 January 2014) draws the **outer boundary**: multimedia works do **not fall entirely** within Directive 2009/24.

### The Nintendo formula (paragraph 23)

> "[V]ideogames, such as those at issue in the main proceedings, constitute complex matter comprising not only a computer program but also **graphic and sound elements, which, although encrypted in computer language, have a unique creative value which cannot be reduced to that encryption**. In so far as the parts of a videogame, in this case, the graphic and sound elements, are part of its originality, they are protected, together with the entire work, by copyright in the context of the system established by Directive 2001/29." (Nintendo paragraph 23)

### Operational consequences for software cases

For any file in which a software product also contains substantial multimedia or audiovisual components (videogames, multimedia apps, AR/VR works, interactive installations), the practitioner must distinguish three questions:

| Question | Answer under Nintendo |
|---|---|
| What regime applies to the computer-program part? | Directive 2009/24 (track 1; SAS Institute, Sony/Datel, BSA) |
| What regime applies to the graphic, sound and other creative components? | Directive 2001/29 (full regime; Painer, Cofemel, etc.) |
| What regime applies to the multimedia work as a whole? | Directive 2001/29 (Nintendo paragraph 23) — no artificial severance |

For the **broader doctrinal treatment of multimedia works** (complex-matter doctrine, holistic protection, connection with the Călinescu anti-severability rule paragraph 64): see `methodology/08-multimedia-works.md`.

### Connection with the BSA/SAS Institute/Sony/Datel line

Nintendo completes a doctrinal line on the scope of Directive 2009/24:

| Judgment | Contribution to scope of Dir. 2009/24 |
|---|---|
| **BSA** (C-393/09) | GUI ≠ expression of a computer program (falls under Dir. 2001/29 if original) |
| **SAS Institute** (C-406/10) | Functionality, programming language, file formats ≠ expression |
| **Sony/Datel** (C-159/23) | Runtime variables in working memory ≠ expression |
| **Nintendo** (C-355/12) | Multimedia works (videogames with graphic/sound elements) ≠ mere computer program — fall under Dir. 2001/29 as a whole |

## Application in argumentation

For developed argumentation per position:

- To establish that software elements are original → `positions/pro-rightsholder.md`, section *Software and GUI*
- To establish that software elements are not original → `positions/pro-alleged-infringer.md`, section *Software and GUI*

## Principal judgments in this module

- **Infopaq** (C-5/08) — general originality formula, basis for BSA and SAS
- **BSA** (C-393/09) — two-track system; GUI not under Software Directive but possibly under InfoSoc; technical-function exclusion; idea/expression merger
- **SAS Institute** (C-406/10) — functionality, programming language, file format not protectable as such; reverse engineering legitimised; manuals under InfoSoc
- **Sony/Datel** (C-159/23) — reproducibility test; runtime variables in working memory not an expression; literal-expression formula; confirmation of clean-room reverse engineering
- **Nintendo / PC Box** (C-355/12) — outer boundary Dir. 2009/24: multimedia works (videogames with graphic/sound elements) do not fall entirely under the Software Directive but under Dir. 2001/29 as a whole; complex-matter doctrine (paragraph 23) — developed in `08-multimedia-works.md`
- **Top System v Belgian State** (C-13/20) — decompilation for error correction under art. 5(1) Dir. 91/250 (formerly Dir. 2009/24); confirmation of the BSA doctrine that both source code and object code are forms of expression (paragraph 36); full treatment falls **outside skill scope** (exceptions to exploitation rights); footnote mention only ⓘ
- **Cofemel** (C-683/17), **Brompton** (C-833/18) — extension of technical-function exclusion to applied art and utilitarian articles; full treatment as key judgments in `05-applied-art.md`; cross-references from this module via the BSA-Brompton doctrine
