# Contributing Guide

Thank you for your interest in contributing to Open Ecosystem Challenges!

Whether you're fixing a typo, proposing an adventure idea, or building an entire challenge, your contribution matters.

## Ways to Contribute

| Type                          | Description                                                    | Guide                                               |
|-------------------------------|----------------------------------------------------------------|-----------------------------------------------------|
| ✨ Improvements & Bug Fixes   | Improve docs, enhance challenge setup, fix bugs                | This page                                           |
| 💡 Adventure Ideas            | Propose a new adventure with a full implementation plan        | [Adventure Ideas](#propose-an-adventure-idea)       |
| 🏗️ New Adventures            | Build and implement a full adventure based on an approved idea | [Building Adventures](#build-a-new-adventure)       |
| 📖 Solution Walkthroughs      | Write a step-by-step guide for a completed challenge           | [Solution Walkthroughs](#write-a-solution-walkthrough) |

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Be respectful and constructive.

## Before You Start

1. **Check existing issues.** Search [open issues](https://github.com/dynatrace-oss/open-ecosystem-challenges/issues) before creating a new one.
2. **Determine if you need an issue:**
      - **Small fixes** (typos, broken links): No issue needed, just open a PR.
      - **Larger improvements & bug fixes**: Open an issue first to discuss.
      - **Adventure ideas**: No issue needed, submit your idea directly as a PR.
      - **New adventures & solution walkthroughs**: Pick up an existing issue.
3. **Claim the issue.** If working on an existing issue, comment to let others know you're on it.

## Pull Request Process

1. **Fork the repository** and create your branch from `main`.
2. **Make your changes** with clear, focused commits.
3. **Test your changes.** Run verification scripts if applicable.
4. **Open a pull request** with a clear description of what you changed and why.
5. **Address feedback.** Maintainers will review and may request changes.

Keep PRs focused. Smaller, single-purpose PRs are easier to review and merge.

## Developer Certificate of Origin (DCO)

This project uses the [Developer Certificate of Origin](https://developercertificate.org/) (DCO). All commits must be signed off to certify that you have the right to submit the code and agree to the DCO terms.

Sign off your commits by adding `-s` to your commit command:

```bash
git commit -s -m "Your commit message"
```

If you've already made commits without signing off, you can amend them:

```bash
git commit --amend -s --no-edit
git push --force-with-lease
```

The DCO is enforced automatically via [cncf/dco2](https://github.com/cncf/dco2). PRs without signed-off commits will be flagged.

## Getting Help

- **Ideas & bugs?** [Open an issue](https://github.com/dynatrace-oss/open-ecosystem-challenges/issues)
- **Questions & discussions?** [Open Ecosystem Community](https://community.open-ecosystem.com/c/challenges)

## License

This project is licensed under the [MIT License](https://github.com/dynatrace-oss/open-ecosystem-challenges/blob/main/LICENSE).

By contributing, you agree that your contributions will be licensed under the same MIT License.

---

## Propose an Adventure Idea

Have a concept for a new challenge? We'd love to hear it!

Adventure ideas are proposals for new challenges. You don't need to implement anything yet. Just describe what the
adventure could look like and what learners would gain from it.

### Before You Start

- **Check existing ideas.** Browse [adventure idea issues](https://github.com/dynatrace-oss/open-ecosystem-challenges/issues?q=is%3Aissue+is%3Aopen+label%3A%22adventure+idea%22)
  and [open PRs](https://github.com/dynatrace-oss/open-ecosystem-challenges/pulls) to make sure your idea hasn't already been submitted or is in the pipeline.
- **Focus on actions, not tools.** Frame challenges around what learners will *do* (e.g., "release safely", "observe AI
  systems") rather than tools they'll use (e.g., "Argo Rollouts", "OpenTelemetry").
- **Consider multiple levels.** Three levels (Beginner, Intermediate, Expert) are recommended but not required. Even a
  single well-designed level is valuable.

### How to Submit

1. **Fork** the repository on GitHub
2. **Copy** `ideas/adventure-idea-template.md` and rename it to `ideas/your-adventure-name.md`:
   ```
   cp ideas/adventure-idea-template.md ideas/your-adventure-name.md
   ```
3. **Fill in the template** and commit your changes
4. **[Open a pull request](https://github.com/dynatrace-oss/open-ecosystem-challenges/compare)** with the title `Adventure Idea: [emoji] Your Adventure Name`

No issue required. Submit your idea directly as a PR.

### From Idea to Adventure

After you open a PR:

1. **Review.** Maintainers review your idea for fit and feasibility.
2. **Feedback.** We may suggest adjustments or ask clarifying questions.
3. **Approval.** Once approved and merged, your idea becomes available for implementation via `make new-adventure`.
4. **Implementation.** You or another contributor picks it up, builds it, and the idea moves to `ideas/.implemented/`.

You're welcome to implement your own idea after approval, but there's no obligation to do so.

### Idea Folder Structure

Ideas are organized by their status:

```
ideas/
├── [your-idea].md      # Proposals & approved ideas (submitted via PR)
└── .implemented/       # Completed adventures (reference only)
```

### What Makes a Good Adventure Idea?

Strong adventure ideas share these qualities:

| Quality             | Description                                                          |
|---------------------|----------------------------------------------------------------------|
| **Action-oriented** | Focuses on what learners will *do*, not just what tools they'll use  |
| **Story-driven**    | Has an engaging narrative that motivates the challenges              |
| **Progressive**     | Multiple levels that build on each other (recommended, not required) |
| **Practical**       | Teaches skills applicable to real-world scenarios                    |
| **Self-contained**  | Can run entirely in a [devcontainer](https://containers.dev/)        |

### Calibrating Difficulty

The 🟢 Beginner / 🟡 Intermediate / 🔴 Expert labels set participant expectations before they start. Getting this right matters — a mislabeled level is frustrating regardless of which direction it's off.

Three levels are recommended but not required. A single well-scoped level or a two-level adventure is perfectly valid.

#### What each level feels like

**🟢 Beginner** — Get to know the tool. Participants encounter it for the first time and learn the fundamentals: what it does, how it's configured, and what "working" looks like. The challenge is contained and approachable.

**🟡 Intermediate** — Move into systems thinking. Participants have seen the tool before; now they see how it fits into a broader, more realistic setup. The interesting part is the integration — how things connect, interact, and break in non-obvious ways.

**🔴 Expert** — Something genuinely interesting. Not just "harder" — a qualitatively different challenge that rewards deep understanding. Adventure 01 is the best example: Expert isn't just more configuration, it's a completely different observability layer that ties everything together.

#### A quick self-check

Ask: *Could someone who has read the docs but never used this tool in a real project solve this in under an hour?*

- **Yes** → Beginner
- **No — they'd need to understand how two systems interact** → Intermediate
- **No — they'd need to understand the full architecture** → Expert

#### One level, a few new concepts

A common mistake is packing too much into a single level. Each level should introduce 2–3 new ideas — not a tour of everything the technology can do.

Adventure 01 is a useful reference: Beginner introduces Argo CD ApplicationSets → Intermediate adds Argo Rollouts and PromQL → Expert adds OpenTelemetry Collector and distributed tracing.

### Adventure Idea Template

A ready-to-use template is available at [`ideas/adventure-idea-template.md`](https://github.com/dynatrace-oss/open-ecosystem-challenges/blob/main/ideas/adventure-idea-template.md).

Copy it using the command below, fill in the placeholders, and follow the [How to Submit](#how-to-submit) steps above.

```
cp ideas/adventure-idea-template.md ideas/your-adventure-name.md
```

See [Echoes Lost in Orbit](https://github.com/dynatrace-oss/open-ecosystem-challenges/blob/main/ideas/.implemented/echoes-lost-in-orbit.md) for a complete example of a well-written idea.

### Writing Good Objectives

Objectives are verifiable outcomes, not tasks. Write them as the state a participant should reach, not the steps they should follow — specific enough that the verification script can check them directly.

| Task (avoid) | Outcome (aim for) |
|---|---|
| Fix the ApplicationSet | See two distinct Applications in the Argo CD dashboard |
| Add instrumentation | Send traces to the OpenTelemetry Collector at `http://localhost:30107` |

---

## Build a New Adventure

Ready to turn an approved idea into a full adventure? This guide walks you through the implementation process.

### Before You Start

- **Pick an approved idea.** Browse [open implementation issues](https://github.com/dynatrace-oss/open-ecosystem-challenges/issues?q=is%3Aissue+is%3Aopen+label%3A%22adventure+idea%22) to find unclaimed ideas. Once you pick one, comment on its issue to claim it.
- **Read the idea thoroughly.** Understand the story, objectives, and learning outcomes.
- **Have your own idea?** [Propose it](#propose-an-adventure-idea) — ideas go through review before they're available for implementation.
- **Ready to build?** Once an idea is approved and merged into `ideas/`, it's available via `make new-adventure`.

### What You'll Build

An adventure consists of:

| Component | Purpose |
|-----------|---------|
| **Challenge files** | The "broken" state participants will fix |
| **Documentation** | Story, objectives, hints, and solution walkthroughs |
| **Devcontainer** | Pre-configured environment with all required infrastructure |
| **Verification script** | Validates solutions and generates completion certificate |

### Adventure Structure

Use `00` as the adventure number during development. When your adventure is scheduled for release, maintainers will assign the final number and move it out of `planned/`.

```
adventures/planned/00-adventure-name/
├── README.md                    # Brief intro + link to docs
├── docs/
│   ├── index.yaml               # Adventure introduction
│   ├── beginner.yaml            # Level guide
│   ├── intermediate.yaml
│   ├── expert.yaml
│   └── solutions/
│       ├── beginner.md          # Solution walkthrough
│       ├── intermediate.md
│       └── expert.md
├── beginner/
│   ├── verify.sh                # Verification script
│   └── [challenge files]
├── intermediate/
│   └── ...
└── expert/
    └── ...

.devcontainer/00-adventure-name_01-beginner/
├── devcontainer.json
├── post-create.sh               # Runs once (install tools)
└── post-start.sh                # Runs every start (start services)
```

### Step-by-Step

#### 1. Scaffold the Files

Run the scaffolding script to generate the skeleton for your adventure level:

```bash
make new-adventure
```

This will prompt you to select an adventure and level, then generate:

- `adventures/planned/00-adventure-name/` — adventure base with `README.md` and `docs/index.yaml`
- `adventures/planned/00-adventure-name/docs/<level>.yaml` — level guide
- `adventures/planned/00-adventure-name/<level>/verify.sh` — verification script skeleton
- `.devcontainer/00-adventure-name_NN-level/` — `devcontainer.json`, `post-create.sh`, `post-start.sh`

Search for `TODO` in the generated files to find everything that needs filling in.

#### 2. Configure the Devcontainer

Open the generated `.devcontainer/00-adventure-name_NN-level/` files and fill in the TODOs.

For Kubernetes-based adventures, [Adventure 01](adventures/01-echoes-lost-in-orbit/) is a good reference for what features and setup scripts to use.

**post-create.sh** runs once when the container is created:
- Install CLI tools using setup scripts from `lib/` — every script accepts a `--version` flag to pin a specific version. Run any script with `--help` to see available flags and defaults.
- Pull container images
- Set up one-time configurations

Example calls in `post-create.sh`:
```bash
"$REPO_ROOT/lib/kubernetes/init.sh"                                            # use default versions
"$REPO_ROOT/lib/argocd/init.sh" --version v3.5.0                              # pin a version
"$REPO_ROOT/lib/argocd/init.sh" --read-only --version v3.5.0                  # combine flags
"$REPO_ROOT/lib/kubernetes/init.sh" --kubectl-version v1.35.0 --helm-version v4.1.0  # per-tool versions
```

**post-start.sh** runs every time the container starts:
- Start services (databases, clusters, etc.)
- Apply initial state

**Infrastructure constraints:**

Codespaces run on 2 cores and 8 GB RAM by default. Design your adventure within these limits — avoid memory-hungry workloads running in parallel and prefer lightweight images where possible.

Post-create should finish in under 15 minutes, but aim for well under that.

#### 3. Build the Working Solution

Implement the fully working version first. This is what the solved challenge looks like where everything works correctly.

This approach helps you:
- Understand the problem space before designing the challenge
- Ensure the challenge is actually solvable
- Have a reference implementation for the solution walkthrough

#### 4. Introduce the Challenges

Work backwards from your working solution to create the "broken" state participants will fix.

Good challenges are:
- **Realistic.** Introduce issues that could happen in real-world scenarios.
- **Discoverable.** Problems should be findable using standard tools and techniques.
- **Focused.** Each issue should teach something from the learning objectives.
- **Solvable.** Don't require knowledge outside what's being taught.

Not sure if a challenge belongs at Beginner, Intermediate, or Expert? See [Calibrating Difficulty](#calibrating-difficulty) for concrete signals and time expectations.

#### 5. Write the Documentation

Fill in the generated `docs/<level>.yaml` — it already contains the story, objectives, and learning outcomes from the idea file. Add:
- Architecture overview (how the level is set up)
- UI access instructions with port numbers
- Where to start investigating
- Helpful links to external docs

No spoilers — save those for a `solutions/<level>.md` file.

See [Lex Imperfecta's beginner level](adventures/05-lex-imperfecta/docs/beginner.yaml) for a good example.

#### 6. Create the Verification Script

Fill in the generated `<level>/verify.sh`. It already has the boilerplate wired up — add your checks between the `print_sub_header` and the summary block.

A good verification script:
- Passes when the challenge is solved correctly
- Fails with helpful error messages when not solved
- Generates a certificate users can copy to claim completion

**Check outcomes, not implementation.** Verify the state the participant should have reached — a service is healthy, traces are present in Jaeger, a metric is being collected — not how they got there. File content checks (`check_file_contains`) are a last resort: they break for valid alternative solutions and reward copy-pasting over understanding. If your objective says "see traces in Jaeger", your verification should check that traces exist, not that a specific import was added.

Browse `lib/scripts/` to see the available helper functions.

#### 7. Final Test Run

Before submitting:

1. **Start fresh.** Open a new Codespace to test the full experience.
2. **Solve the challenge.** Complete it as a participant would.
3. **Run verification.** Ensure `verify.sh` passes when solved and fails when not.
4. **Check all links.** Documentation should be complete and accurate.

### Tips

- **[Open a draft PR early.](https://github.com/dynatrace-oss/open-ecosystem-challenges/compare)** Get feedback on structure before completing everything.
- **Ship one level at a time.** Each level gets its own PR — start with one, get it working, then build the next. Use `Part of #<tracking-issue>` on all but the last PR, and `Closes #<tracking-issue>` on the final one so the tracking issue closes automatically.
- **Test on slow connections.** Codespace startup time matters.
- **Write clear error messages.** Help participants understand what went wrong without giving away the solution.

---

## Write a Solution Walkthrough

Solution walkthroughs help participants who get stuck and serve as learning resources for those who want to understand the "why" behind each solution.

> ⚠️ **Walkthroughs are only accepted after the challenge deadline has passed.** This protects the experience for active participants.

### How to Contribute

Browse [walkthrough issues](https://github.com/dynatrace-oss/open-ecosystem-challenges/issues?q=is%3Aissue+is%3Aopen+label%3A%22solution+walkthrough%22), comment to claim a level, and [submit your walkthrough as a PR](https://github.com/dynatrace-oss/open-ecosystem-challenges/compare). Walkthroughs can take any form:

- **External content** — a blog post, video, or any public resource. Just link to it from the adventure's solutions page.
- **In-repo** — a markdown file in `adventures/XX-adventure-name/docs/solutions/`.

The most useful walkthroughs don't just show what to fix — they explain *why* something was broken and how you'd reason your way to the solution.
