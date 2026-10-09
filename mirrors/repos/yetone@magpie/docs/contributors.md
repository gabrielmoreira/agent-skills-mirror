# Community PRs: what is closed unreviewed, and who is blocked

magpie merges community PRs through agents. Two things keep that from
wearing the project down: a PR that could harm users is caught before any
review of what it does, and an author who keeps sending work that costs
more to review than it gives is stopped.

## Look for harm first

Before running a PR, read its diff for anything that reaches past its stated
goal. Any one of these stops the review until the maintainer has looked:

- It changes `.github/` (workflows, actions, permissions, secrets), a release
  or publish script, the Dockerfile, or `site/`.
- It adds a network address, an upload, telemetry, or sends a credential,
  token, cookie or file anywhere it didn't go before.
- It reads or writes a credential file, keychain entry or agent config the
  goal doesn't need.
- It adds a dependency, a `replace` in go.mod, an npm install script, a
  binary, a minified or encoded blob, or code built from a string at run time.
- It adds a relay, reseller or affiliate address, or a vendor the maintainer
  removed (DimAgent).

Say which line stopped it in the review. Don't run the PR's code on a machine
with real accounts until the maintainer has cleared it.

## Close without a full review

Close with a short reason, without running it, a PR that:

- changes what the maintainer has ruled on (see "Don't reverse deliberate
  decisions" in [code standards](code-standards.md)), such as the Codex
  prompt files, which are kept byte for byte;
- is a resubmission of a PR closed for its idea, with nothing new to answer
  the reason it was closed;
- is one of several near-identical PRs opened seconds apart.

## Blocking an author

An author is proposed for the block list when any one of these holds:

1. They have 3 or more PRs closed by a maintainer as low-value (wrong,
   untested, unrelated, machine-made filler), and fewer than 30% of their
   PRs merged.
2. They resubmitted a PR after an explicit rejection, twice.
3. They did anything deceptive: hid a change outside the PR's stated goal,
   faked a test or a verification, or anything from "Look for harm first"
   done on purpose.
4. They open PRs in machine bursts (several within a minute) that are
   low-value as in 1.
5. They re-add a removed vendor, a relay or an advertisement after being
   told no.

An agent only proposes. It writes the evidence (PR numbers, dates, what was
wrong) to the maintainer; the maintainer decides. A blocked author's new PRs
and issues are closed with: "Thanks — this account's contributions aren't
accepted in this repository." Nothing more is argued.

An author being watched (one or two low-value PRs, no pattern yet) gets a
normal review; the reviewer notes the PR here if it is low-value too.

## Lists

Blocked: none yet.

### Reviewed with extra care

The maintainer chose not to block these authors, so their PRs are still
reviewed, but more strictly than others:

- Read every line of the diff, not only the part the description talks
  about. Compare the files it touches with its stated goal; anything outside
  the goal is a reason to close it.
- Run "Look for harm first" in full, even on a PR that looks like a typo
  fix.
- Run it yourself on current `main`; don't rely on the PR's claims or its
  CI. Never merge it in the same tick it was opened, and use
  `--match-head-commit`.
- A PR that repeats one already closed is closed with a link to the first.

| Author | Evidence |
| --- | --- |
| lunar-me | #233, #234, #235 opened within 12 seconds, all rewriting `codex_prompt.md`, which is kept byte for byte. #590 resubmitted after the rejection. #592 broke a path in AGENTS.md. #590, #592 and #593 opened within 51 seconds. The same template across many repositories. |

Watched: none yet.
