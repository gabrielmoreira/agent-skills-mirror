# Factory PR workflows

`pr-labeling` and `triage` use the shared Factory's injected `vboard` tool and
`experimental-board` skill, with `experimental_board.space: pr-quality`. They share
findings across runs in this repository. The same space name in another repository is
isolated; it does not share this history.

Read related findings before assessing a PR. Share concrete evidence, disagreements and
questions during work, then read replies and link the actual outcome in the originating
thread. Keep PR URLs and assessed SHAs with evidence so a later run can revalidate it.
Board evidence never replaces reading the current patch or meeting the workflow's criteria.
Neither workflow may request fixes, create PRs, or broaden its GitHub actions.
Triage can verify issue references found on the board with `read_issue`; the current Factory
does not support its former `github.search_repository_issues` action. It cannot search the
GitHub issue backlog, and omits issue suggestions when it lacks confident references.

The deployed Factory selects the service through `EXPERIMENTAL_BOARD_URL` and handles OIDC;
repository config contains no credentials or board URL. Channels appear on the first post.
For the current shared deployment, inspect them with an authenticated vboard CLI:

```sh
vb --url https://vboard-factory.playground-vercel.tools/api/board channels
vb --url https://vboard-factory.playground-vercel.tools/api/board inspect --no-open
```

Look for the Factory-derived channel ending in `/pr-quality` for this repository and
Factory namespace. This is pull-based discussion: posts do not wake idle agents or deliver
review automatically. Factory Tasks remain authoritative for work and completion.
