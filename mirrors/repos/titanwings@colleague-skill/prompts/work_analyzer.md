# Work Skill Analysis Prompt

## Task

You will receive source material from **{name}** (documents, messages, emails, etc.).
Extract their work capabilities and methods from it, for use in building the Work Skill.

**Principle: extract only work-related content and ignore small talk. Do not infer; write only what has evidence, and where there is none, mark it "insufficient source material".**

---

## General Extraction Dimensions (apply to all roles)

### 1. Scope of Responsibility

Identify from the source material:
- The systems / modules / business lines / products they own
- The documents they maintain (API docs, wiki, runbooks...)
- Their responsibility boundaries (what is theirs and what isn't)
- Project codenames and business terms they mention frequently

```
Output format:
Domain: [description]
Core systems: [list]
Maintained docs: [list]
Boundaries: [what they own / what they don't]
```

### 2. Workflow

Extract from task descriptions and meeting notes:
- The steps they follow when taking on a task
- Their structural habits when writing proposals / documents
- How they manage progress and handle deadlines
- How they handle exceptions / emergencies

```
Output format:
Taking on tasks: [steps]
Writing proposals: [structure description]
Exception handling: [process]
```

### 3. Output Format Preferences

- Tables / lists / flowcharts / plain prose
- Conclusion first, or a gradual build-up
- Document level of detail (minimal / moderate / exhaustive)
- Reply / email style

```
Output format:
Document style: [description]
Level of detail: [minimal / moderate / exhaustive]
```

### 4. Experience Knowledge Base

Experience-based judgments, lessons learned the hard way, and technical opinions they have explicitly expressed (quote their own words directly):

```
- "[original quote or summary]"
- "[original quote or summary]"
```

---

## Role-Specific Extraction

Based on {name}'s role, focus on the corresponding dimensions:

---

### 🖥️ Backend Engineer / Server-Side Engineer

**Technical standards**:
- Tech stack (languages, frameworks, middleware)
- Naming conventions (API path style, variable / function naming)
- API design (response structure, error codes, pagination, idempotency)
- Database preferences (ORM vs. raw SQL, transaction boundaries)
- Error-handling style

**Code Review focus**:
- CR issues they raise repeatedly (N+1, transactions, concurrency safety...)
- Their CR comment style (direct / tactful, [block]/[suggest] severity levels...)

**Deployment and operations**:
- Monitoring metrics they watch
- Steps for troubleshooting production issues
- Change release process

---

### 🌐 Frontend Engineer

**Technical standards**:
- Tech stack (framework, state management, styling approach)
- Component-splitting principles (when to split, when not to)
- Performance concerns (first paint, lazy loading, bundle size...)
- How they call APIs and handle errors

**Engineering practices**:
- Code-style tooling (ESLint rule and Prettier config preferences)
- Test coverage expectations (attitude toward unit / integration tests)
- CR focus (attention to accessibility / responsiveness / compatibility)

---

### 🤖 Algorithm Engineer / ML Engineer

**Research and experimentation**:
- How they define problems (how they break down an ML problem)
- Experiment design habits (baseline selection, ablation design)
- Metric definition preferences (attitude toward offline vs. online metrics)
- Models / methodologies they commonly use

**Engineering deployment**:
- Training framework preferences
- Model launch process
- Data processing standards

**Documentation and conclusions**:
- How they write experiment reports (conclusion-focused / process-focused)
- Papers or methodologies they cite

---

### 📱 Product Manager / Technical Product Manager

**Requirements handling**:
- PRD structure and level of detail
- How they define user stories / requirement boundaries
- How they align with engineering (review style, change process)

**Decision framework**:
- Prioritization method (RICE / MoSCoW / custom)
- Ratio of data-driven decisions to intuition
- How they handle conflicting requirements

**Deliverables**:
- Types of documents they deliver (PRD / MRD / prototypes / competitive analysis)
- Prototyping tool preferences
- Level of involvement in analytics event tracking

---

### 🎨 Designer

**Design standards**:
- Design system / component library used
- Annotation style and handoff standards
- How strictly they demand pixel-perfect results

**Workflow**:
- Steps from requirements to design solution
- How they do design walkthroughs / acceptance reviews
- How they handle implementation-fidelity issues on the engineering side

---

### 📊 Data Analyst

**Analysis methods**:
- Common analysis frameworks (funnel / cohort / A/B testing...)
- SQL style (terse / heavily commented)
- Data visualization preferences (choice of chart types)

**Report style**:
- Ratio of conclusions to data
- How strictly they practice "let the data speak"
- How they handle data anomalies / disputes over metric definitions

---

## Output Requirements

- Language: the user's language
- Dimensions with no information: mark them `(Insufficient source material; consider adding relevant documents)`
- Conclusions backed by source text: quote the original words
- The output is used directly to generate work.md, so it must be concrete and actionable; do not use vague wording like "might" or "tends to"
