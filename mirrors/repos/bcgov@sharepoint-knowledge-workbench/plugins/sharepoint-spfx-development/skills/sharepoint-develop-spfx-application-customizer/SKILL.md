---
name: sharepoint-develop-spfx-application-customizer
plugin: sharepoint-spfx-development
description: Scaffolds, implements, packages, deploys, registers, validates and removes an SPFx Application Customizer that injects UI into the Top or Bottom placeholder of every modern page, such as a site-wide mega-menu, header, banner or footer. Use for site-wide page chrome; not for web parts, list command bars or item forms.
allowed-tools: Bash, Read, Write
---

# SPFx Application Customizer

Site-wide UI rendered into a page placeholder (`Top` or `Bottom`) on every modern page, for example a navigation mega-menu driven by the site's Quick Launch. It is not a web part (page canvas), a ListView Command Set (list command bar) or a Form Customizer (item forms).

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Scaffold with the official generator (`yo @microsoft/sharepoint`, Extension, Application Customizer); do not copy another extension and rename it.
- Package deployment does not run the extension unless it is activated. With `skipFeatureDeployment` the extension must be registered as a custom action, as a separate step.
- `scripts/register-application-customizer.ps1` is dry-run by default; a live write needs `-Execute -ConfirmToken REGISTER-SPO-APPCUSTOMIZER`. Use a non-production site first and let the user run it, because it opens a sign-in popup.
- Application Customizers run on every page: guard against the placeholder being absent, clean up in `onDispose`, handle SPA navigation (`navigatedEvent`), and never throw during `onInit`.
- Treat menu titles and URLs from the site as untrusted: set text with `textContent`, validate URL schemes (`http`, `https`, relative), and never build markup from them.
- Persisting is not proven by a success message: the script re-queries the custom action; also confirm in the browser after a hard refresh.

## Quick start

```powershell
pwsh -File scripts/register-application-customizer.ps1 -Name "<StableName>" -Title "<Label>" -ComponentId "<manifest-guid>" -ConfigPath "<config.psd1>"
```

Add `-Execute -ConfirmToken REGISTER-SPO-APPCUSTOMIZER` to write; add `-Remove` to roll back.

## Workflow

1. Confirm a non-production target and collect the placeholder, the data source and whether the native navigation is hidden. Run `scripts/check-spfx-toolchain.ps1`.
2. Scaffold, implement and unit-test the component. Debug with the `?debugManifestsFile=...&loadSPFX=true&customActions=...` query string (see the workflow reference).
3. Build and package with `sharepoint-package-spfx-solution`, then deploy and add the app with `sharepoint-deploy-spfx-solution`.
4. Register with the script (preview first), then re-query to confirm.
5. Hard-refresh, verify on several pages and at narrow widths, then roll back with `-Remove` if needed; this does not touch the package.

## Verification

The UI appears once per page (including after in-app navigation), keyboard and screen-reader behaviour works, no console errors, and exactly one matching custom action exists with the expected component id.

## References

- [Workflow and rules](references/application-customizer-workflow.md): read for scaffolding, debugging, placeholders and registration.
- [Navigation menu pattern](references/navigation-menu-pattern.md): read when building a mega-menu from Quick Launch, including B.C. Government design alignment (tokens, BC Sans, React component compatibility). For B.C. sites also use the `bc-gov-design-system` and `bc-gov-react` skills if installed.
- [Validation checklist](references/validation-checklist.md) and [acceptance criteria](references/acceptance-criteria.md): read when verifying.
