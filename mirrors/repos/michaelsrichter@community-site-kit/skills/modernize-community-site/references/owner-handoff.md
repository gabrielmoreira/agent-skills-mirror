# Owner handoff and update emails

## After every deploy, send one short email (or Teams message)

If the WorkIQ tools are available, send it with `workiq-do_action` → `/me/sendMail` (HTML body). Otherwise
print the message for the owner to copy. Keep it scannable:

```html
<p>Hi {{OWNER_FIRST_NAME}},</p>
<p>{{ONE_SENTENCE_WHAT_CHANGED}} It is live at <a href="{{URL}}">{{URL}}</a>.</p>
<h3>What changed</h3>
<ul><li>…</li></ul>
<h3>Checks</h3>
<p>Type check, {{N}} unit, {{N}} API and {{N}} browser tests (including accessibility scans) passed. Link check
clean. CI and deploy green. Live smoke test {{N}}/{{N}}. Screenshots reviewed in light and dark mode on
phone and desktop.</p>
<h3>Still needs you</h3>
<ul><li>…only items that truly need the owner…</li></ul>
```

Subject: `{{SHORT_NAME}} website: {{what changed}} is live`.

## First launch email also includes

- Repository URL, Azure resource names (no secrets), monthly cost estimate (Free plan ≈ $0; Application
  Insights within the free data allowance for a small site).
- How editors sign in: `https://<site>/admin/` → Login with GitHub; how to invite editors (repo → Settings →
  Collaborators); personal GitHub accounts only (EMU accounts can't be invited).
- Where the docs are: editor guide, DNS cutover, rollback.

## Manual steps that usually remain (say exactly what to click)

| Step | Who | Exact instructions |
| --- | --- | --- |
| Create or update the GitHub OAuth App | Owner (or agent in owner's signed-in browser) | GitHub → Settings → Developer settings → OAuth Apps → app → Homepage URL `https://<domain>`, Authorization callback URL `https://<domain>/api/callback` → Update application |
| DNS for a custom subdomain | Owner at the registrar | CNAME `<sub>` → `<default-hostname>.azurestaticapps.net`; TXT `_dnsauth.<sub>` → `<validation token>` |
| DNS for the apex/root domain | Owner | Prefer `www` + a registrar redirect from the apex; or ALIAS/ANAME/flattened CNAME if supported |
| Photo permission | Owner | Confirm the photographer agreed; otherwise swap photos in the CMS (Gallery) |
| Invite editors | Owner | Repo → Settings → Collaborators → Add people |
| Analytics IDs | Owner | GA4 Admin → Data streams → Measurement ID; Clarity → Settings → Project ID |

## Things that do NOT need the owner

Azure app settings, GitHub secrets/variables, redirects, content, tests, docs, geocoding, image work —
the agent does these. When the owner asks "what do I need to put into Azure?", the usual answer is
"nothing — it's done; you only need the DNS records."
