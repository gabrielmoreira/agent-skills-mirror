# Degardis Authoring

**Version:** `2.1.0` · **License:** [MIT](../../LICENSE) · [Changelog](CHANGELOG.md)

Turn a repeatable agent workflow into a skill that another agent can follow and you can inspect before release.

Degardis Authoring guides an agent from an intended outcome to maintained Degardis source, an evidence-grounded review, or a validated package. It helps the agent define the job clearly, put guidance where the executing agent will reach it, and check what the generated bundle actually teaches.

> [!CAUTION]
> A skill is guidance, not a guarantee. Review the source, generated bundle, evidence, and changes before relying on them, especially for high-impact work. An agent can misunderstand or skip guidance, and this skill can have defects of its own.

## Purpose-built for skill authors

A skill is a set of written instructions that an AI agent loads when a request matches what the skill is for. Writing one looks easy: describe the job and list the steps. The hard part is that the agent that later runs your skill has only what you wrote. It doesn't know what you meant, which examples you had in mind, or the conversation that shaped the text. Wherever you left a gap without noticing, it guesses.

Degardis Authoring is built around the ways skills tend to go wrong. Two terms help here: the **source** is the set of files you write and maintain for a skill, and Degardis compiles it into a **bundle**, the folder or ZIP that an agent actually installs and reads.

- **Getting picked for the right requests.** An agent decides whether to use a skill from its short description, before it reads anything else. Describe the skill too broadly and it takes over unrelated work; too narrowly and it never gets used. Degardis Authoring has the agent write the description, and the cues for each task, from how people actually ask, so the skill takes the requests it's meant for and leaves the rest alone.
- **No decision left to guesswork.** Before looking at what a skill says, the authoring agent works out from its goal everything the skill must settle: the inputs it needs, the permissions each action takes, every branch and fallback, where it stops, and what counts as done. Each of those needs a rule that reaches the executing agent before the decision. A rule the agent would have to infer counts as missing.
- **No rules that contradict each other.** When two rules can meet in the same situation and can't both be followed, the agent ends up picking one. The authoring agent checks how the parts of a skill depend on one another: the description against the kinds of request it covers, those requests against one another, and every condition against the situations that can reach it. A conflict is settled in the source, not left for the agent to settle mid-task.
- **No rule open to two readings.** If the text in an agent's path supports two readings that lead to different actions, and nothing in that path decides between them, the skill has a defect, even when its author knows which one was meant.
- **Reasons, not just rules.** A bare rule handles only the cases it lists. Each choice, precaution, or threshold in the skill carries what it prevents, what tells similar cases apart, and what decides between them, so the agent can handle a case nobody wrote down. A list that decides what's allowed is tested against a case it doesn't name, and then becomes a general rule or says plainly where it stops.
- **One rule, one place.** Copies of a rule drift apart until they disagree. Each point has a single owner, on the page where its decision is made, and each thing keeps one name, because a second name reads as a second thing.
- **Rules the agent actually reaches.** A Degardis skill is split into pages that the agent opens as it needs them. That keeps each run's reading light, but a rule on a page the agent never opens, or one that arrives after the decision it governs, does nothing. Degardis Authoring checks that each instruction lands where it's needed, in time to matter. When a page grows too long, it removes duplication or moves detail to where it's needed, never a distinction or check the agent relies on.
- **Facts that hold up.** A skill that states a threshold, a rule, or a procedure needs a reliable source for it. Degardis Authoring takes each fact from an authority that can settle it, keeps its version or date, and writes it into the skill. A fact that changes too often to copy is handled differently: the skill tells the agent where to look it up when it runs, and what to do if that source isn't available.
- **Working habits that hold under pressure.** An agent arrives able to reason and plan, but nothing in an ordinary request makes it stop and check its own work. A skill that adds expert knowledge without that discipline produces answers that are confident, well-informed, and impossible to verify. Degardis Authoring keeps a library of sixteen principles for those failures, such as asking before crossing a boundary, keeping what was checked apart from what was assumed, and keeping sensitive material out of reports. It gives each skill the principles its work needs, word for word, and adds principles from the skill's own field where they're needed. The skills in this collection carry principles chosen this way; the [design principles guide](../../docs/design-principles.md) explains each one.
- **Fixes at the cause.** When a skill misbehaves, the fix goes to the earliest point in the skill that made the failure possible, not to the sentence nearest the symptom, so the whole family of failures goes away. The corrected text replaces the faulty text rather than sitting beside it, where both would still apply.
- **Changes that keep what worked.** A revision accounts for every part of the skill it touches, each carried over, rewritten, merged, moved, or withdrawn with your say-so, and it rechecks how the changed parts fit with the rest. A shorter page is never taken as proof that what was cut didn't matter.
- **Growing without falling apart.** Skills get patched as people use them, and a run of reasonable-looking fixes can leave copies that disagree, one decision with several owners, or the same workaround showing up again and again. Degardis Authoring treats those signs as the evidence for restructuring. "Cleaner" alone isn't a reason, because every move risks breaking something that worked.

Every command, option, and format rule the agent relies on comes from the help and manual of the Degardis compiler it's actually using, such as the one you've installed or pointed it to, not from memory of another version.

> [!TIP]
> **When you create or revise a skill, choose a capable model and give it a generous reasoning budget.** Authoring asks the agent to keep routing, task boundaries, evidence, source structure, compiler behavior, and the future executing agent's reading path consistent all at once. A stronger setting gives it more room to trace those relationships and catch conflicting, unreachable, or incomplete guidance before packaging. It takes more time and usage, so lighter tasks, such as describing an existing bundle, can start at the default. See [how to choose model capability and reasoning](../../docs/using-skills.md#choose-model-capability-and-reasoning-by-evidence).

## How it checks a skill

Before a skill counts as finished, Degardis Authoring has the authoring agent read it the way the later agent will: can that agent find each instruction before the decision it governs, tell which branch applies, and act without inventing a missing rule?

It judges a skill in four layers, and none stands in for another:

- **Compiler checks:** what the Degardis compiler's own validation establishes.
- **Coverage:** every decision and end state the skill's job requires has an owner, and the generated pages lead the executing agent to it.
- **Meaning:** the executing agent can decide without guessing, even where instructions interact.
- **Reach:** each instruction arrives on the page where it's needed, before the decision it governs.

Two practices back those layers up:

- **Cold-reader rehearsal.** The authoring agent walks through the generated skill as an executing agent would: with the request and the host's context, but without the author's private knowledge. It covers each kind of request, both sides of every condition, and success, failure, and partial results, and it records each case. That exposes a rule that's present but unreachable, late, or too vague to decide from.
- **Independent evidence when it's worth the cost.** With your authorization, the agent can run a blind trial: a fresh agent gets the skill under test and an ordinary request, without being told what behavior is expected. A comprehension case checks whether that agent understands the skill; an execution case gives it a small, sanitized, representative fixture to work on. The verdict doesn't rest on the fresh agent's own account of how it did. Once that agent and any helpers it started have stopped, the authoring agent examines the full record of the run: the pages it opened, the tools it used, the questions it asked, what it produced, and the state of the files it worked on.

## When this skill fits

Use it when you want to create or improve Degardis source, understand why a skill routes poorly, check whether its instructions are reachable, or package it. It also helps with skills written any other way: it can tell you what one instructs an agent to do, and what a session with it shows about how it behaves.

Asking about a skill never turns into editing it. A defect the agent finds is reported, and fixed only when you ask for the fix and allow the change; saying that changes are acceptable isn't asking for one. Judging how a skill was authored takes its Degardis source, so for an installed skill or a ZIP on its own, the agent describes what it finds rather than guess at what was written, left out, or decided.

Building and packaging are in scope. Installing a skill, replacing an installed copy, publishing, and releasing aren't. Once you have a ZIP or built folder, use the collection's [installation guide](../../docs/installation.md).

## Example requests

Each request below gets a different kind of result. Phrase yours however you like; what matters is the outcome you name and what you allow.

**Turn a repeatable job into a skill**

```text
Create a Degardis skill that helps an agent review database schema changes.
Put the source in skills/schema-review/ under the MIT license.
```

You get new source with a clear purpose, the requests it should and shouldn't handle, and steps the later agent can follow, checked against the bundle it builds.

**Find out whether a skill is sound**

```text
Review skills/release-notes/ for defects. Don't change anything.
```

You get an evidence-based assessment, with each finding traced to the point in the source that causes it.

**Make an existing skill more reliable**

```text
Review skills/release-notes/ and revise it to make its routing clearer, its instructions easier to follow, and its normal runs cheaper.
```

The agent reviews first, then changes only what the review supports and you allowed.

**Agree on a change before anyone edits**

```text
Plan how to extend skills/release-notes/ to cover hotfix releases.
```

The agent asks you the decisions that are yours, then gives you a step-by-step plan that calls out unproven assumptions and any decision you left open.

**Understand an installed skill before trusting it**

```text
Describe this installed skill directory.
Explain its visible routing, instructions, links, and bundled resources.
```

**Learn from a session that went wrong**

```text
Here's the transcript of a session where the release-notes skill skipped the changelog.
What does it show about the skill?
```

**See how a fresh agent handles a skill**

```text
Run a blind trial of skills/release-notes/: give a fresh agent the skill and ask it to draft notes for the last three commits.
You may start one agent for the trial.
```

Each case ends as supported, failed, blocked, or inconclusive.

**Understand a design choice**

```text
Why does Degardis put a guide's conditions beside its link instead of on the guide's own page?
```

The answer comes from your compiler's own help and manual and the authoring guidance behind the choice.

**Package a source you have finished**

```text
Validate skills/schema-review/ and package it as a ZIP under .artifacts/.
```

## Get started

Download the latest packaged [Degardis Authoring skill][packaged-skill] as a ZIP. Before installing any third-party skill, inspect its instructions and executable files, and make sure you trust where it came from. A skill is a set of instructions that your agent may act on.

Then follow the collection's [installation guide][installation-guide] to put it where your agent can use it. For help writing a request, see [how to get good results](../../docs/using-skills.md). If a run doesn't behave as expected, start with [troubleshooting](../../docs/troubleshooting.md), and [share a report](../../docs/feedback.md) with the evidence you can safely provide.

[packaged-skill]: ../../../../releases/latest/download/degardis-authoring.zip
[installation-guide]: ../../docs/installation.md
