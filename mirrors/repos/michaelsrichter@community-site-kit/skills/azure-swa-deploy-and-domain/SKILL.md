---
name: azure-swa-deploy-and-domain
description: >-
  Provision, deploy and operate a static community website on Azure Static Web Apps (Free) with GitHub
  Actions, managed Functions, Application Insights, security headers, legacy redirects, smoke tests and a
  custom domain. Use when deploying the site, setting app settings or GitHub secrets, adding a custom
  domain or subdomain (Namecheap, GoDaddy, Cloudflare, Squarespace DNS), answering "what do I put in
  Azure / my DNS?", or troubleshooting a failed SWA deployment.
---

# Azure Static Web Apps: deploy and custom domain

## Before creating anything

```powershell
az account show --query "{name:name, id:id, user:user.name}" -o table
gh auth status
az staticwebapp list -o table
gh repo view <owner>/<repo> 2>$null
```

Reuse existing resources; never delete or overwrite production resources, DNS or secrets. Names:
`rg-<slug>-web`, `swa-<slug>-web`, `appi-…`, `log-…`. Region with SWA support (e.g. `eastus2`). Tags:
`project`, `owner`, `managedBy=bicep`.

## Provision (starter: `infra/main.bicep` + `infra/deploy.ps1`, idempotent)

1. `az group create` + `az deployment group create` (SWA Free, Log Analytics, Application Insights).
2. Deployment token → GitHub secret without displaying it:
   `az staticwebapp secrets list -n <swa> -g <rg> --query properties.apiKey -o tsv | gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --repo <owner>/<repo>`
3. GitHub variables: `SITE_URL` (https URL of the live site), `ALLOW_INDEXING` (`false` until launch),
   `PUBLIC_GA4_ID`, `PUBLIC_CLARITY_ID` (optional).
4. App settings (values never printed): `ALLOWED_HOSTS` (default hostname + custom domains, comma-separated),
   `APPLICATIONINSIGHTS_CONNECTION_STRING`, `GITHUB_OAUTH_CLIENT_ID`, `GITHUB_OAUTH_CLIENT_SECRET`.
5. Push to `main` → the SWA workflow builds (with `BUILD_NOW` unset in production) and deploys; PRs get
   preview environments. A scheduled workflow rebuilds nightly.

Personal-account pushes from a work machine: see the Windows notes in `modernize-community-site`.

## `staticwebapp.config.json` rules

- Max **20 KB**. Keep ~50 high-value `301` redirects here; generate the long tail as redirect pages.
- No two routes that differ only by a trailing slash (deploy validation fails).
- `globalHeaders`: CSP (built at postbuild with hashes of inline scripts; no `unsafe-inline` for scripts;
  no inline `style=""` in HTML), `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` (camera=(), microphone=(),
  geolocation=(self) only if the map uses "near me"), `frame-ancestors 'none'`.
- `mimeTypes` for `.ics`, `.mp4`, `.webmanifest`; long `cache-control: immutable` for `/_astro/*` and `/media/*`.
- `responseOverrides` 404 → `/404.html`.
- Platform: `apiRuntime: node:22` (check current SWA support).

## Smoke test after every deploy

`node scripts/smoke.mjs https://<site>` (starter) checks: homepage has the next event, community page and
feed, security headers, immutable asset caching, top legacy 301s, a long-tail redirect page, custom 404,
sitemap, robots, `llms.txt`, ICS feeds, Event JSON-LD, `/admin/` + config + bundle, `/api/auth` (302 or
503 "not configured"), telemetry accepts same-origin and rejects cross-origin. Update the expected
strings for each organization.

## Custom domain (subdomain, e.g. `events.example.org` or `sdli.example.app`)

1. In Azure (you do this):
   `az staticwebapp hostname set -n <swa> -g <rg> --hostname <sub.domain> --validation-method dns-txt-token --no-wait`
   then read the token: `az staticwebapp hostname show -n <swa> -g <rg> --hostname <sub.domain> --query validationToken -o tsv`
   (it can take a minute to appear).
2. Tell the owner the **exact** records (registrar UI wording):

   | Type | Host | Value | TTL |
   | --- | --- | --- | --- |
   | CNAME | `<sub>` | `<default-hostname>.azurestaticapps.net` | Automatic |
   | TXT | `_dnsauth.<sub>` | `<validation token>` | Automatic |

   Namecheap: Domain List → Manage → **Advanced DNS** → Add New Record. "Host" is only the part before the
   domain (`sdli`, not `sdli.example.app`). Remove any conflicting URL-redirect or parking records for that host.
   Cloudflare: proxy **off** (DNS only) during validation. GoDaddy: "Name" = host.
3. Poll until `status` is `Ready` (minutes to an hour), then check `https://<sub.domain>` (free managed cert).
4. Update: `ALLOWED_HOSTS` app setting, GitHub variable `SITE_URL`, re-run the deploy (canonical URLs,
   sitemap), and the **GitHub OAuth App** Homepage + callback URLs (owner step; see `decap-cms-github-oauth`).
5. Answer to "what do I put into Azure?": usually **nothing** — you already did it; they only add DNS records.

## Apex/root domain (`example.org`)

Use `www` as the primary (CNAME as above) and a registrar redirect from the apex to `https://www.example.org`,
or ALIAS/ANAME/CNAME-flattening if the DNS host supports it (then validate with TXT). Don't touch the
organization's live DNS without explicit permission; write `docs/dns-cutover.md` with exact steps and a
rollback (lower TTL a day before; keep old hosting until verified).

## Cost

Static Web Apps Free: $0. Application Insights/Log Analytics: within the free monthly data allowance for a
small site (set a daily cap). No paid service without writing why in the decision log.
