# Step 01 — Gather Requirements Context

**Previous step:** (none)
**Next step:** `step-02-draft.md`

---

## 1. Establish Scope

Ask the user:

1. **What's the project name and one-line description?**
2. **Is this greenfield or brownfield?**
   - Greenfield: starting from scratch
   - Brownfield: adding to or modifying existing system (if so, load `project-context.md`)
3. **What phase of planning are we in?**
   - Pre-concept (exploring the idea)
   - Post-brief (brief exists, now formalizing requirements)
   - Mid-development (adding to an in-flight project)
4. **Who are the stakeholders?** (Product owner, engineering lead, design, etc.)

⏸️ **STOP** — wait for answers before proceeding.

---

## 2. Define Goals and Non-Goals

Ask:

1. **What is the primary goal of this project/feature?** One clear sentence.
2. **What are 2–3 secondary goals?**
3. **What is explicitly NOT a goal?** (Non-goals are as important as goals.)
4. **What does "done" look like?** The moment this ships, what has changed?

---

## 3. Identify User Personas

For each user type that will interact with this system:

Ask: "Who are the different types of users? Let's go through each one."

For each persona, capture:
- **Name/role** (e.g., "Admin", "End User", "Developer")
- **Primary goal** when using the system
- **Key pain point** today
- **Success definition** for them

---

## 4. Enumerate Features (High Level)

Ask: "Let's brainstorm the key capabilities. What must this system do?"

Capture as a raw list — no detail yet. We'll refine in the next step.

Group them roughly into:
- **Core** — must-have for MVP
- **Important** — high value, can slip post-launch
- **Nice to have** — defer unless free

⏸️ **STOP** — Present the prioritized feature list and ask: "Does this capture the scope? Anything missing or to reprioritize?"

---

## 5. Identify Constraints and Assumptions

Ask:
1. Any technology constraints? (must use X, cannot use Y)
2. Any regulatory, compliance, or security requirements?
3. Performance or scale requirements?
4. Timeline or milestone constraints?
5. Dependency on other teams or systems?

---

## 6. Save Context and Move On

Save a working notes file at `{planning_artifacts}/prd/{project_name}-prd-context.md` with all gathered context.

Update frontmatter:
```yaml
stepsCompleted: ["step-01-requirements"]
```

Say: "Great — I have what I need to start drafting. Let's write the PRD."

Load and follow `./step-02-draft.md`.
