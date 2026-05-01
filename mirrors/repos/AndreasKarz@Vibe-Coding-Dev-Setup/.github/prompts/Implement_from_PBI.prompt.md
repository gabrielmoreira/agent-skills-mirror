---
agent: agent
description: Implement a feature end-to-end from an Azure DevOps PBI — analyze, plan, code, test, review.
tools: ['vscode', 'execute', 'read', 'agent', 'edit', 'search', 'web', 'ado/advsec_get_alert_details', 'ado/advsec_get_alerts', 'ado/core_get_identity_ids', 'ado/core_list_project_teams', 'ado/core_list_projects', 'ado/pipelines_get_build_definition_revisions', 'ado/pipelines_get_build_definitions', 'ado/pipelines_get_build_log', 'ado/pipelines_get_build_log_by_id', 'ado/pipelines_get_build_status', 'ado/pipelines_get_builds', 'ado/pipelines_get_run', 'ado/pipelines_list_runs', 'ado/pipelines_run_pipeline', 'ado/pipelines_update_build_stage', 'ado/repo_create_pull_request', 'ado/repo_create_pull_request_thread', 'ado/repo_get_branch_by_name', 'ado/repo_get_pull_request_by_id', 'ado/repo_get_repo_by_name_or_id', 'ado/repo_list_branches_by_repo', 'ado/repo_list_my_branches_by_repo', 'ado/repo_list_pull_request_thread_comments', 'ado/repo_list_pull_request_threads', 'ado/repo_list_pull_requests_by_commits', 'ado/repo_list_pull_requests_by_repo_or_project', 'ado/repo_list_repos_by_project', 'ado/repo_reply_to_comment', 'ado/repo_search_commits', 'ado/repo_update_pull_request', 'ado/repo_update_pull_request_reviewers', 'ado/repo_update_pull_request_thread', 'ado/search_code', 'ado/search_wiki', 'ado/search_workitem', 'ado/testplan_add_test_cases_to_suite', 'ado/testplan_create_test_case', 'ado/testplan_create_test_plan', 'ado/testplan_create_test_suite', 'ado/testplan_list_test_cases', 'ado/testplan_list_test_plans', 'ado/testplan_list_test_suites', 'ado/testplan_show_test_results_from_build_id', 'ado/testplan_update_test_case_steps', 'ado/wiki_create_or_update_page', 'ado/wiki_get_page', 'ado/wiki_get_page_content', 'ado/wiki_get_wiki', 'ado/wiki_list_pages', 'ado/wiki_list_wikis', 'ado/wit_add_artifact_link', 'ado/wit_add_child_work_items', 'ado/wit_add_work_item_comment', 'ado/wit_create_work_item', 'ado/wit_get_query', 'ado/wit_get_query_results_by_id', 'ado/wit_get_work_item', 'ado/wit_get_work_item_type', 'ado/wit_get_work_items_batch_by_ids', 'ado/wit_get_work_items_for_iteration', 'ado/wit_link_work_item_to_pull_request', 'ado/wit_list_backlog_work_items', 'ado/wit_list_backlogs', 'ado/wit_list_work_item_comments', 'ado/wit_list_work_item_revisions', 'ado/wit_my_work_items', 'ado/wit_update_work_item', 'ado/wit_update_work_items_batch', 'ado/wit_work_item_unlink', 'ado/wit_work_items_link', 'ado/work_assign_iterations', 'ado/work_create_iterations', 'ado/work_get_iteration_capacities', 'ado/work_get_team_capacity', 'ado/work_list_iterations', 'ado/work_list_team_iterations', 'ado/work_update_team_capacity', 'memory/*', 'sequential-thinking/*', 'azure-mcp/search', 'todo']
---

# Implement from PBI

Implement a feature end-to-end from an Azure DevOps PBI. Follow the persona, conventions, and delegation rules defined in `AGENTS.md`. Apply `general.instructions.md` and `tests.instructions.md` throughout. Use the `C# Expert` agent for .NET implementation decisions.

Work autonomously, accurately, and incrementally — one compilable step at a time.

---

## Phase 0: Identify the PBI

If the user provided a PBI ID (a number), use it directly. If not, ask:

> What is the PBI ID (Azure DevOps Work Item ID) to implement?

Do NOT proceed until you have a valid numeric Work Item ID.

---

## Phase 1: Deep PBI Analysis

Use Azure DevOps MCP tools to gather the full picture. Execute these steps in order:

1. **Fetch the PBI** — retrieve the work item by ID (project: `<!-- TODO: Replace with your ADO project name -->`). Extract: title, description, acceptance criteria, state, assigned to, iteration, area path.
2. **Fetch the Parent** — if the PBI has a parent link, retrieve it. Understand the epic/feature context and any overarching requirements or constraints.
3. **Fetch all Children** — if the PBI has child work items (tasks, sub-items), retrieve each one. Map out the full scope of work including task breakdown, estimates, and any already-completed tasks.
4. **Fetch linked items** — check for related work items, predecessor/successor links, or referenced PRs that provide additional context.

Compile a structured summary:

```
## PBI Analysis

**PBI #{id}: {title}**
**Parent**: #{parent_id}: {parent_title} (or "None")
**State**: {state} | **Iteration**: {iteration}

### Description
{description text}

### Acceptance Criteria
{acceptance criteria — bullet list}

### Child Work Items
- #{child_id}: {title} — {state}
- ...

### Key Constraints & Dependencies
{anything from parent, linked items, or description that constrains the implementation}
```

Present this summary and confirm understanding before proceeding.

---

## Phase 2: Codebase Analysis

Identify the affected domain service(s) and analyze the existing code:

2. **Locate the domain** — determine which domain service(s) under `src/` are affected.
2. **Map the layers** — for each affected domain, inspect the relevant layers (Abstractions, Core, DataAccess, GraphQL, Host, Worker) to understand the current structure.
3. **Trace related code** — find existing models, services, repositories, resolvers, consumers, and types that relate to the PBI's functionality. Use search, usages, and file reads.
4. **Identify patterns** — note which patterns the existing code uses (repository pattern, DataLoader, MassTransit consumers, mutation conventions) so the new code stays consistent.
5. **Check existing tests** — locate the test projects and understand the current test patterns, sample data classes, and fixtures in use.

---

## Phase 3: Implementation Plan

Create a numbered, step-by-step implementation plan. Each step must be:
- **Small and compilable** — the solution must build after every step
- **Testable** — existing tests must pass after every step
- **Layered** — follow the dependency rules (Abstractions → Core → DataAccess → GraphQL)

Format:

```
## Implementation Plan

### Step 1: {Layer} — {What}
{What will be added/changed and why}
Files: {list of files to create or modify}

### Step 2: {Layer} — {What}
...

### Step N: Tests — Unit tests for new functionality
{Which test classes, what scenarios, target ≥82% coverage on new code}
```

**Present the plan to the developer and wait for explicit approval before implementing.**

If the developer suggests changes, revise the plan and present again. Do not start coding until the developer confirms the plan.

---

## Phase 4: Incremental Implementation

After plan approval, implement each step sequentially. For **every step**:

1. **Implement the changes** — write clean, production-ready code following:
   - `general.instructions.md` coding standards (underscore prefix, explicit types, descriptive names)
   - `CSharpExpert` agent patterns (SOLID, error handling, async best practices)
   - Existing patterns in the affected domain service
   - `tests.instructions.md` conventions when touching test files

2. **Validate compilation** — run `dotnet build` on the affected project(s). Fix any errors before proceeding.

3. **Run existing tests** — execute the existing unit tests for the affected domain:
   ```
   dotnet test src/{Domain}/test/{Layer}.Tests/ --no-build
   ```
   If any test fails, stop and fix the regression before moving to the next step. Never leave broken tests behind.

4. **Report progress** — briefly state what was completed and that tests pass.

### Implementation Rules

- **One step at a time** — never skip ahead or combine steps
- **No breaking changes** — existing functionality must remain intact after each step
- **Follow existing patterns** — if the codebase uses a specific pattern (e.g., `ID<T>`, Outbox, DataLoader), use the same pattern
- **No shortcuts** — do not use `var` unless the type is obvious, do not abbreviate variable names, do not skip null guards
- **Compile after every file change** — catch errors early
- **If stuck** — explain the blocker and ask the developer for guidance instead of guessing

---

## Phase 5: Test Implementation

After all functional code is implemented and all existing tests pass:

1. **Identify test scenarios** — list all public methods and behaviors introduced or changed. For each, define:
   - Happy path test(s)
   - Edge case / boundary tests
   - Error / exception path tests

2. **Write unit tests** following `tests.instructions.md`:
   - Framework: xUnit + xUnit Asserts (new tests), FluentAssertions only in existing test files
   - Mocking: Moq with `MockBehavior.Strict` as default
   - Pattern: Arrange-Act-Assert with clear sections
   - Naming: `MethodName_Scenario_ExpectedBehavior`
   - Use Theories with `[InlineData]` instead of duplicating tests
   - Use Snapshooter when asserting complex objects (>5 properties)
   - Re-use existing sample data classes; create new ones if needed

3. **Measure code coverage** — run:
   ```
   dotnet tool install -g dotnet-coverage 2>$null
   dotnet-coverage collect -f cobertura -o coverage.cobertura.xml dotnet test src/{Domain}/test/
   ```
   Verify that **new code** achieves at least **82% line coverage**. If below target, add additional test cases for uncovered paths.

4. **Run the full test suite** — ensure all tests (existing + new) pass:
   ```
   dotnet test src/{Domain}/test/ --no-build
   ```

---

## Phase 6: Code Review

After all tests pass and coverage target is met:

1. **Stage and review changes** — use `git diff` to verify all changes are intentional and clean.

2. **Invoke the `code-reviewer` skill** — apply the full code review checklist on the current branch changes:
   - Architecture layer violations
   - Security issues
   - Naming conventions
   - Type safety
   - Test quality
   - GraphQL patterns
   - Documentation completeness

3. **Fix any BLOCKER findings** — address all blocker-severity issues identified by the review. Re-run tests after each fix.

4. **Report IMPROVEMENT and NITPICK findings** — present these to the developer for decision.

5. **Final validation** — run the complete test suite one last time to confirm everything is green.

---

## Completion Summary

When all phases are complete, present:

```
## Implementation Complete

**PBI #{id}: {title}**

### Changes Made
- {list of files created/modified, grouped by layer}

### Test Coverage
- New tests: {count}
- Coverage on new code: {percentage}%

### Code Review Result
- Blockers fixed: {count}
- Improvements noted: {count}
- Vote recommendation: {Approve / Approve with Suggestions}

### Ready for PR
- [ ] All existing tests pass
- [ ] All new tests pass
- [ ] Coverage ≥82% on new code
- [ ] Code review blockers resolved
- [ ] PR title: `feat({Scope}): {PBI title}`
```
