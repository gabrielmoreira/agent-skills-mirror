# Full report (`/insta-audit @handle [period] [competitors]`)

A complete, evidence-backed HTML report on any Instagram account and its competitors. Write it in the creator's language. Default to the last 90 days, up to 100 target posts and 5 relevant competitors (up to 30 recent posts each). These are collection limits, not promises of API coverage.

## Resolve the account and scope

Use the supplied handle. Otherwise inspect Treg's connected Instagram identity; if exactly one account is clearly the user's, use it and name it. If absent or ambiguous, ask for the handle. Never infer account ownership from a public search result. Infer niche, language and target audience from the bio and recent posts; label those inferences. Respect supplied competitors and budget.

Save each run under `video-agent/audits/<handle>/<YYYY-MM-DD-HHmm>/` without overwriting earlier runs: `index.html`, `data.json`, and `sources/` for sanitized API evidence. Use the user's local timezone and include UTC retrieval timestamps. Read [workflow.md](workflow.md) for the collection contract, formulas and HTML requirements.

## Collect through Treg

Use the installed Treg CLI or authenticated Treg MCP. Discover endpoints and read their live parameter and pricing contracts before calling; never invent an endpoint, cursor, response field or permission. Start with catalog discovery and connected tools, not scraped credentials. CLI discovery:

```sh
treg tool ls
treg catalog search "instagram"
treg catalog get instagram.instagram.user.profile
treg catalog get instagram.instagram.user.posts
treg catalog get instagram.instagram.account.insights
treg catalog get instagram.instagram.media.insights
treg catalog get treg.instagram.user.profile
treg catalog get treg.instagram.user.posts
treg catalog get exa.creators.search
```

Use official connected-account endpoints for the user's own insights when accessible, public endpoints for competitors. They have different access boundaries. If MCP authentication fails and an authenticated CLI exists, use it. Do not install, log in or switch organizations silently.

Read prices and balance, announce the expected cost and collection scope before spending. Keep a per-call ledger and a conservative default total ceiling of US$1 unless the user specifies another budget. Account for per-result pricing, pagination, overflow and retries; stop before the next call could exceed the ceiling. Routed calls support `X-Treg-Route-Max-Cost`; cap them within the remaining budget and disable automatic waterfall when appropriate. Do not treat that header as a universal spending cap for non-routed providers. Missing pricing means do not call that route.

Paginate only using the selected provider's documented contract. Stop at the date boundary, item limit, repeated cursor, no new IDs or budget limit. Keep a partial report on access errors or exhausted coverage. Never label a partial sample a complete account history.

## Find competitors and outliers

Discover candidates by niche, language and audience using Treg creator search; validate each candidate against its actual profile and recent posts. Select direct peers separately from larger aspirational accounts. Search ranking alone does not establish competition. Use each account's own format-specific baseline to identify outliers; never pool all accounts into one median.

Inspect the strongest examples: hook, topic, format, duration if available, caption, CTA and observable presentation. Only describe audiovisual features after actually inspecting media or a transcript; a caption is not a spoken hook. Mark explanations as hypotheses, not proven causes of virality. Translate findings into specific, original content experiments for the audited account.

## Deliver and verify

Create the report using the requirements in the reference. No public hosting, posting, DMs or account mutations are part of an audit. Open the local HTML with an available file preview. Inspect at desktop and mobile widths if a permitted browser is available; otherwise state that visual rendering was not verified. Check reported calculations against `data.json`, source links, missing-data labels and HTML escaping. Return the HTML link, strongest findings, coverage limitations and recorded API cost. Never claim live data collection or visual validation that did not happen.
