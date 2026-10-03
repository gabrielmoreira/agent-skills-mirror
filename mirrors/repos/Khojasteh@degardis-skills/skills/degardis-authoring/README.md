# Degardis Authoring

**Version:** `2.0.0` · **License:** [MIT](../../LICENSE) · [Changelog](CHANGELOG.md)

Turn a repeatable agent workflow into a skill that another agent can follow and you can inspect before release.

Degardis Authoring guides an agent from an intended outcome to maintained Degardis source, an evidence-grounded review, or a validated package. It helps the agent define the job clearly, put guidance where the executing agent will reach it, and check what the generated bundle actually teaches.

> [!CAUTION]
> A skill is guidance, not a guarantee. Review the source, generated bundle, evidence, and changes before relying on them, especially for high-impact work. An agent can misunderstand or skip guidance, and this skill can have defects of its own.

## Purpose-built for skill authors

A skill is a set of written instructions that an AI agent loads when a request matches what the skill is for. Writing one looks easy: describe the job and list the steps. The hard part is that the agent that later runs your skill has only what you wrote. It doesn't know what you meant, which examples you had in mind, or the conversation that shaped the text. Wherever you left a gap without noticing, it guesses.

Degardis Authoring is built around the ways skills tend to go wrong, and it guides the authoring agent past each one:

- **Getting picked for the right requests.** An agent decides whether to use a skill from its short description, before it reads anything else. Describe the skill too broadly and it takes over unrelated work; too narrowly and it never gets used. Degardis Authoring has the agent write the description, and the cues for each task, from how people actually ask, so the skill takes the requests it's meant for and leaves the rest alone.
- **Rules the agent actually reaches.** A Degardis skill is split into pages that the agent opens as it needs them. That keeps each run's reading light, but a rule on a page the agent never opens, or one that arrives after the decision it governs, does nothing. Degardis Authoring checks that each instruction lands where it's needed, in time to matter.
- **Steps an agent can decide.** You know what "use good judgment" means for your job; the agent running your skill doesn't. Degardis Authoring has each step say what it's for, what tells its branches apart, and what to do when that information is missing. A gap the agent would have to fill with its own judgment counts as a defect in the skill.
- **Facts that hold up.** A skill that states a threshold, a rule, or a procedure needs a reliable source for it. Degardis Authoring takes each fact from an authority that can settle it, keeps its version or date, and writes it into the skill. A fact that changes too often to copy is handled differently: the skill tells the agent where to look it up when it runs, and what to do if that source isn't available.
- **Working habits that hold under pressure.** An agent arrives able to reason and plan, but nothing in an ordinary request makes it stop and check its own work. A skill that adds expert knowledge without that discipline produces answers that are confident, well-informed, and impossible to verify. Degardis Authoring keeps a library of fifteen principles for those failures, such as asking before crossing a boundary, keeping what was checked apart from what was assumed, and keeping sensitive material out of reports. It gives each skill the principles its work needs, word for word, and adds principles from the skill's own field where they're needed. The skills in this collection carry principles chosen this way; the [design principles guide](../../docs/design-principles.md) explains each one.
- **Growing without falling apart.** Skills get patched as people use them, and a run of reasonable-looking fixes can leave copies that disagree, one decision with several owners, or the same workaround showing up again and again. Degardis Authoring treats those signs as the evidence for restructuring. "Cleaner" alone isn't a reason, because every move risks breaking something that worked.

Every command, option, and format rule the agent relies on comes from the help and manual of the Degardis compiler it's actually using, such as the one you've installed or pointed it to, not from memory of another version.

> [!TIP]
> **When you create or revise a skill, choose a capable model and give it a generous reasoning budget.** Authoring asks the agent to keep routing, task boundaries, evidence, source structure, compiler behavior, and the future executing agent's reading path consistent all at once. A stronger setting gives it more room to trace those relationships and catch conflicting, unreachable, or incomplete guidance before packaging. It takes more time and usage, so lighter tasks, such as describing an existing bundle, can start at the default. See [how to choose model capability and reasoning](../../docs/using-skills.md#choose-model-capability-and-reasoning-by-evidence).

## Choose the outcome you need

Two terms help here. The **source** is the set of files you write and maintain for a skill. Degardis compiles it into a **bundle**: the folder or ZIP that an agent actually installs and reads.

Pick the row that matches what you're after. Each kind of request gets its own result, so a request to look at a skill never turns into an edit you didn't ask for. You can combine several in one request; the agent works through them in order.

| If you want to… | Ask the agent to… | What you get |
| --- | --- | --- |
| Turn a job you repeat into a skill | Create a skill | New source with a clear purpose, the requests it should and shouldn't handle, and steps the later agent can follow, checked against the bundle it builds. |
| Fix or extend a skill you already have | Revise the skill | Changes limited to what you allowed, with their effect on everything the skill already did accounted for and checked against the final build. |
| Know whether a skill is sound | Review it | An assessment based on evidence, with nothing changed. |
| Agree on a change before anyone edits | Plan the work | A step-by-step plan that calls out open decisions and unproven assumptions, with nothing changed. |
| Understand a skill you didn't write, with or without its source | Describe it | What its description, instructions, links, and files tell an agent to do, and what they leave unsettled. |
| Learn from a session that has already happened, using its transcript and outputs | Evaluate the session | What that session shows about the skill, and no more. When something went wrong, the agent traces it to the earliest point in the skill that allowed it, and keeps skill defects apart from causes such as a missing tool, a permission, or the host. |
| See how the skill behaves for an agent that has never seen it | Run a blind trial | With your go-ahead, a fresh agent receives the skill and an ordinary request. Each case ends as supported, failed, blocked, or inconclusive. |
| Learn how Degardis works or why a skill is shaped a certain way | Explain it | An answer based on your compiler's own help and manual and on the authoring guidance behind the choice. |
| Get something you can install | Build or package it | A validated folder or ZIP built from exactly the source you supplied. Installing and publishing it are up to you. |

Evaluation isn't limited to skills written in Degardis. You can share a session from any skill, or supply any skill exactly as it is for a trial.

If a review or evaluation turns up a defect in Degardis source and you've said the agent may fix it, the agent moves on to revising the skill, or to planning the fix if your setup doesn't allow it to change the source.

## Improve what the next agent receives

Before a skill counts as finished, Degardis Authoring has the authoring agent read it the way the later agent will: can that agent find each instruction before the decision it governs, tell which branch applies, and act without inventing a missing rule?

It judges a skill in four layers, and none stands in for another:

- **Compiler checks:** what the Degardis compiler's own validation establishes.
- **Coverage:** every decision and end state the skill's job requires has an owner, and the generated pages lead the executing agent to it.
- **Meaning:** the executing agent can decide without guessing, even where instructions interact.
- **Reach:** each instruction arrives on the page where it's needed, before the decision it governs.

Two practices back those layers up:

- **Cold-reader rehearsal.** The authoring agent rehearses the generated skill as an executing agent would: with the request and the host's context, but without the author's private knowledge. That exposes a rule that's present but unreachable, late, or too vague to decide from.
- **Independent evidence when it's worth the cost.** With your authorization, the agent can run a blind trial: a fresh agent gets the skill under test and an ordinary request, without being told what behavior is expected. A comprehension case checks whether that agent understands the skill; an execution case gives it a small, sanitized, representative fixture to work on. The verdict doesn't rest on the fresh agent's own account of how it did. Once that agent and any helpers it started have stopped, the authoring agent examines the full record of the run: the pages it opened, the tools it used, the questions it asked, what it produced, and the state of the files it worked on.

## When this skill fits

Use it when you want to create or improve Degardis source, understand why a skill routes poorly, check whether its instructions are reachable, or package it. It also evaluates how any skill behaves, whether or not it's written in Degardis. If the original source is missing, the agent can inspect an installed folder or ZIP and explain both the visible instructions and the limits of a review without source.

Building and packaging are in scope. Installing a skill, replacing an installed copy, publishing, and releasing aren't. Once you have a ZIP or built folder, use the collection's [installation guide](../../docs/installation.md).

## Example requests

**Create a skill for a repeatable job**

```text
Create a Degardis skill that helps an agent review database schema changes.
Put the source in skills/schema-review/.
```

**Make an existing skill more reliable**

```text
Review skills/release-notes/ and revise it to make its routing clearer, its instructions easier to follow, and its normal runs cheaper.
```

**Understand an installed skill before trusting it**

```text
Review this installed skill directory without source.
Explain its visible routing, instructions, links, and bundled resources.
```

**Package a source you have finished**

```text
Validate skills/schema-review/ and package it as a ZIP under .artifacts/.
```

## Get started

Download the latest packaged [Degardis Authoring skill][packaged-skill] as a ZIP. Before installing any third-party skill, inspect its instructions and executable files, and make sure you trust where it came from. A skill is a set of instructions that your agent may act on.

Then follow the collection's [installation guide][installation-guide] to put it where your agent can use it. For help writing a request, see [how to get good results](../../docs/using-skills.md). If a run doesn't behave as expected, start with [troubleshooting](../../docs/troubleshooting.md), and [share a report](../../docs/feedback.md) with the evidence you can safely provide.

[packaged-skill]: ../../../../releases/latest/download/degardis-authoring.zip
[installation-guide]: ../../docs/installation.md
