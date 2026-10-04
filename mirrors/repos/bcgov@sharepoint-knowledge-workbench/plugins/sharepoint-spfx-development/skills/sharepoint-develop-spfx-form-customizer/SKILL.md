---
name: sharepoint-develop-spfx-form-customizer
plugin: sharepoint-spfx-development
description: Scaffolds, implements, tests, packages, deploys, associates, validates and rolls back an SPFx Form Customizer extension for SharePoint Online list New, Edit and Display forms. Use when a list needs a customized item form, especially one driven by URL parameters such as a parent SelectedID.
allowed-tools: Bash, Read, Write
---

# Scaffold SPFx Form Customizer

Guide the full lifecycle of an SPFx Form Customizer, from suitability check to rollback.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Hard gate: deployed is not done.** A successful `.sppkg` build, or a user confirming the app was uploaded, does not mean the custom form is active. SharePoint silently keeps serving the default form until the component GUID is
  associated with the list's content type. After confirming deployment, immediately prompt for the association step (step 9). Treat "deployed" and "associated" as two separate required checkpoints and say which is outstanding at
  every status update. Never report the workflow complete after deploy alone.
- Check suitability first: a Form Customizer attaches to a content type. For a dashboard use a web part; for command buttons use a ListView Command Set; for styling use JSON form formatting.
- Treat URL parameters as untrusted (positive-integer `SelectedID`, sanitized `Source`), and send lookups the integer `Id` (`<Field>Id`), never display text.
- `associate-form-customizer.ps1` and `remove-form-customizer-association.ps1` are dry runs unless `-Execute` is passed; `deploy-spfx-package.ps1` has no gate. Work on a non-production site.

## Quick start

```powershell
pwsh -File scripts/check-spfx-toolchain.ps1
```

## Workflow

1. Confirm the toolchain, then gather requirements (name, list, content type, form modes, URL parameters, parent list and lookup field, validation, return navigation). Do not guess.
2. Scaffold with `yo @microsoft/sharepoint` (Extension, Form Customizer, React), then implement the lifecycle host, URL-driven logic, accessible UI and safe redirect handling.
3. Build, package (`sharepoint-package-spfx-solution`) and deploy (`sharepoint-deploy-spfx-solution`).
4. Associate: `pwsh -File scripts/associate-form-customizer.ps1 -ListName ... -ContentTypeName ... -ComponentId <manifest id>` (dry run), then again with `-Execute`.
5. Validate with `scripts/validate-form-customizer-association.ps1` and the browser checklist. Roll back with `scripts/remove-form-customizer-association.ps1 -Execute` if needed.

## Verification

The validation script reports the content type's component ID matching the manifest `id`, and the browser checklist passes: the custom form loads with parent details, saves with the lookup ID populated, loads existing values on edit, and Cancel
closes without saving.

## References

- [Suitability and setup](references/form-customizer-suitability-and-setup.md): read first, for the decision matrix, prerequisites, requirements to gather and the Yeoman prompts.
- [Implementation patterns](references/form-customizer-implementation-patterns.md): read when writing code, for the structure, lifecycle host, URL-driven pattern, accessibility and redirect handling.
- [Deploy, associate, validate, roll back](references/form-customizer-deploy-associate-validate.md): read for steps 8 to 11 and the flow diagram.
- [Lifecycle](references/form-customizer-lifecycle.md), [content type association](references/content-type-association.md), [URL-driven related-item pattern](references/url-driven-related-item-pattern.md),
  [validation checklist](references/validation-checklist.md) and [acceptance criteria](references/acceptance-criteria.md): read for the detailed lifecycle APIs, association mechanics, state handling, test matrix and expected behavior.
