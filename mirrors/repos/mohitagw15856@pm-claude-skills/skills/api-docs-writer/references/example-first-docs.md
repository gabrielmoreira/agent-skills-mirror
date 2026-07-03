# Example-First API Docs: the Rules That Make Docs Usable

Developers don't read API docs — they hunt for a working example, paste it, and diff reality against expectation. Documentation quality is therefore example quality; everything else is furniture. (And in 2026, half your readers are agents who will execute your examples *verbatim* — a broken sample is now a broken integration.)

## The example contract

- **Every endpoint: one complete, runnable request AND its real response.** Complete means auth included, placeholder values obviously placeholder (`sk_test_…`, `{{USER_ID}}`), and copy-paste-runnable against a sandbox.
- **Responses are real captures, not hand-typed** — hand-typed responses drift from production within two releases; generate them from actual calls in CI if possible.
- **Show the failure, not just the success.** The 401, the 422 with its body, the rate-limit response — developers integrate error handling by example too, and it's the half you didn't document that pages them at 2am.

## The reference-entry anatomy (per endpoint, in this order)

1. One sentence: what it does and the main WHEN you'd call it
2. The runnable example (request + response)
3. Parameters table — with types, required-ness, defaults, and *constraints in prose* ("ISO-8601, must be future-dated")
4. Errors table — code, meaning, and what the developer should DO about each
5. Gotchas ("idempotent only with the header", "paginates at 100, see cursors")

## The two-audience structure

Guides (task-shaped: "accept your first payment") and Reference (endpoint-shaped) are different documents with different readers at different moments. Guides link into reference; reference never tries to be a guide. The most common docs failure is one document trying to be both and being neither.

## Freshness mechanics

Docs rot silently. The countermeasures that actually work: examples executed in CI against the sandbox (broken example = failing build) · error strings in docs grep-matched against the codebase's actual strings (that's how developers search — by pasting the error) · a changelog section per endpoint for breaking changes, dated.
