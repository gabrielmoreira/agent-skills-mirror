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
- **Shared public copy lives in `web/lib/content/`.** Locale-aware
  `{ en, zh }` modules (product vocabulary, the getting-started path) are the
  single source for the nouns and the new-user path; pages render from them.
  Keep definitions verbatim with `docs/public-surface-facts.json` /
  `docs/MODES.md` — `web/lib/content/vocabulary.test.ts` pins this. New
  locales extend the pairs, not the pages.
- **Real-session media goes through `web/lib/media-manifest.ts`.** A
  `pending` entry renders the visible "recording pending release candidate"
  state via `components/session-media.tsx`; never commit placeholder or staged
  footage. Flipping to `published` requires the full asset set, the enforceable
  file/byte/poster checks in `media-manifest.test.ts`, and the physical-media
  checks in `docs/releases/v0.9.2-media-plan.md`.
- `AGENT.md` (singular, next to this file) documents the community
  assistant (Cloudflare cron drafting triage/review/digest drafts into
  Workers KV, never posting directly). It is maintainer-owned automation;
  don't extend it without Hunter.
