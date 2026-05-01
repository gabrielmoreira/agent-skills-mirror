---
applyTo: "**"
---

# Repository Root Ownership

This repository is both the published ODA reference and a working example of ODA.

Root-owned guidance belongs here only when it is an architecture-wide contract for the whole repository.

The live customization should model the architecture it teaches.

Keep each customization layer in its documented role instead of using one surface as a catch-all.

Do not place owner instructions directly under `.github/instructions/ownership/`, and do not replace the literal `repository/` folder with the checkout or repository name.

Prefer GitHub-native versioning through tags and releases over repo-local version files.

## Repository Hygiene

Treat drift between public guidance and repository behavior as a real defect.

When the current change moves content or changes a rule, update every dependent surface in the same change.

Prefer one coherent source of truth over repeated near-copies.

## Writing Standard

Avoid enumeration unless the set itself is the contract.

Prefer wording that names the underlying relationship or consequence, so the guidance still covers future surfaces.

Better: update every surface that teaches or validates the same rule.

Weaker: review a hand-picked list of files that might mention the rule.

Use enumeration only when each named item needs distinct handling or when the exact closed set must be visible.

## Markdown Guidance

When editing Markdown, keep sections short and purposeful.

Prefer concrete examples and decision rules over vague prose.

Keep links and local navigation accurate.

Move durable detail into focused reference pages instead of bloating overview files.

## Follow-Through Triggers

If the current change alters a repo-wide architecture rule or customization convention, update the teaching surfaces and validation that encode the same rule.

If the current change alters repository structure, update navigation and validation that assume the old structure.
