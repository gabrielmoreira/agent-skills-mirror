---
name: decap-cms-github-oauth
description: >-
  Set up and troubleshoot Decap CMS (formerly Netlify CMS) on Azure Static Web Apps with GitHub sign-in
  through a small OAuth Function. Use when creating or fixing /admin/, creating the GitHub OAuth App,
  moving CMS sign-in to a new domain, inviting editors, fixing "Config Errors", "does not have access to
  this repo", or editors being signed out, and when writing the editor guide.
---

# Decap CMS with GitHub OAuth on Azure Static Web Apps

## How it fits together

- `public/admin/index.html` loads `decap-cms.js` (copied from `node_modules` by `scripts/copy-cms.mjs`).
- `cms/config.yml` is the source config (YAML anchors for shared field groups). `scripts/build-cms-config.mjs`
  writes `public/admin/config.yml` with the real repo, branch and site URL on every build.
- `backend: { name: github, repo: <owner>/<repo>, branch: main, base_url: <site>, auth_endpoint: api/auth }`
  with `publish_mode: editorial_workflow` (drafts → review → publish = PRs with preview deployments).
- `api/src/functions/oauth.js`: `/api/auth` redirects to GitHub with a signed `state`; `/api/callback`
  exchanges the code and posts the token back to the CMS window. It reads `GITHUB_OAUTH_CLIENT_ID` and
  `GITHUB_OAUTH_CLIENT_SECRET` from Static Web App **app settings** and checks the host against
  `ALLOWED_HOSTS` (using `x-ms-original-url`). Returns 503 until configured.

## Create the GitHub OAuth App (one time; GitHub has no API for this)

Preferred: the owner signs in to GitHub in the Playwright browser and you do the clicks.

1. Go to `https://github.com/settings/applications/new` (owner's account, or the org's settings if the
   repo is in an organization).
2. Application name: "<Org> Website CMS". Homepage URL: `https://<live domain>`. Authorization callback
   URL: `https://<live domain>/api/callback`. Register.
3. **Uncheck "Expire user access tokens"** (Decap cannot refresh tokens; editors would be signed out).
4. Generate a client secret. **Never print it.** Read it from the page into a temp file
   (e.g. `browser_evaluate` with a `filename`), then:

   ```powershell
   az staticwebapp appsettings set -n <swa> -g <rg> --setting-names GITHUB_OAUTH_CLIENT_ID=<id> "GITHUB_OAUTH_CLIENT_SECRET=$(Get-Content $tmp -Raw)" --output none
   Remove-Item $tmp
   ```

   Or use the starter's `infra/deploy.ps1 -OAuthClientId <id> -OAuthClientSecret (Read-Host -AsSecureString)`.
5. Verify: `curl -sI https://<site>/api/auth?provider=github&scope=public_repo` → `302` to github.com.
   Then sign in at `/admin/` and confirm collections load.

**One callback URL per OAuth App.** Sign-in works only on the domain in the callback. When a custom
domain is added, update Homepage URL + callback in the app settings (owner step) and add the domain to
`ALLOWED_HOSTS`. Preview environments are for viewing changes, not for signing in.

## Editors

- Invite personal GitHub accounts as collaborators (repo → Settings → Collaborators).
- **Enterprise Managed User (EMU) accounts** (names like `jane_contoso`) cannot be invited to personal
  repos — the API returns 422. Editors must use a personal account. Put this in the editor guide's
  troubleshooting table with "Log out → switch account on github.com → Login with GitHub".
- Fallbacks when sign-in breaks: GitHub web editor (pencil icon → new branch → PR), local CMS
  (`npm run cms:local` + `npm run dev`, then `/admin/index.html`), or a hosted OAuth bridge such as DecapBridge.

## Config rules that prevent outages

- `sortable_fields` must be a **list of field names**. An object with `default` crashed the live CMS.
- Do **not** add a `media_library` block for the default library (Decap treats any block as external).
- Every entry needs an explicit `published: true|false` boolean (a missing boolean shows as "off").
- Booleans, selects and relations need `required: false` + defaults where optional.
- Image fields: `alt` required beside every image; add a `focus` string field (hint: "50% 30%").
- Keep the CMS config in sync with the Zod schema: a unit test should assert every schema field is
  editable and every collection exists.
- **An e2e test must open `/admin/`** (with the backend stubbed or just the config load) and fail if the
  page shows "Config Errors" or the bundle fails. Also smoke-test `/admin/config.yml` and `/admin/decap-cms.js`
  after deploy.
- Sort events newest first for editors: `sortable_fields: ['startDateTime', 'title']` and tell editors to
  click the column twice (Decap remembers).

## Editor guide (plain language)

Cover: signing in, see what's coming up, change one date of a recurring series (overrides), cancel,
postpone, add a one-time event, duplicate, add a community event or organizer, teacher/band links,
dance styles, venues and the map, homepage slideshow, the banner, photos (permission + alt + focus point),
pages/membership/prices, checking a change before it goes live (preview link on the PR), undoing a
change, sign-in setup (administrator), recovering from mistakes. Short sentences; numbered steps;
screenshots if helpful.
