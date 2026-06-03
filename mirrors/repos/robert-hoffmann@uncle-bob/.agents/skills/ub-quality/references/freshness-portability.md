# Freshness And Portability

This reference clarifies which `ub-quality` behaviors are repository policy and
which guidance surfaces should be treated as strong defaults that downstream
adopters may adapt deliberately.

## Repository Policy

Within this repository, these `ub-quality` behaviors are policy rather than
mere preference:

1. load and apply the required `ub-quality` references before writing
2. align touched eligible separator blocks
3. preserve special comment-tag handling and document-generation rules
4. respect repository validation and synchronization requirements when they are
   explicitly documented

If a file is touched in this repository and those rules apply, they are not
optional cleanup.

## Strong Defaults

Many language and framework skills express strong defaults rather than
universal law.

Examples:

1. latest-stable version bias
2. primary tool preferences such as `uv`, Vite-native integrations, or CSS-first Tailwind
3. ecosystem preferences such as VueUse-first or standard-library-first guidance

These are intentionally strong house defaults, but they are still defaults.
They may need deliberate adaptation in other repositories or compatibility
contexts.

## Portability Boundary

When working inside this repository:

1. treat documented repository contracts as binding
2. treat validation-backed rules as policy
3. treat volatile setup recipes and tool preferences as strong defaults unless
   a repo contract explicitly promotes them to policy

When adapting this repository's guidance elsewhere:

1. keep the stable principles
2. re-evaluate framework recipes and tool choices against the target repo's truth
3. do not copy strong defaults as if they were portable requirements without
   checking the downstream environment first

## Internal-First Distribution Model

This catalog is internal-first and distributable-second.

That means:

1. strong opinions and standardized internal workflows are expected
2. internal standardization is a valid reason to ship deterministic starter
   assets and opinionated helper scripts
3. distributable skill content still needs a clean portability boundary
4. portable skill surfaces are the files shipped inside `.agents/skills`,
   especially `SKILL.md`, `references/`, `assets/`, and skill-owned `scripts/`
5. repo-root wiring such as task runners, CI layout, local wrappers, and
   shell-specific inspection habits are repository truth, not portable skill
   contract

Practical rule:

1. ship opinionated assets when they can be scaffolded cross-platform
2. allow small broadly portable runtime assumptions such as Python or
   Node/`npx` when the skill-owned scaffold genuinely depends on them
3. keep repo-local automation names and Unix-specific command examples out of
   distributable skill references unless the skill itself recreates that
   surface for adopters

## Freshness Boundary

Freshness review for volatile skills is advisory only in this repository.

Rules:

1. do not create a new blocker just because a skill is marked high-volatility
2. use freshness markers to prioritize review, not to halt unrelated work
3. tighten freshness only after the repository explicitly chooses stronger enforcement

## Parallel Research Delegation

When freshness, portability, donor comparison, official documentation review,
or analogous-system research has two or more independent read-heavy slices,
prefer explicit parallel delegation when the current agent runtime supports it.

Portable trigger:

1. each slice can be investigated without depending on another slice's result
2. the expected output is distilled evidence, not implementation
3. the sources or allowed paths can be bounded up front
4. the parent thread can verify anchors and reconcile conflicts

Delegation contract:

1. assign one subagent, background thread, or equivalent worker per slice
2. give each worker a bounded read-only task, allowed sources or paths, and
   no-edit constraints
3. ask workers to return distilled findings with fact, inference, source,
   implication, and rejected pattern when that shape fits the research
4. wait for all requested workers before consolidating
5. keep the parent agent accountable for source verification, conflict
   reconciliation, and final recommendation

Do not delegate when the task is single-threaded, the current runtime lacks a
safe subagent or background-thread surface, authorization boundaries are
unclear, or parallel work would mostly duplicate context. Use narrow
sequential passes instead.

Do not use recursive fan-out unless the operator explicitly asks for it and the
runtime supports bounded recursion. For proprietary donors, use only authorized
paths, public docs, public license or README material, and observed behavior
the operator is allowed to inspect.
