# Coder

**Version:** `1.3.0` · **License:** [MIT](../../LICENSE) · [Changelog](CHANGELOG.md)

Help your coding agent turn a software request into a result you can check, understand, and trust.

Coder guides an agent through the decisions that make software work succeed. The agent learns what result you really need, finds the contract the software must keep, stays inside the limits you set, and collects evidence that shows whether the result works. One skill covers the whole job: investigation, design, planning, implementation, review, documentation, verification, and measurement. An edited file is never treated as proof that the work is done.

> [!CAUTION]
> A skill is guidance, not a guarantee. Review the diff, evidence, and remaining risks before you rely on the result, especially for high-impact changes. An agent can misunderstand or skip guidance, and this skill can have defects or gaps.

## Better outcomes, not just more code

A coding agent can write a convincing patch quickly. The harder part is making sure the patch solves the right problem, keeps working what must still work, and checks the behavior that could fail. Coder keeps those questions in front of the agent:

- **A diagnosis comes before a fix.** For a defect, the agent first finds the expected behavior, reproduces the problem, and finds where things first go wrong. Only then does it edit anything.
- **The expected result comes from outside the code.** Requirements, interfaces, schemas, the software that uses the code, and meaningful tests decide what's correct. The code being questioned can't decide its own correct answer. So the agent never "fixes" a failing test by changing its expected value to match the code.
- **A passing check proves only what it ran.** A successful build is no evidence for behavior it never ran. An earlier check doesn't prove that a later edit still works.
- **A review finding comes with its evidence.** Each finding names the input that triggers it and where the behavior differs from the contract. It gives the expected and actual results and their effect on a user or system. It also says what the agent checked that could have proved it wrong. A structural problem names the future change it makes more expensive. A style preference isn't reported as a defect.
- **A test must be useful.** The agent adds or changes a test in your project only when the test would catch a real contract violation or a regression. A changed file alone isn't a reason.
- **A refactor keeps behavior.** It removes a named structural cost, such as one rule copied into three places. It keeps visible behavior and compatibility the same unless you ask for a change.
- **Performance work starts with measurement.** Before optimizing, the agent decides the metric, a realistic workload, and a baseline. It finds where the cost really is, and it checks limits such as memory use or error rate. If you only ask for a measurement, it reports what it measured and the conditions it measured under. It doesn't invent a threshold to judge the result.
- **A claim about "all" needs a full search.** "All references updated" or "no callers affected" needs a search that also finds the less obvious cases, such as registrations, reflection, and generated code.
- **Criteria come before the check.** When you ask whether something works, the agent decides what counts as a pass or a fail before it runs anything. A check it couldn't run is reported as unverified, never as passed.
- **Your choices stay yours.** When a plan depends on a choice only you can make, the agent asks you before it decides the design. An example is how completely a migration should remove the old approach. The plan names any choice you left open. If you say to continue without questions, the agent picks the option the evidence supports best for a preference and tells you, so you can change it. It never assumes a permission.
- **Allowing something isn't asking for it.** If you say breaking changes are acceptable, the agent may make one. It still considers what the break costs the code that calls yours, and it keeps a compatible design when that works just as well.
- **A limited request stays limited.** Assessing, investigating, reviewing, explaining, designing, planning, verifying, or measuring leaves your source unchanged. A documentation task doesn't become a code change. The agent reports defects it finds instead of fixing them, and it waits for you to ask for follow-up work, such as applying a review's fixes. A report or plan you ask for as a file isn't committed unless you ask to keep it in the project.
- **A command is judged by what it leaves behind.** When you ask the agent to investigate, explain, design, plan, verify, or measure, it may run commands that leave only temporary output. Examples are a new build folder or a test database it creates for the run. A command that writes to your files or a shared database, leaves a process running, calls a remote system, or costs money needs your approval. The kind of command doesn't matter.

You get a better handoff: a change you can review, evidence you can understand, and clear limits wherever the agent couldn't find an answer.

## Engineering judgment it brings

Coder also has guidance for the design decisions that make software easy or hard to maintain. It applies the part that fits the work.

- **Designs are compared, not taken from a first draft.** Before editing, the agent compares the workable designs where they really differ: who owns each responsibility, which way dependencies point, where state lives, and where the boundaries are. The first working idea, the smallest diff, or the closest existing pattern doesn't win automatically. A mechanism your project already has is one of the options. A design that removes a guarantee it gives must name that guarantee and the evidence for giving it up.
- **Architecture rules as questions, not slogans.** Each option is tested for clear ownership and cohesion, coupling and dependency direction, information hiding, one source of truth for each fact, code you can follow without hidden globals or mode flags, and how far the next change would spread. These questions show consequences. They don't force a pattern or score designs by acronym.
- **Abstractions only where they help.** Better names and existing boundaries come before a new layer. An interface comes from what its callers need. An extension point comes from alternatives your software actually supports. No factory, strategy, or wrapper is added just to fit a pattern. Code that only looks similar stays separate when the rules behind it can change separately.
- **Code that fits your project.** The agent follows your required style rules and the code around the change, so new code looks familiar to its maintainers. It checks relevant tool suggestions, including ones a normal build may not show. It replaces familiar syntax only when your project is adopting a new form or you ask for one. Any syntax it uses must work in all supported language versions. Formatting follows your project's rules without unrelated restyling.
- **Values that stay correct across boundaries.** When a value passes through configuration, serialization, templates, commands, protocols, or storage, the agent checks its type, spelling, defaults, missing values, and precision at each step. It verifies the value where it's finally used.
- **Interfaces treated as behavior, not styling.** For user-interface work, the agent models the flow as states a user can reach, such as loading, empty, error, or permission denied. It reuses your design system and components instead of starting a second one. Appearance, interaction, semantics, and accessibility are separate claims. A screenshot doesn't prove keyboard or screen-reader behavior, and anything the agent couldn't observe in your environment is reported as unverified.
- **Documentation written for a named reader.** Before writing, the agent decides who the reader is, what they want to do, and which kind of document helps them. Examples are a tutorial, a how-to guide, release notes, a runbook, a design proposal, or a decision record. Each definition, schema, or option list has one place, not copies on several pages. Every factual claim needs evidence from outside the documentation. Version-specific behavior matches the versions your project uses, and the agent checks the commands and examples a reader will run. API reference tells callers what they need without reading the code. A code comment says only what the code can't say.
- **Risky areas get extra care.** Security boundaries, failure and cleanup paths, concurrency, stored data, interfaces other software depends on, and logs and metrics each have their own guidance. For example, changing code and applying a migration are separate actions. A new constraint isn't added until the existing data is shown to meet it.

## Guidance for your stack

Coder adds guidance for the technology your project actually uses. It covers 25 languages, 19 frameworks and libraries, 5 runtimes and platforms, and 18 test frameworks. These include Python, TypeScript, Java, C#, Go, Rust, React, Django, Spring, ASP.NET Core, pytest, Jest, Playwright, and others.

The guidance knows about versions. For example, it knows that React 19 removed `ReactDOM.render` and that Python 3.13 removed standard-library modules such as `cgi` and `telnetlib`. It checks which versions your project uses before applying either rule.

For code documentation, it follows the conventions of your tool: Javadoc, KDoc, JSDoc and TSDoc, .NET XML comments, Python docstrings, Go doc comments, rustdoc, Swift DocC, and Doxygen.

## Where it stops

- **Changing code isn't permission to operate.** Each of these needs your approval for that action and target: deploying, publishing, pushing or opening a pull request, repairing data, applying a schema, using privileged access, reading production systems, and spending money.
- **A new dependency is your decision.** Before it adds one to an existing project, even one used only in development, the agent shows you what it would provide, the options, and what each would commit you to. It skips this only if you've already allowed it.
- **It's built for software work.** Requests outside software engineering are outside its scope.

For the habits Coder shares with the rest of the collection, such as asking before crossing a limit and keeping sensitive material out of reports, see [what the skills are designed to do](../../docs/design-principles.md).

## When it fits best

Coder fits best when you can name the result you want, even if you don't know the solution yet. "Find why this export fails and fix the cause" is enough to start. So are "review this branch for merge-blocking risk" and "update this guide to match the supported command."

Tell the agent when the work has an important limit: an API that callers depend on, a stored data format, a security-sensitive path, a performance target, or a system the agent must not touch. Coder uses that to decide what to keep and what evidence it needs.

A real request can need several kinds of work. A defect repair might need an investigation, a code change, a regression test, and a documentation update. Coder does them in order and gives each part what the earlier parts found. Your goal and limits stay the same throughout.

For a technology upgrade or migration, name the technology and the compatibility you expect. Then the agent can plan for dependencies, old and new behavior, and recovery, instead of treating the request as an ordinary edit.

## Give the agent a useful target

You don't need a formal specification. A short request is much more useful when it includes:

- the result you want, and the code, diff, branch, or document it's about;
- the behavior, error, or business rule you observed;
- behavior, interfaces, data formats, or callers that must stay compatible;
- the checks your project uses, if they aren't easy to find; and
- what the agent may read, edit, run, or contact.

For performance work, also give the metric, a realistic workload, the current measurement, the smallest improvement worth having, and any limits such as memory, cost, or error rate.

## Example requests

Each request below gets a different kind of result. Write yours in your own words. What matters is the result you ask for and the limits you set.

### Understand and judge

These leave your source unchanged.

**Find a cause before deciding on a fix**

```text
Since Tuesday, the nightly import has been skipping some rows.
Find out why.
```

You get the cause at the first point where behavior goes wrong. If the cause isn't clear, you get what's still unknown and the evidence needed next.

**Review a change before merge**

```text
Review this branch against main for issues that should block the merge.
```

You learn whether anything should block the merge. Then you get the findings, ranked by the decision each one requires and each with its evidence. Risks that aren't confirmed are listed separately.

**Know where to invest**

```text
Assess the test suite of this codebase and tell me where better tests would help most.
```

You get a prioritized roadmap. It says which parts the agent read, sampled, or didn't reach.

**Learn how something works**

```text
Explain how a sign-in request is authenticated, from the login form to the session cookie.
```

You get an explanation at the depth you asked for. Where it matters for the answer, it says what the agent didn't look at.

**Choose a design before building**

```text
How should we add multi-currency support to invoicing?
Existing invoices must keep their totals.
```

You get a design proposal with the alternatives and the trade-off that rules out each one. If the evidence can't decide between two designs, the proposal names the fact or decision that would.

**Check a result against criteria**

```text
Verify that the rate limiter lets the 100th request in a minute through and rejects the 101st.
```

You get a pass, fail, or unverified result, judged against criteria decided before any check ran.

**Measure what something costs**

```text
How long does the full test suite take on main, and which ten tests are slowest?
```

You get the measured result with the revision, configuration, and environment it was measured on.

**Agree on a migration before anyone edits**

```text
Plan the move from Python 3.10 to 3.13.
```

The agent first asks you the choices that are yours. Then it gives you the starting state the plan assumes and the steps in order. Each step says how it will be verified and names any open choice or blocker that stops it.

### Change existing software

Each change comes with current evidence that it works. The tests, documentation, and interfaces it affects are updated to match.

**Find and repair a defect**

```text
Uploading a CSV with a blank trailing line returns a 500 instead of a validation error.
Find the cause and fix it.
```

**Add a limited feature**

```text
Add a --dry-run flag to the sync command.
It must report the changes it would make without writing anything.
```

**Speed up a slow request**

```text
GET /api/orders takes about three seconds for accounts with a large history.
Find what makes it slow, improve it, and keep peak memory within its current range.
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

The feature is removed as far as you allowed. Anything left over is either removed or kept with a stated reason.

**Fix outdated documentation**

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

You get a working product with a clear scope in that folder. It comes with evidence for its main paths and a list of what's not included.

## Get Coder

Download the latest packaged [Coder skill][packaged-skill] as a ZIP. A skill is a set of instructions your agent may act on. Before you install any third-party skill, check its instructions and executable files, and make sure you trust where it came from.

Then follow the collection's [installation guide][installation-guide] to put it where your agent can use it. For help writing a request, see [how to get good results](../../docs/using-skills.md). If a run misses the goal, does something unexpected, or leaves you unsure, start with [troubleshooting](../../docs/troubleshooting.md). Then [share a report](../../docs/feedback.md) with the evidence you can safely provide.

[packaged-skill]: ../../../../releases/latest/download/coder.zip
[installation-guide]: ../../docs/installation.md
