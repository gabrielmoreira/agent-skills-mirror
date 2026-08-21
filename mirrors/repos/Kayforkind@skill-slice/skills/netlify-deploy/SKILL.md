---
name: netlify-deploy
description: "Publishes a linked web project with `npx netlify`: status/login, link or init, draft `netlify deploy`, then `--prod`, honoring netlify.toml build and publish directories. Use when a site needs a Netlify draft URL or production alias. Not for serverless function authoring (netlify-functions). Do not use for CLI install, `netlify dev`, or context-scoped env vars (netlify-cli-and-deploy)."
version: 1.0.1
---

## When to Use

Use this skill when the user asks to:
- Deploy, publish, or host a web project on Netlify
- Create a preview/draft deploy or a production deploy
- Link an existing local project to a Netlify site
- Initialize a new Netlify site from a local project or Git repo
- Troubleshoot a Netlify CLI deployment failure

Trigger keywords: **netlify, deploy, publish, host, preview deploy, production deploy, netlify link, netlify init, netlify.toml**

## Prerequisites

- **Node.js** installed and available on `PATH` (Netlify CLI runs via `npx`).
- **Netlify CLI**: No global install required; `npx netlify` is the primary invocation.
- **Authentication**: An active Netlify login session (browser OAuth) **or** a `NETLIFY_AUTH_TOKEN` environment variable set.
- **Project**: A valid web project in the current working directory (must contain a `package.json`, static HTML, or a build output directory).
- **Windows host (primary)**: Commands below assume PowerShell. On PowerShell, use `$env:NETLIFY_AUTH_TOKEN = "YOUR_TOKEN"` instead of `export`.
- **Sandbox networking**: Deployment requires outbound network access. If the sandbox blocks network calls, rerun with `sandbox_permissions=require_escalated`.
- **Timeouts**: Deployments can take several minutes. Use appropriate timeout values (e.g., 300+ seconds for build + upload).

## Procedure

### 1. Verify Netlify CLI Authentication

Check whether the user is already logged in:

```powershell
npx netlify status
```

**Expected output patterns**:
- Authenticated: Shows logged-in user email and current site link status.
- Not authenticated: "Not logged into any site" or an authentication error.

**If not authenticated**, guide the user through browser OAuth:

```powershell
npx netlify login
```

This opens a browser window for OAuth. Wait for the user to complete login, then re-run `npx netlify status` to confirm.

**Alternative — API Key authentication** (use when browser OAuth is unavailable):

PowerShell:
```powershell
$env:NETLIFY_AUTH_TOKEN = "YOUR_TOKEN_HERE"
```

bash/zsh:
```bash
export NETLIFY_AUTH_TOKEN=YOUR_TOKEN_HERE
```

Tokens are generated at: `https://app.netlify.com/user/applications#personal-access-tokens`

> Never commit tokens to Git. Use `YOUR_TOKEN_HERE` as a placeholder in any shared output.

### 2. Detect Site Link Status

From the `npx netlify status` output, determine:
- **Linked**: Site is already connected (output shows site name and URL). Skip to step 4.
- **Not linked**: Proceed to step 3.

### 3. Link to Existing Site or Create New

**3a. Attempt to link by Git remote** (if the project is Git-based):

```powershell
git remote show origin
```

Extract the remote URL (format: `https://github.com/username/repo` or `git@github.com:username/repo.git`), then:

```powershell
npx netlify link --git-remote-url https://github.com/username/repo
```

**3b. If linking fails** (site does not exist on Netlify yet), create a new site:

```powershell
npx netlify init
```

This walks the user through:
1. Choosing team/account
2. Setting site name
3. Configuring build settings
4. Creating `netlify.toml` if needed

### 4. Verify Dependencies

Before deploying, ensure project dependencies are installed:

```powershell
# npm
npm install

# yarn
yarn install

# pnpm
pnpm install
```

Detect the package manager from lockfile presence (`package-lock.json` → npm, `yarn.lock` → yarn, `pnpm-lock.yaml` → pnpm).

### 5. Deploy to Netlify

**5a. Preview / Draft deploy** (default — creates a unique draft URL for testing):

```powershell
npx netlify deploy
```

**5b. Production deploy** (for new sites or when the user explicitly requests production):

```powershell
npx netlify deploy --prod
```

**Deployment process**:
1. CLI detects build settings from `netlify.toml` or prompts the user.
2. Builds the project locally using the configured build command.
3. Uploads built assets to Netlify.
4. Returns a deployment URL.

### 6. Report Results

After deployment, report to the user:
- **Deploy URL**: Unique URL for this deployment (draft or production).
- **Site URL**: Production URL (if `--prod` was used).
- **Deploy logs**: Link to the Netlify dashboard for detailed logs.
- **Next steps**: Suggest `npx netlify open` to view the site or dashboard.

## Handling netlify.toml

If a `netlify.toml` file exists, the CLI uses it automatically. If not, the CLI prompts for:
- **Build command**: e.g., `npm run build`, `next build`
- **Publish directory**: e.g., `dist`, `build`, `.next`

Common framework defaults:

| Framework | Build command | Publish directory |
|---|---|---|
| Next.js | `npm run build` | `.next` |
| React (Vite) | `npm run build` | `dist` |
| Static HTML | _(none)_ | `.` (current directory) |

Detect the framework from `package.json` dependencies and suggest appropriate settings.

> **Load `references/netlify-toml.md`** when the user needs to author or debug a `netlify.toml` file, configure redirects, headers, plugins, or environment-specific build settings.

## Pitfalls

- **"Not logged in"** → Run `npx netlify login` or set `NETLIFY_AUTH_TOKEN`.
- **"No site linked"** → Run `npx netlify link` (existing site) or `npx netlify init` (new site).
- **"Build failed"** → Check the build command and publish directory in `netlify.toml` or CLI prompts. Verify dependencies are installed. Review build logs for specific errors.
- **"Publish directory not found"** → Verify the build command ran successfully and the publish directory path is correct.
- **Sandbox network blocks** → If deployment fails with timeouts, DNS errors, or connection resets, rerun with `sandbox_permissions=require_escalated`. The deploy requires escalated network access when sandbox networking blocks outbound requests. Example message to user: *"The deploy needs escalated network access to deploy to Netlify. I can rerun the command with escalated permissions—want me to proceed?"*
- **PowerShell environment variables** → Use `$env:NETLIFY_AUTH_TOKEN = "YOUR_TOKEN"` on Windows PowerShell. Using `export` will fail silently.
- **Never commit secrets** → Do not write tokens, API keys, or `.env` secrets into Git. Set them in the Netlify dashboard under Site Settings → Environment Variables. Access in builds via `process.env.VARIABLE_NAME`.
- **Always test with draft first** → Use `npx netlify deploy` (no `--prod`) before deploying to production to catch build or routing issues.

## Verification

After deployment, verify success with these checkable commands:

```powershell
# Confirm site link and current status
npx netlify status

# View the deployed site in the browser
npx netlify open

# View function logs (if using Netlify Functions)
npx netlify logs
```

**Expected verification outputs**:
- `npx netlify status` shows the site name, URL, and last deploy status without error.
- `npx netlify open` launches the deployed site URL in the default browser.
- The draft deploy URL returned by `npx netlify deploy` loads successfully in a browser.
- For production deploys, the production site URL serves the latest content.

## Bundled References (Load As Needed)

Load these reference files only when the specific need arises:

- **`references/cli-commands.md`** — Load when the user asks about specific Netlify CLI subcommands, flags, or advanced CLI usage beyond basic deploy/link/init.
- **`references/deployment-patterns.md`** — Load when the user needs guidance on monorepo deploys, continuous deployment via Git integration, branch deploys, or deploy contexts.
- **`references/netlify-toml.md`** — Load when the user needs to author, edit, or debug a `netlify.toml` configuration file (build settings, redirects, headers, plugins, environment variables).

## Related Skills

- **vercel-deploy** — For deploying to Vercel instead of Netlify.
- **github-pages-deploy** — For static site deployment to GitHub Pages.

## Reference

- Netlify CLI Docs: `https://docs.netlify.com/cli/get-started/`
- netlify.toml Reference: `https://docs.netlify.com/configure-builds/file-based-configuration/`
- Personal Access Tokens: `https://app.netlify.com/user/applications#personal-access-tokens`
