# Privacy Policy

Last updated: October 11, 2026

This policy applies to the Agentic Awesome Skills (AAS) open-source repository, its packaged skills and plugins, and the companion catalog at <https://aaskills.tech/>.

## AAS plugins

AAS skills-only plugins are local instruction bundles. They do not create an AAS account, run an AAS-hosted service, collect telemetry, or independently receive, store, or transmit conversation content, files, credentials, or tool results.

The agent client that installs a plugin processes prompts, files, and generated output under that client's own privacy terms and settings. Some bundled skills explain how to use third-party tools or services. Those services receive data only when the user or agent client separately enables and invokes them, and their own privacy terms apply. AAS does not receive that third-party traffic.

Do not place secrets or personal data in prompts, examples, issue reports, or public discussions unless the chosen client and destination are appropriate for that information.

## Hosted catalog

The hosted catalog is a static application hosted on Vercel. It:

- loads public catalog data and public, aggregate skill-save counts;
- stores saved-skill choices, shortlists, and named collections (including optional notes) in that browser's local storage;
- imports collection files into browser memory for an explicit review before saving; exports contain the names, notes, version labels, and IDs chosen by the user;
- creates shareable links containing exact skill IDs and the catalog version in a URL fragment; anyone receiving a link can inspect it, so it should not be treated as private;
- keeps Workbench imports in browser memory and does not upload them to AAS;
- uses Vercel Web Analytics for aggregate visit statistics, with query strings and URL fragments removed by AAS before analytics events are sent;
- does not send Workbench imports, shortlist contents, or agent briefs as analytics events;
- does not use an AAS account system or advertising tracker.

Vercel, GitHub (including the legacy redirect site), Supabase, the user's browser, and network providers may process routine connection metadata under their own policies. AAS does not sell personal information.

Vercel describes Web Analytics as cookie-free aggregate measurement; see its [analytics privacy documentation](https://vercel.com/docs/analytics/privacy-policy) for data handling and retention. Search text still forms part of the navigation URL and browser history, so do not enter secrets or personal data into catalog searches.

## Retention and control

AAS does not maintain a user profile or a server-side store of plugin conversations. Collections have no automatic cross-device sync. Export a backup before clearing site data; browser-local saved skills and collections can be removed by clearing site data. Content voluntarily posted to GitHub is retained and controlled under GitHub's features and policies.

## Contact

For ordinary privacy questions, use the project's [Q&A support channel](https://github.com/sickn33/agentic-awesome-skills/discussions/new?category=q-a). Do not post sensitive information publicly. For a sensitive report, use [GitHub's private security reporting flow](https://github.com/sickn33/agentic-awesome-skills/security/advisories/new).

Material changes to this policy will be recorded in the repository history and reflected by the date above.
