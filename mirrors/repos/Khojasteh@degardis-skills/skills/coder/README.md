# Coder

**Version:** `1.0.0` · **License:** [MIT](../../LICENSE) · [Changelog](CHANGELOG.md)

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
- **A bounded request stays bounded.** A documentation task doesn't turn into a code change, and defects found along the way are reported rather than quietly fixed.

You get a better handoff: a change you can review, evidence you can interpret, and clear limits wherever the agent couldn't establish an answer.

## What you can ask for

Coder handles ten kinds of software outcome, in an existing codebase or a new, bounded product:

| Ask it to… | You get… |
| --- | --- |
| Assess a codebase | A prioritized, evidence-backed roadmap that says which parts it inspected, sampled, or didn't reach. |
| Plan work | A decision-ready plan with ordered steps, how each will be verified, open decisions, and blockers. |
| Investigate a problem | The cause at the first point where behavior goes wrong, or a clear account of what's still unknown and the evidence needed next. |
| Review code or a change | Findings ranked by the decision they force, each tied to its evidence. |
| Explain how software works | An explanation at the depth you asked for, grounded in the code and clear about what it didn't inspect. |
| Write or revise documentation | Pages whose claims come from the software itself, with their links and examples checked. |
| Implement a change | A feature, fix, refactor, performance improvement, upgrade, or migration, with affected contracts reconciled and current evidence that it works. |
| Withdraw a feature | The capability removed as far as you authorized, with what remains reconciled and leftovers removed or kept for a stated reason. |
| Create a new product | A working, bounded product in the destination you choose, with evidence for its main paths and a clear list of what's left out. |
| Verify an outcome | A pass, fail, or unverified verdict against criteria fixed before any check ran. |

Assessments, investigations, reviews, explanations, and verifications leave your source unchanged.

A real request can need more than one of these. A defect repair might need an investigation, a code change, a regression test, and a documentation update. Coder takes them in order, gives each part what the earlier ones found, and keeps your outcome and boundaries the same throughout.

## Guidance for your stack

Coder brings in guidance for the technology your project actually uses. It covers 25 languages, 19 frameworks and libraries, 5 runtimes and platforms, and 18 test frameworks: Python, TypeScript, Java, C#, Go, Rust, and many more, along with React, Django, Spring, ASP.NET Core, pytest, Jest, Playwright, and others.

That guidance is version-aware. It knows, for example, that React 19 removed `ReactDOM.render` and that Python 3.13 dropped standard-library modules such as `cgi` and `telnetlib`, and it checks the versions your project configures before applying either.

For code documentation, it follows the conventions of the tool you use: Javadoc, KDoc, JSDoc and TSDoc, .NET XML comments, Python docstrings, Go doc comments, rustdoc, Swift DocC, and Doxygen.

## Where it stops

- **Changing code isn't permission to operate.** Deploying, publishing, repairing data, applying a schema, using privileged access, reading production systems, and spending money each need your go-ahead for that action and target.
- **Follow-on work waits for your ask.** A review doesn't apply its fixes, an assessment doesn't start on its roadmap, and a plan doesn't start building until you request that work.
- **It's built for software work.** Requests outside software engineering are outside its scope.

For the habits Coder shares with the rest of the collection, such as asking before crossing a boundary and keeping sensitive material out of reports, see [what the skills are designed to do](../../docs/design-principles.md).

## When it fits best

Coder is a strong fit when you can name the result you want, even if you don't know the solution yet. "Find why this export fails and fix the cause" is enough to begin. So are "review this branch for merge-blocking risk" and "update this guide to match the supported command."

Be explicit when the work has an important boundary: an API that callers depend on, a stored data format, a security-sensitive path, a performance target, or a system the agent must not touch. Coder uses that to decide what to preserve and what evidence it needs.

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

**Find and repair a defect**

```text
Uploading a CSV with a blank trailing line returns a 500 instead of a validation error.
Find the cause and fix it.
```

**Review a change before merge**

```text
Review this branch against main for issues that should block the merge.
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

**Bring documentation back in line**

```text
The install section of our README no longer matches what the setup script does.
Update the guide so it describes the supported behavior.
```

## Get Coder

Download the latest packaged [Coder skill][packaged-skill] as a ZIP. Before installing any third-party skill, inspect its instructions and executable files, and make sure you trust where it came from. A skill is a set of instructions that your agent may act on.

Then follow the collection's [installation guide][installation-guide] to put it where your agent can use it. For help writing a request, see [how to get good results](../../docs/using-skills.md). If a run misses, drifts, or leaves you uncertain, start with [troubleshooting](../../docs/troubleshooting.md), and [share a report](../../docs/feedback.md) with the evidence you can safely provide.

[packaged-skill]: ../../../../releases/latest/download/coder.zip
[installation-guide]: ../../docs/installation.md
