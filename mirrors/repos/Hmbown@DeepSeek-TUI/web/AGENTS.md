# web — agent guidance

The codewhale.net site (Next.js). Read the repo-root `AGENTS.md` first.

- **Facts derive from the repo.** `npm run prebuild` regenerates
  `lib/facts.generated.ts` (version, crate/provider/tool counts, license)
  and `npm run check:facts` fails if the committed copy drifts. Never
  hand-edit the generated file; change the source of truth in the repo and
  regenerate.
- **Gates** (all must pass; CI runs them):

  ```sh
  npm ci && npm run prebuild && npm run check:facts && npm run check:docs \
    && npm test && npm run lint && npm run build
  ```

- `check:docs` verifies doc topics against real repo files, the version
  stamp, and install snippets — stale docs fail here, not in production.
- `AGENT.md` (singular, next to this file) documents the community
  assistant (Cloudflare cron drafting triage/review/digest drafts into
  Workers KV, never posting directly). It is maintainer-owned automation;
  don't extend it without Hunter.
