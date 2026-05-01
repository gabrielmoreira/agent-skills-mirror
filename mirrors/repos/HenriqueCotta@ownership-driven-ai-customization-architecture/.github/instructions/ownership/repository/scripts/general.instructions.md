---
applyTo: "scripts/**"
---

# Scripts Ownership

Scripts are maintenance surfaces that should encode the current repository contract, not stale historical assumptions.

Validation should fail on real drift that maintainers can act on.

Keep script logic aligned with the repository contract it protects.

Do not encode historical structure just because it used to be true.

## Follow-Through Triggers

If a change under `scripts/**` alters what the repo considers valid, update the automation and guidance that depend on that validation contract.
