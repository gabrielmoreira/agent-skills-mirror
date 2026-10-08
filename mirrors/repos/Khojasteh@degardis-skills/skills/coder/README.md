# Coder

**Version:** `1.1.0` · **License:** [MIT](../../LICENSE) · [Changelog](CHANGELOG.md)

Help your coding agent turn a software request into a result you can inspect, understand, and trust.

Coder guides an agent through the decisions that make software work succeed: understanding the real outcome, finding the contract the software must honor, keeping the work inside the boundary you set, and gathering evidence that shows whether the result works. One skill covers the whole job, from investigation and planning to implementation, review, documentation, and verification, and it never treats an edited file as proof that the work is done.

> [!CAUTION]
> A skill is guidance, not a guarantee. Review the diff, evidence, and remaining risks before relying on the result, especially for high-impact changes. An agent can misunderstand or skip guidance, and this skill can contain defects or gaps.

## Better outcomes, not just more code

A coding agent can produce a convincing patch quickly. The harder part is making sure it solved the right problem, kept working what still matters, and checked the behavior that could actually fail. Coder keeps those questions in front of the agent:

- **A diagnosis comes before a fix.** For a defect, the agent establishes the expected behavior, reproduces the symptom, and finds where things first go wrong before it edits anything.
- **The expected result comes from outside the code.** Requirements, interfaces, schemas, consumers, and meaningful tests define what's correct. The code under question can't be its own answer key, so a failing test is never "fixed" by changing its expectation to match whatever the code does.
- **A passing check proves only what it exercised.** A green build isn't evidence for behavior it never ran, and an earlier check doesn't prove that a later edit still works.
- **A review finding comes with its evidence.** Each one names the input that triggers it, where behavior departs from the contract, the expected and actual results, and what the agent checked that could have proved it wrong. A style preference isn't reported as a defect.
- **A test earns its place.** The agent adds or revises a maintained test only when it would catch a real contract violation or regression, not just because a file changed.
- **A refactor keeps behavior.** It removes a named structural cost, such as one rule copied into three places, and preserves observable behavior and compatibility unless you ask for a change.
- **Performance work starts with measurement.** The agent fixes the metric, a representative workload, and a baseline first, finds where the cost really is, and checks guardrails such as memory or error rate.
- **A broad claim needs broad coverage.** "All references updated" or "no callers affected" needs a search that could find the non-obvious cases too, such as registrations, reflection, and generated code.
- **Criteria come before the check.** When you ask whether something works, the agent fixes what counts as a pass or a fail before it runs anything, and a check it couldn't run is reported as unverified, never as passed.
- **Your choices stay yours.** When a plan depends on a choice only you can make, such as how far a migration should retire the old approach, the agent asks before it settles the design, and the plan names any choice you left open.
- **Allowing something isn't asking for it.** If you say breaking changes are fine, the agent may make one, but it still weighs what the break costs your callers and keeps a compatible design when that serves the outcome as well.
- **A bounded request stays bounded.** Assessing, investigating, reviewing, explaining, or verifying leaves your source unchanged, and a documentation task doesn't turn into a code change. Defects found along the way are reported rather than quietly fixed, and follow-on work, such as applying a review's fixes, waits until you ask for it.

You get a better handoff: a change you can review, evidence you can interpret, and clear limits wherever the agent couldn't establish an answer.

## Engineering judgment it brings

Beyond checking its own work, Coder carries guidance for the design and craft decisions that make software easy or hard to live with, and applies the part that fits the work at hand.

- **A design chosen by comparison, not by first draft.** Before editing, the agent compares the viable designs where they actually differ: who owns each responsibility, which way dependencies point, where state lives, and where boundaries fall. The first plausible implementation, the smallest diff, or the nearest existing pattern doesn't win by default. A mechanism your project already has is extended rather than bypassed, unless your outcome needs something it can't guarantee; then the agent names that trade and its evidence.
- **Architecture heuristics as questions, not slogans.** Each candidate is tested for clear ownership and cohesion, coupling and dependency direction, information hiding, one source of truth for each fact, code you can follow without hidden globals or mode flags, and how far the next change would spread. The heuristics expose consequences; they don't force a pattern or score designs by acronym.
- **Abstractions that earn their place.** Better names and existing boundaries come before a new layer. An interface comes from what its callers need, an extension point from variation that already exists, and no factory, strategy, or wrapper goes in just to fit a pattern. Code that only looks alike stays separate when the rules behind it can change independently.
- **Values that survive every boundary.** When a value crosses configuration, serialization, templates, commands, protocols, or storage, the agent checks its type, spelling, defaults, missing values, and precision at each crossing, and verifies it where it's finally used.
- **Interfaces treated as behavior, not styling.** For user-interface work, the agent models the flow as states a user can reach, such as loading, empty, error, or permission-denied, and reuses your design system and components instead of starting a parallel one. Appearance, interaction, semantics, and accessibility are separate claims: a screenshot doesn't prove keyboard or screen-reader behavior, and what it couldn't observe in your environment is reported as unverified.
- **Documentation written for a named reader.** Before drafting, the agent settles who the reader is, what they're trying to do, and which kind of document serves them, from a tutorial or how-to guide to release notes, a runbook, or a decision record. Each definition, schema, or option list gets one home instead of copies across pages. Every factual claim needs evidence outside the documentation, version-specific behavior is tied to the versions your project uses, and the commands and examples a reader will run are checked first. API reference tells a caller what they need without reading the implementation, and a code comment keeps only what the code can't say.
- **Risky surfaces get their own scrutiny.** Security boundaries, failure and cleanup paths, concurrency, stored data, interfaces that other software depends on, and logs and metrics each have focused guidance. For example, changing code and applying a migration are separate actions, and a new constraint isn't added until existing data is shown to satisfy it.

## Guidance for your stack

Coder brings in guidance for the technology your project actually uses. It covers 25 languages, 19 frameworks and libraries, 5 runtimes and platforms, and 18 test frameworks: Python, TypeScript, Java, C#, Go, Rust, and many more, along with React, Django, Spring, ASP.NET Core, pytest, Jest, Playwright, and others.

That guidance is version-aware. It knows, for example, that React 19 removed `ReactDOM.render` and that Python 3.13 dropped standard-library modules such as `cgi` and `telnetlib`, and it checks the versions your project configures before applying either.

For code documentation, it follows the conventions of the tool you use: Javadoc, KDoc, JSDoc and TSDoc, .NET XML comments, Python docstrings, Go doc comments, rustdoc, Swift DocC, and Doxygen.

## Where it stops

- **Changing code isn't permission to operate.** Deploying, publishing, repairing data, applying a schema, using privileged access, reading production systems, and spending money each need your go-ahead for that action and target.
- **It's built for software work.** Requests outside software engineering are outside its scope.

For the habits Coder shares with the rest of the collection, such as asking before crossing a boundary and keeping sensitive material out of reports, see [what the skills are designed to do](../../docs/design-principles.md).

## When it fits best

Coder is a strong fit when you can name the result you want, even if you don't know the solution yet. "Find why this export fails and fix the cause" is enough to begin. So are "review this branch for merge-blocking risk" and "update this guide to match the supported command."

Be explicit when the work has an important boundary: an API that callers depend on, a stored data format, a security-sensitive path, a performance target, or a system the agent must not touch. Coder uses that to decide what to preserve and what evidence it needs.

A real request can need several kinds of work. A defect repair might need an investigation, a code change, a regression test, and a documentation update. Coder takes them in order, gives each part what the earlier ones found, and keeps your outcome and boundaries the same throughout.

For a technology upgrade or migration, name the technology and the compatibility you expect. That lets the agent account for dependencies, old and new behavior, and recovery rather than treating the request as an ordinary edit.

## Give the agent a useful target

You don't need a formal specification. A short request becomes much more useful when it includes:

- the outcome you want and the code, diff, branch, or document in scope;
- the observed behavior, error, or business rule that matters;
- behavior, interfaces, data formats, or callers that must stay compatible;
- the checks your project uses, if they aren't easy to discover; and
- what the agent may read, edit, run, or contact.

For performance work, add the metric, a representative workload, the current measurement, the smallest improvement worth having, and any guardrails such as memory, cost, or error rate.

## Example requests

Each request below gets a different kind of result. Phrase yours however you like; what matters is the outcome you name and the boundaries you set.

### Understand and judge

These leave your source unchanged.

**Find a cause before deciding on a fix**

```text
Since Tuesday, the nightly import has been skipping some rows.
Find out why, but don't change anything yet.
```

You get the cause at the first point where behavior goes wrong, or a clear account of what's still unknown and the evidence needed next.

**Review a change before merge**

```text
Review this branch against main for issues that should block the merge.
```

You get findings ranked by the decision they force, each tied to its evidence.

**Know where to invest**

```text
Assess the test suite of this codebase and tell me where better tests would pay off first.
```

You get a prioritized roadmap that says which parts the agent inspected, sampled, or didn't reach.

**Learn how something works**

```text
Explain how a sign-in request is authenticated, from the login form to the session cookie.
```

You get an explanation at the depth you asked for, clear about what the agent didn't inspect.

**Check a result against criteria**

```text
Verify that the rate limiter lets the 100th request in a minute through and rejects the 101st.
```

You get a pass, fail, or unverified verdict against criteria fixed before any check ran.

**Agree on a migration before anyone edits**

```text
Plan the move from Python 3.10 to 3.13. Don't change any code yet.
```

The agent asks you the choices that are yours, then gives you ordered steps, how each will be verified, any choice you left open, and blockers.

### Change existing software

Each change comes with current evidence that it works, and with the tests, documentation, and interfaces it affects brought in line.

**Find and repair a defect**

```text
Uploading a CSV with a blank trailing line returns a 500 instead of a validation error.
Find the cause and fix it.
```

**Add a bounded feature**

```text
Add a --dry-run flag to the sync command.
It must report the changes it would make without writing anything.
```

**Improve a slow path**

```text
GET /api/orders takes about three seconds for accounts with a large history.
Find where the time goes, improve it, and keep peak memory within its current range.
```

**Remove duplication that slows every change**

```text
The discount rules are copied into checkout, invoicing, and refunds, so every pricing change needs three edits.
Consolidate them without changing any totals.
```

**Retire a feature**

```text
Remove the legacy XML export. Keep the JSON export working.
```

The feature is removed as far as you allowed, and what remains is reconciled, with each leftover removed or kept for a stated reason.

**Bring documentation back in line**

```text
The install section of our README no longer matches what the setup script does.
Update the guide so it describes the supported behavior.
```

### Build something new

**Start a small product**

```text
Build a command-line tool that renames photos by the date they were taken.
Put it in tools/photo-rename/.
```

You get a working, bounded product in that destination, with evidence for its main paths and a clear list of what's left out.

## Get Coder

Download the latest packaged [Coder skill][packaged-skill] as a ZIP. Before installing any third-party skill, inspect its instructions and executable files, and make sure you trust where it came from. A skill is a set of instructions that your agent may act on.

Then follow the collection's [installation guide][installation-guide] to put it where your agent can use it. For help writing a request, see [how to get good results](../../docs/using-skills.md). If a run misses, drifts, or leaves you uncertain, start with [troubleshooting](../../docs/troubleshooting.md), and [share a report](../../docs/feedback.md) with the evidence you can safely provide.

[packaged-skill]: ../../../../releases/latest/download/coder.zip
[installation-guide]: ../../docs/installation.md
