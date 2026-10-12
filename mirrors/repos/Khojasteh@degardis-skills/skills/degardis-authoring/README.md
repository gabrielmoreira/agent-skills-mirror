# Degardis Authoring

**Version:** `2.2.0` · **License:** [MIT](../../LICENSE) · [Changelog](CHANGELOG.md)

Turn a repeatable agent workflow into a skill that another agent can follow and that you can check before you release it.

Degardis Authoring guides an agent from a goal to one of three results: maintained Degardis source, a review based on evidence, or a validated package. It helps the agent define the job clearly, put each instruction where the executing agent will find it, and check what the generated bundle really teaches.

> [!CAUTION]
> A skill is guidance, not a guarantee. Review the source, generated bundle, evidence, and changes before you rely on them, especially for high-impact work. An agent can misunderstand or skip guidance, and this skill can have its own defects.

## Built for skill authors

A skill is a set of written instructions that an AI agent loads when a request matches the skill's purpose. Writing one looks easy: describe the job and list the steps. The difficulty is that the agent that later runs your skill has only what you wrote. It doesn't know what you meant, which examples you had in mind, or the conversation that shaped the text. Where you left a gap without noticing, it guesses.

Degardis Authoring is built around the common ways skills fail. Two terms help here. The **source** is the set of files you write and maintain for a skill. Degardis compiles the source into a **bundle**: the folder or ZIP that an agent installs and reads.

- **Chosen for the right requests.** An agent decides whether to use a skill from its short description, before it reads anything else. If the description is too broad, the skill takes over unrelated work. If it's too narrow, the skill is never used. The authoring agent writes the description, and the cues for each task, from the way people really ask. Then the skill takes the requests it's meant for and ignores the rest.
- **No decision left to guessing.** From the skill's goal, the authoring agent works out everything the skill must decide, in the terms of the skill's field. This includes what an expert would have to get right, and what to do when an input is missing, partial, unclear, or conflicting. It also includes the permissions each action needs, every branch and fallback, where the work stops, and what counts as done. The agent lists all of this before it compares the list with the skill's text, so it also finds gaps the skill never mentions. Each item needs a rule that reaches the executing agent before the decision. A rule the agent would have to work out by itself counts as missing.
- **No conflicting rules.** If two rules can apply in the same situation and can't both be followed, the agent has to pick one. The authoring agent checks how the parts of a skill depend on each other. It compares the description with the kinds of request it covers, those requests with each other, and every condition with the situations that can reach it. A conflict is resolved in the source, not left for the agent to resolve during a task.
- **No rule with two meanings.** Suppose the text in the agent's path can be read in two ways that lead to different actions, and nothing in that path decides between them. Then the skill has a defect, even if its author knows which meaning was intended.
- **Reasons, not only rules.** A rule without a reason covers only the cases it lists. Each choice, precaution, or threshold in the skill says what it prevents, how to tell similar cases apart, and what decides between them. Then the agent can handle a case nobody wrote down. A list that decides what's allowed is tested against a case it doesn't name. Then it either becomes a general rule or says clearly where it ends.
- **One rule, one place.** Copies of a rule change separately until they disagree. Each point has one owner, on the page where its decision is made. Each thing keeps one name, because a second name looks like a second thing.
- **Rules the agent actually reads.** A Degardis skill is split into pages that the agent opens when it needs them. This keeps each run's reading small. But a rule on a page the agent never opens, or a rule that arrives after its decision, has no effect. Degardis Authoring checks that each instruction arrives where it's needed, in time. When a page gets too long, it removes duplicates or moves detail to where it's needed. It never removes a distinction or check the agent depends on.
- **Reliable facts.** A skill that states a threshold, a rule, or a procedure needs a reliable source for it. Degardis Authoring takes each fact from a source with the authority to confirm it, keeps its version or date, and writes it into the skill. Some facts change too often to copy. For those, the skill tells the agent where to look them up during the run, and what to do if that source isn't available.
- **Good working habits, even under pressure.** An agent can already reason and plan. But nothing in an ordinary request makes it stop and check its own work. A skill that adds expert knowledge without that discipline gives answers that are confident and well informed, but impossible to verify. Degardis Authoring keeps a library of sixteen principles against these failures. Examples are asking before crossing a limit, keeping what was checked separate from what was assumed, and keeping sensitive material out of reports. It gives each skill the principles its work needs, word for word, and adds principles from the skill's own field where they're needed. The skills in this collection use principles chosen this way. The [design principles guide](../../docs/design-principles.md) explains each one.
- **Fixes at the cause.** When a skill behaves badly, the fix goes to the earliest point in the skill that made the failure possible, not to the sentence closest to the symptom. That removes the whole group of related failures. The corrected text replaces the wrong text. It isn't added beside it, where both would still apply.
- **Changes that keep what worked.** A revision accounts for every part of the skill it touches. Each part is kept, rewritten, merged, or moved. A part is removed only with your approval. The agent then checks again how the changed parts fit with the rest. A shorter page is never taken as proof that the removed text didn't matter. If a change would also affect a case you didn't ask about, that part waits for your approval. A review of the fixes checks exactly what changed, instead of reviewing everything again.
- **Growing without breaking.** Skills get fixed as people use them. Many reasonable-looking fixes can leave copies that disagree, one decision with several owners, or the same workaround appearing again and again. Degardis Authoring treats these signs as the evidence for restructuring. "Cleaner" alone isn't a reason, because every move can break something that worked.

Every command, option, and format rule the agent uses comes from the help and manual of the Degardis compiler it's actually using, such as the one you installed or pointed it to. It doesn't come from memory of another version.

> [!TIP]
> **When you create or revise a skill, choose a capable model and give it a large reasoning budget.** Authoring asks the agent to keep many things consistent at once: routing, task boundaries, evidence, source structure, compiler behavior, and what the executing agent will read. A stronger setting gives it more room to follow those connections and find conflicting, unreachable, or incomplete guidance before packaging. It takes more time and usage, so lighter tasks, such as describing an existing bundle, can start with the default. See [how to choose model capability and reasoning](../../docs/using-skills.md#choose-model-capability-and-reasoning-by-evidence).

## How it checks a skill

Before a skill counts as finished, the authoring agent reads it the way the later agent will. Can that agent find each instruction before the decision it controls? Can it tell which branch applies? Can it act without inventing a missing rule?

It judges a skill on four levels, and no level replaces another:

- **Compiler checks:** what the Degardis compiler's own validation confirms.
- **Coverage:** every decision and end state the skill's job needs has an owner, and the generated pages lead the executing agent to it.
- **Meaning:** the executing agent can decide without guessing, even where instructions interact.
- **Reach:** each instruction appears on the page where it's needed, before the decision it controls.

Two practices support these checks:

- **Cold-reader rehearsal.** The authoring agent walks through the generated skill as an executing agent would. It has the request and the host's context, but not the author's private knowledge. It covers each kind of request, both sides of every condition, and success, failure, and partial results, and it records each case. This finds rules that exist but can't be reached, arrive too late, or are too vague to act on.
- **Independent evidence when it's worth the cost.** If you allow it, the agent can run a blind trial. A fresh agent gets the skill and an ordinary request, but isn't told what behavior is expected. A comprehension case checks whether that agent understands the skill. An execution case gives it a small, realistic example to work on, with no sensitive data in it. The result doesn't depend on the fresh agent's own report of how it did. After that agent and any helpers it started have stopped, the authoring agent examines the full record: the pages it opened, the tools it used, the questions it asked, what it produced, and the final state of the files it worked on.

## When this skill fits

Use it to create or improve Degardis source, to understand why a skill handles the wrong requests or picks the wrong task, to check whether its instructions can be reached, or to package it. It also helps with skills written in other ways. It can tell you what such a skill instructs an agent to do, and what a session with it shows about how it behaves.

Asking about a skill never leads to editing it. The agent reports any defect it finds, and fixes it only when you ask for the fix and allow the change. Saying that changes are acceptable isn't asking for one. If you ask for a change but don't allow the edit, you get a plan instead. The agent runs the scripts or tests of a skill it works on only with your permission, and keeps what they write in temporary locations.

Judging how a skill was written needs its Degardis source. For an installed skill or a ZIP alone, the agent describes what it finds. It doesn't guess what was written, left out, or decided.

Building and packaging are part of this skill. Installing a skill, replacing an installed copy, publishing, and releasing aren't. When you have a ZIP or built folder, use the collection's [installation guide](../../docs/installation.md).

## Example requests

Each request below gets a different kind of result. Write yours in your own words. What matters is the result you ask for and what you allow.

**Turn a repeatable job into a skill**

```text
Create a Degardis skill that helps an agent review database schema changes.
Put the source in skills/schema-review/ under the MIT license.
```

You get new source with a clear purpose, the requests it should and shouldn't handle, and steps the later agent can follow. It's checked against the bundle it builds. You choose the skill's name. If you don't give one, the agent suggests some.

**Find out whether a skill has defects**

```text
Review skills/release-notes/ for defects.
```

You get an assessment based on evidence. Each finding is traced to the point in the source that causes it.

**Make an existing skill more reliable**

```text
Review skills/release-notes/ and revise it to make its routing clearer, its instructions easier to follow, and its normal runs cheaper.
```

The agent reviews first. Then it changes only what the review supports and what you allowed.

**Agree on a change before anyone edits**

```text
Plan how to extend skills/release-notes/ to cover hotfix releases.
```

The agent first asks you the decisions that are yours. Then it gives you a step-by-step plan. The plan points out assumptions that aren't proven and any decision you left open.

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

The answer comes from your compiler's own help and manual, and from the authoring guidance behind the choice.

**Package a source you have finished**

```text
Validate skills/schema-review/ and package it as a ZIP under .artifacts/.
```

You get the ZIP and an identity for its exact contents. Later, you can use the identity to confirm that a copy is the same bundle.

## Get started

Download the latest packaged [Degardis Authoring skill][packaged-skill] as a ZIP. A skill is a set of instructions your agent may act on. Before you install any third-party skill, check its instructions and executable files, and make sure you trust where it came from.

Then follow the collection's [installation guide][installation-guide] to put it where your agent can use it. For help writing a request, see [how to get good results](../../docs/using-skills.md). If a run doesn't behave as you expected, start with [troubleshooting](../../docs/troubleshooting.md). Then [share a report](../../docs/feedback.md) with the evidence you can safely provide.

[packaged-skill]: ../../../../releases/latest/download/degardis-authoring.zip
[installation-guide]: ../../docs/installation.md
