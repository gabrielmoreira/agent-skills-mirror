# PR Descriptions as Review Navigation

A PR description's job is not narrating what you did — it's *optimising someone else's next 20 minutes*. The reader is a busy peer deciding: what is this, where do I look hardest, what can I trust, how do I verify it?

## The four questions the description must answer

1. **What & why in two sentences** — the change and the reason it exists (link the issue, but never ONLY link: "see ticket" outsources your job to a tab-switch).
2. **Where to look hardest** — the honest heat map: "the tricky part is the cursor logic in `pagination.ts`; the rest is mechanical renames." This single section halves review time and doubles review quality — reviewers spend attention where the author knows the risk lives.
3. **What I already verified** — tests added/run, manual checks performed, edge cases exercised. Specific ("tested with 0, 1, and 10k-row workspaces; verified the migration on a prod snapshot") not ceremonial ("tested locally ✅").
4. **What I'm NOT confident about** — the professional-courage section: "I'm unsure whether the retry belongs here or in the caller — opinions welcome." Naming your doubt gets it reviewed; hiding it gets it shipped.

## Calibrations

- **Description length ∝ diff surprise, not diff size.** A 500-line generated migration needs three lines; a 20-line concurrency change needs a paragraph and a diagram.
- **Screenshots/recordings for anything visual** — before/after beats prose; reviewers shouldn't check out the branch to see a button moved.
- **Breaking changes & rollout notes are description material**, not commit-message trivia: flags, migration order, revert procedure.
- **If the PR does two things, the description can't fix it** — split the PR. A description that needs the word "also" twice is a code smell upstream of the writing.

## Anti-patterns

The novel (500 words for a rename) · the void ("fixes bug") · the mystery tour (perfect summary, zero guidance on where danger lives) · the false confidence (no doubts section on a change the author privately fears — reviewers can review code, not withheld anxiety).
