# Contributing to OpenMotion

[简体中文](CONTRIBUTING.zh-CN.md)

## Start with one useful contribution

Designers, creators, prompt authors and engineers are all welcome. The [OpenMotion Library](library/README.md) is the shared home for creative contributions; core production workflow changes remain in `skills/`.

| Contribution | Location | Include |
| --- | --- | --- |
| A reusable method | `library/skills/<name>/SKILL.md` | Name and description frontmatter, a clear trigger, steps and a real usage example. |
| A template | `library/templates/<name>/` | Editable source or a maintained source link, `TEMPLATE.md`, preview and adaptation checks. |
| A motion component | `library/components/<name>/` | Source or a labeled recipe, timing, inputs, editable choices and review notes. |
| A motion design system | `library/design-systems/<name>/MOTION_DESIGN.md` | Visual language, pacing, movement, sound, references and review criteria. |
| A Brandkit | `library/brandkits/<name>/BRANDKIT.md` | Confirmed facts, copy, identity, asset locations and permission notes. |
| Runtime / editor / agent support | Existing modules linked in the [architecture](docs/product/architecture.md) | A reproducible case, focused change and checks for the affected boundary. |

Use the [entry checklist](library/ENTRY_TEMPLATE.md), link the new entry from its collection, and preserve sources and licenses. Label references, recipes and editable examples accurately. Adding a folder does not register it in Studio, the MCP workflow registry or the default five-Skill installation. Packaging uses an explicit file list.

For published motion guidance source and locale metadata, use the [catalog contribution loop](https://github.com/nexu-io/openmotion/tree/main/library/templates/catalog#change-a-template). Stage changes before running the storage-policy check. New media needs no CMS account; maintainers prepare final media on the original PR before Squash merge.

## PR workflow

### Follow through on review

Opening a PR starts the review cycle. The author is responsible for following up on comments, checks and conflicts until the change is ready or a clear blocker is reported. This applies to code, templates, media and Skills, including PRs created by an Agent.

1. Read every unresolved review thread and the latest CI results. Verify each claim against the current code or contribution before changing it; automated feedback can be wrong.
2. Fix confirmed issues, run the applicable checks, and push follow-up commits. Reply on each thread with the fix, commit and validation. If you disagree, explain the evidence and proposed outcome instead of ignoring the comment.
3. Resolve addressed threads when your permissions allow. A resolved thread must have a verified outcome; do not mark unanswered feedback resolved just to clear a merge warning. If you cannot resolve it or a disagreement remains, explain what still needs the reviewer.
4. Fix failing required checks and merge conflicts. After a fix push, re-request review from reviewers who already reviewed the PR and have not reviewed the new commit, when your permissions allow; otherwise report that re-review is pending. A reply alone does not re-request review.
5. Before reporting review follow-up complete, refresh the PR state and report remaining threads, CI, conflicts or pending re-review. Green CI alone does not mean the review is complete or authorize merging or publishing.

Agents follow the same process through [Repository PR review follow-up](AGENTS.md#repository-pr-review-follow-up). Authors can use any suitable PR interface; installing a particular Skill is not required.

### Automatic follow-up with an Agent

Ask your Agent to keep the review loop active while waiting for CI or comments. Claude Code can use `Monitor` when that tool is available in the session; other clients can use their monitor/wait tools or a lightweight session wait. The [Agent waiting guidance](AGENTS.md#automatic-waiting-during-pr-follow-up) covers state changes, CI aggregation and session lifetime.

```text
Keep following PR_URL through CI and review in this session. Use an available
monitor/wait tool, or wait for PR state changes in-session. Verify new feedback,
fix confirmed issues and required CI/conflicts, push validated changes, reply and
resolve addressed threads, and re-request prior reviewers when permitted.
Continue until the review follow-up is ready or a concrete blocker needs me.
Report the latest state. Do not merge or publish.
```

Replace `PR_URL` with your PR link. A promise to keep watching is not a running monitor: ask the Agent to identify the active mechanism and its lifetime. Closing a session stops session-only waiting; unattended tracking needs a separately configured durable runner.

### Submit a video with your Agent

Share your video, reference or editable project with your Agent and paste this brief:

```text
Create a reusable OpenMotion template from the video or project I provide.
Read https://github.com/nexu-io/openmotion/blob/main/CONTRIBUTING.md and the linked
template catalog contribution guide. Use the OpenMotion video-to-template workflow
for a reference video; preserve editable source for an existing project.
Include a preview, replaceable content, TEMPLATE.md, motion guidance, source
attribution and asset licenses. Register catalog entries and locale metadata only
as described in the catalog guide. Run the applicable template and storage checks.
Prepare a focused pull request against nexu-io/openmotion with an English title
and description, and show me the template and validation results for review.
Do not merge or publish packages or CMS content.
```

Studio's **Submit video** link opens this guide. **Recreate and submit** copies a
brief that also identifies the selected template; **Recreate template** copies only
the recreation brief. Paste either into your Agent to continue. These controls do
not upload media or create a pull request by themselves.

### Submit a Brand Kit

Studio's **Submit Brand Kit** link opens this contribution guide. Start with a
public website or a local Brand Kit Motion Package. Include the original source,
permission and license notes, reusable design tokens and brand assets, and a
preview of the fixed showcase. Mark the package `brand-kit` and `style-only`:
its colors, typography and visual rules can be reused, while the showcase's story
and timing are not template guidance. See [Brand Kits](docs/brand-kits.md).

Ask your Agent to prepare a focused pull request with the source references,
package validation and preview evidence. Keep private context files and rules out
of the contribution. The link does not upload a kit, submit a pull request or
publish it to the official collection. Catalogue inclusion requires review and
an explicit update to the maintained catalogue.

### Submit a skill with your Agent

Have a local folder with a `SKILL.md`, or a public repository with one? Share it with your Agent and paste this brief:

```text
Contribute the Agent skill I provide (a local SKILL.md folder or a public GitHub
repository) to OpenMotion. Read https://github.com/nexu-io/openmotion/blob/main/CONTRIBUTING.md
and library/ENTRY_TEMPLATE.md first. Confirm that I wrote the skill or that its
license allows redistribution; record the author, original URL or version and the
licenses of its code and media, and stop to ask me if any of this is unclear.
Fork nexu-io/openmotion and branch from the latest main. Put the skill at
library/skills/<name>/SKILL.md with name and description frontmatter, a clear
trigger, steps and a real usage example; keep its references and scripts in the
same folder and add a README.md from the entry checklist. Link the entry from the
Skills row of library/README.md. Do not change skills/, Studio, the MCP registry or
the distribution file list. Open a draft pull request against nexu-io/openmotion
with an English title and description that state the source and license, then send
me the link. Do not merge or publish anything.
```

Studio's **Submit a skill** button on the Skills page opens this section. It does not
upload files or create a pull request by itself.

Work from the repository root; read [AGENTS.md](AGENTS.md) and the [architecture](docs/product/architecture.md). Use the pinned CI Node version. Keep `package-lock.json` and `scripts/runtime-lock.json` in sync with any intentional dependency change.

Before opening a PR, follow the [local validation guidance](AGENTS.md#local-validation) and report the checks you actually ran. Studio unit tests use `npm run test:studio`. Model creation and visual acceptance require separate evidence. Do not overwrite real user data or host configuration to test an installer.

Keep PRs focused and describe the user-visible behavior and actual validation. Discuss substantial changes in an existing issue, requirement or PR description; a separate issue is not required when the work is already defined. Review the entire product architecture for each change and update it only when needed, following the [shared guidance](AGENTS.md#product-architecture-review); documentation edits are not required in every PR. Preserve existing Git history and push follow-up commits during review; do not force-push a shared branch.

For an agent contribution: read the entry and sources, make the requested change, update the affected guide and [change record](docs/product/changes.md), run the applicable checks, and report the exact result and remaining gaps. Do not treat successful installation, technical rendering and human content acceptance as interchangeable.

Use the PR Actions summary to review new duplicate fragments and unused code or dependencies. The report is advisory. When a confirmed issue needs a separate change, link its source PR from a GitHub issue labeled `maintainability`, describe the impact, and assign an owner. Review open follow-ups in the existing engineering review. Promote repeat findings to a required check only after the rule is explicit and historical PRs show that the check detects it reliably.

Only deliberately public documentation belongs here. Do not commit credentials, internal links, private plans, workstation paths or user projects. Distribution uses the positive list in `scripts/distribution.ts`; newly shipped files require an explicit decision. Preserve all upstream attribution and license notices. Do not add telemetry or publish a package without a separate decision.

Contributions are licensed under the repository's [Apache-2.0 license](LICENSE); vendored components retain their own terms. This migration branch is for review only and must not be merged or published automatically.

## Repository media and size

For template projects, commit the editable files under the catalog entry's `source/` directory and refresh the source manifest and project-file hashes. You do not need to upload project files or ZIPs to `r.open-design.ai`, obtain CMS credentials or supply new public download URLs. Local Studio/MCP read the registered checkout files; hosted NPM consumers receive them through automatic main-branch synchronization after merge. See [contributing editable project files](docs/template-repository.md#contribute-editable-project-files). Website CMS publication is a separate internal task.

Keep embedded README previews directly readable. Large existing previews use public R2 URLs registered in `repository-media.json`; small artwork, template source and browser dependencies stay local. The ordinary Git checkout has a 128 MiB advisory target; exceeding the total reports a warning without blocking contributions or media cleanup. Full videos and optional template archives use Git LFS with downloads excluded by default. Follow [storage, scoped downloads and contribution checks](docs/repository-storage.md); run `npm run storage:check` after staging. For contributed media, use the documented **Prepare and merge PR** Action after final review; contributors do not need upload credentials.
