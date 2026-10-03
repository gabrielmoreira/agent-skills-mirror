---
title: Construct ownership
applicability:
- When the work depends on which construct owns a provision
- When the work depends on which kind a knowledge unit takes
---

Choose the owner from the obligation, baseline-or-specialization role, domain, selector, consumer, and read path before looking at its current container. The effective manual establishes available construct types and how each reaches an agent; an existing container, familiar label, or compiler acceptance does not establish ownership.

A behavior-bearing point has one primary authored owner. For a requested outcome, the selected task owns its workflow. Supporting constructs may supply reusable discipline, facts, or situational understanding without becoming second owners of that workflow. Classify the point before applying construct-specific quality rules.

## Core and optional specialization

The core must reach the declared outcome with every facet and facet-owned guide removed. Facets add optional informational specialization to an already-selected task; they do not create baseline capability, support boundary, safety condition, authority rule, workflow, operational dependency, evidence-generation requirement, or completion path. Facet applicability establishes relevance, not workflow or authority.

Applicability and optionality are separate axes. A condition may gate a baseline obligation. If any already in-scope instance needs that obligation for correct completion when the condition holds, its useful general form is core. Put in core any general or abstract rule valid across the skill; a facet may keep only irreducibly domain-specific refinement whose absence makes the result less specialized rather than incomplete. If the core otherwise cannot close, supply a general rule or mechanism for obtaining/applying needed domain facts, or narrow the declared outcome under proper authority; do not make a facet the sole completion path.

## Construct kinds

**Task.** Use a task when the provision belongs to one recognizable class of requested work and helps define or reach that class's finished state. The task owns the actions, stages, order, authority gates, effects, inspection or verification requirements, stopping conditions, fallbacks, and completion criteria for that requested outcome. Route tasks from the requested outcome, not a property of material in front of the agent. A separate task owns an independent outcome or failure boundary, or distinct reasoning the first should not duplicate; variation across material or environment domains does not itself create another task when the requested work stays the same.

**Knowledge.** Use knowledge for reusable subject matter a task's page carries: models, facts, constraints, or guidance a task may need. Because a unit is read on every run of each task carrying it, it must remain valid across that task's situational domains. Keep in it only what every run of each task carrying it needs.

Choose a unit's kind from what its reader must do with it; the effective manual gives each kind's meaning and heading. A `fact` heading presents the unit as settled, so it cannot carry a claim still unestablished or a requirement the skill chooses. Use `constraint` only when the whole meaning is that something must or must not happen, as when an authority the unit names imposes it; a decision needing a discriminator or rationale belongs in concept or guidance. For a unit that both describes and instructs, set the instructions aside: if its point survives, it takes the kind of what remains, concept or fact; if not, it is guidance.

**Principle.** Use a principle for a standard the agent's own work must honor across kinds of work, rather than a step of that work or material a step consumes. The standard may hold in every subject, such as how claims are established and reported, or come from the skill's own field: a norm the field's work owes to the people and systems it affects, or a discipline the field keeps in establishing and stating its results. Role decides, not the idea or how widely it applies: an idea is a principle where the work must honor it and subject matter where the work applies it to its material, and a rule is not a principle merely because many tasks need it. It holds on every path that names it, and a standard that binds only a recognizable part of the field is still a principle, confined to that part by its placement and applicability. After principle is the candidate, use [[guide:principle-selection]] to decide fit.

**Facet.** Use a facet when an observable aspect of subject material, operating environment, audience, governing context, or other situation gives an already-selected task useful optional domain understanding; take how facets are selected and composed from the effective manual. Evidence may be in the request or discovered after task selection. After facet is the candidate, use [[guide:facet-design]] to judge its boundary, specialization, composition, and content.

**Guide.** Use a guide for detail deliberately loaded as a separate page from one or more task or facet owners. Its applicability may identify the situational conditions under which baseline detail applies; those conditions do not by themselves make the behavior optional specialization. A guide reachable only from a facet inherits the facet's informational boundary and cannot own workflow. After guide is the candidate, use [[guide:guide-design]] to write it and decide where it is referenced.

**Script or asset.** An operation the child agent must perform identically on every run, or content it must reproduce exactly, may be better shipped as a file than written as prose; [[guide:shipped-files]] decides.

**Local branch.** Keep reasoning local when it belongs only to an already-open page and has no independently reusable owner. A local branch stays inside that page's established domain; it does not create specialization, and it never stands in for a guide's applicability.

## Overlapping candidates

When more than one construct description appears to fit, identify first whether the provision is baseline behavior or optional specialization, then what makes it applicable and what it may assume:

- a request-visible outcome selects a task;
- reusable subject matter valid throughout an existing task domain selects knowledge;
- a standard the agent's work must honor across kinds of work, in every subject or within the skill's own field, selects a principle;
- a narrower situational domain plus optional informational specialization selects a facet;
- a separately loaded body whose applicability is decidable before opening selects a guide; task-owned guides may carry conditionally applicable baseline detail, while facet-owned guides carry only informational specialization about work the task already owns; and
- an already-open owner's private branch inside its established domain stays local.

These are discriminators, not a priority list. Conditionality, reuse across tasks, frequency, current placement, or greater concreteness alone does not select a facet. Specialization does not become a guide merely because one task consumes most of it. If two kinds remain plausible, name the missing fact about baseline necessity, requested outcome, domain boundary, selector, consumer, or read path instead of choosing from breadth or convenience.

Once a kind is selected, apply that construct's own quality guidance. If the candidate fails its downstream contract, return to classification rather than weakening the construct-specific test.
