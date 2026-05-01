---
applyTo: "docs/**"
---

# Documentation Ownership

The docs tree is the canonical public explanation of the architecture.

Keep overview material separated from focused guidance and examples.

Prefer selective examples over exhaustive trees that no real repository would maintain.

Keep overview pages short and route detail into focused pages instead of repeating it.

Every docs page must include a local table of contents near the top so readers can see what the page answers and jump directly to the relevant section. Use `## On This Page` in English docs and `## Nesta Página` in Portuguese docs. Keep those links synchronized when headings change.

## Follow-Through Triggers

If a change under `docs/**` alters documentation structure, update the mirrored content and any dependent routing or validation.

If a change under `docs/**` alters a public architectural claim, update the copyable artifacts and live customization that teach or enforce the same claim.
