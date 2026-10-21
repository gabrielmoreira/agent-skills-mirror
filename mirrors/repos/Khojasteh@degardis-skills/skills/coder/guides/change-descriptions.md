---
title: Commit messages and change request descriptions
applicability:
- When a commit message, or a change request's title or description, is among what the work produces or assesses
x-claim-provenance:
- claim: Git treats the text up to the first blank line of a commit message as its title and uses it throughout Git, and recommends a title of no more than 50 characters followed by a blank line and a more thorough description.
  source: https://git-scm.com/docs/git-commit
  scope: retrieved 2026-10-20
- claim: A commit message body explains the problem the change solves, justifies its approach, and notes alternatives considered and discarded; it should be understandable without external resources, summarizing a discussion rather than linking it, and cites another commit by abbreviated hash and subject.
  source: https://git-scm.com/docs/SubmittingPatches
  scope: retrieved 2026-10-20
- claim: A revised patch series presents a logical progression without the author's earlier mistakes.
  source: https://git-scm.com/docs/SubmittingPatches
  scope: retrieved 2026-10-20
- claim: Comments relevant only to the moment or the maintainer, such as what changed between versions of a patch, are not suitable for the permanent changelog and are kept out of the committed message; performance and size claims are backed by numbers.
  source: https://docs.kernel.org/process/submitting-patches.html
  scope: retrieved 2026-10-20
- claim: A sign-off's meaning depends on the project; under the Developer Certificate of Origin it certifies the signer's right to submit the work, Reviewed-by can be offered only by the reviewer, and Tested-by states that the named person tested the change.
  source: https://git-scm.com/docs/SubmittingPatches
  scope: retrieved 2026-10-20
- claim: A change description is a permanent public record of what changed and why, and since a change can alter significantly during review, its description is checked against what it does before it is submitted.
  source: https://google.github.io/eng-practices/review/developer/cl-descriptions.html
  scope: retrieved 2026-10-20
- claim: A pull request's title and description explain why the change is needed, what changed, and where reviewers should pay special attention, and link the issues it relates to.
  source: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/getting-started/helping-others-review-your-changes
  scope: retrieved 2026-10-20
- claim: A pull request template's contents populate the body of a new pull request.
  source: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
  scope: retrieved 2026-10-20
- claim: Squash merging can be configured to use the pull request's title and description as the merged commit's message.
  source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests
  scope: retrieved 2026-10-20
- claim: A closing keyword before an issue reference in a pull request description or commit message closes the issue when the change is merged into the default branch.
  source: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
  scope: GitHub, retrieved 2026-10-20
- claim: Text matching the closing pattern in a commit message or merge request description closes the referenced issues when the commit or merge request reaches the default branch.
  source: https://docs.gitlab.com/user/project/issues/managing_issues/
  scope: GitLab, retrieved 2026-10-20
- claim: Mentioning a person or team triggers a notification to them.
  source: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax
  scope: GitHub, retrieved 2026-10-20
- claim: Strings such as [skip ci] in the commit message of a push or of a pull request's head commit skip the workflows those events would trigger.
  source: https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/skipping-workflow-runs
  scope: GitHub Actions, retrieved 2026-10-20
- claim: "[ci skip] or [skip ci], in any capitalization, in a commit message skips the pipeline."
  source: https://docs.gitlab.com/ci/pipelines/
  scope: GitLab CI/CD, retrieved 2026-10-20
---

A commit message is read from the history long after the work, in a log, a blame, a bisect, a patch, or a release tool, by someone who holds the code before and after the commit and wants to know what it does and why. A change request's title and description are read first by reviewers deciding whether to accept the change and where to look, then by anyone tracing the change through the service hosting the repository. Neither reader holds the work that produced the change, and neither record is the report to the requester, which accounts for that work.

Each record carries the change's history, from the state before it to the state after it, not the work's. What the work did to reach the change, such as its searches, attempts, order of edits, mistakes made and corrected along the way, the instructions it received, and the conversation, describes states the reader never sees: for example, *fix the check added in the previous attempt* names an attempt that is in no history, and *as requested* names a request nobody reading the history saw. Test each statement against the code before and after the change, and keep it only when it is true of them and changes what the reader understands or does. What the work established about the change can pass it: the evidence verifying the change as it now stands, which a change request reports to its reviewers; a measurement behind a claim the record makes, such as the timings behind *halves startup time*; and an alternative a later maintainer would otherwise try, with what rules it out. Either record gives such evidence as its decisive result, never as the output that buries it.

The subject identifies the commit wherever only one line shows, so it summarizes what the change does to the code. The body says what the subject cannot: the problem or need, stated as what the code does without the change; why this approach answers it; and the consequences the diff does not show, such as a changed behavior, a compatibility break, a required migration, or a case deliberately left out and why. It does not restate the diff, which already shows the files and lines changed, and an explanation a reader of the code needs belongs in the code or its documentation, where that reader looks, rather than only in the message. A change whose subject says everything needs no body. The message stands without the hosting service and without links, which may not resolve where the history is read: summarize the discussion or issue that decided the change, and cite another commit by its hash and subject. A commit that only corrects an earlier, not yet shared commit of the same change has no change of its own to describe: fold it into the commit it corrects where the project's conventions and the work's authority over that history allow, and otherwise describe what it changes in the code's terms.

A change request's title identifies it in lists as a commit subject does, and its description gives a reviewer what judging the change needs: what it does and why, with any issue it resolves; how it was verified, naming the checks run, what they covered, and what was not verified; the risks, compatibility effects, and migration or rollout steps it brings; where review should start, or which decision a reviewer is asked to make; and what is deliberately left for later, where a reviewer would otherwise take it as covered. A project's change request template states what its reviewers expect: fill each section from the change, remove or mark a section as the template directs, and leave unticked any checklist item the work did not do. Keep the title and description true of the change as it now stands: when review or later commits change it, revise them, and put what changed since the last review in the review conversation, where the reviewers following the change read it.

Material that serves only review, such as where to start reading, how to try the change, screenshots, or answers to reviewers, belongs in the change request rather than in commits, since it means nothing once the change is accepted. The reason for a change belongs in its commits even when the change request also gives it, since the history travels without the hosting service. Where the project's merge method makes the change request's title and description the merged commit's message, as its merged history shows, they are held to the commit message's standard as well, and review-only material goes in a comment.

Every statement in these records is a claim reviewers and maintainers will act on, so each states only what the evidence established: *fixes*, *no behavior change*, and *tested* each need that evidence, as do qualities such as *robust* or *complete*. A message or description that misstates what its change does, or claims verification the evidence does not show, is a defect of the change.

The project's contributing instructions and templates, then its recent history, decide the subject's prefix, mood, length, and capitalization, how issues are referenced, and which trailers appear. Where neither shows a form, write a summary line, a blank line, then the body: Git's own tools take the text before the first blank line as the title and recommend at most fifty characters for it. A trailer such as a sign-off, a review or test credit, or a co-author line asserts something about the person it names: a sign-off commonly certifies that person's right to submit the change under the project's terms, and a review or test credit says that person reviewed or tested it. Add one only where the project's conventions or standing instructions call for it and what it asserts holds: never a sign-off its named person has not given or authorized, nor a credit for a review or test that did not happen.

Some text is acted on rather than read: a closing keyword before an issue reference in a message or description can close that issue once the change reaches the default branch, a mention notifies each person or team it names, and a token such as `[skip ci]` in a commit message can skip the project's checks, so the change reads as verified when nothing ran. Include such text only where the request or the project's conventions call for that effect on that target, and a skip token only when the requester asks for it.

A commit message is copied into every clone and cannot be withdrawn from them, and a change request is visible to everyone who can see the repository, so apply [[principle:sensitive-material]] to every name, address, value, and detail in either before it is recorded or pushed. Where the requester supplies the wording, use it as given, and where it conflicts with a project requirement, such as a required trailer or subject form, say so rather than change it.
