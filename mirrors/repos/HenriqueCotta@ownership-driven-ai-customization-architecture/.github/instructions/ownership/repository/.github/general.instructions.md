---
applyTo: ".github/**"
---

# GitHub Configuration Ownership

Use this as the fallback owner for `.github/` surfaces that do not already have a narrower owner or overlay.

Keep the live Copilot customization aligned with the public architecture this repository teaches.

Owner instructions belong under the literal root node `.github/instructions/ownership/repository/`.

When a change under `.github/**` reveals a stable sub-area with its own behavior, create a child owner instead of expanding this fallback.

## Follow-Through Triggers

If a change under `.github/instructions/**` alters the customization shape, update the guidance and validation that depend on that structure.
