# OAuth Third-Party Login Configuration Guide

This document explains how to configure Google and GitHub OAuth login, as well as Cloudflare Turnstile CAPTCHA verification.

## Table of Contents

- [Google OAuth Configuration](#google-oauth-configuration)
- [GitHub OAuth Configuration](#github-oauth-configuration)
- [Cloudflare Turnstile Configuration](#cloudflare-turnstile-configuration)
- [Deployment Configuration](#deployment-configuration)
- [FAQ](#faq)

---

## Google OAuth Configuration

### Step 1: Create a Google Cloud Project

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project selector at the top, then click "New Project"
3. Enter a project name (e.g., `QuantDinger`), click "Create"

### Step 2: Configure OAuth Consent Screen

1. In the left menu, select "APIs & Services" → "OAuth consent screen"
2. Choose user type:
   - **External**: Allows any Google account to login (recommended)
   - **Internal**: Only for organization users (requires Google Workspace)
3. Fill in application information:
   - App name: `QuantDinger`
   - User support email: Your email
   - Developer contact information: Your email
4. Click "Save and Continue", skip "Scopes" and "Test users", complete setup

### Step 3: Create OAuth 2.0 Client ID

1. In the left menu, select "APIs & Services" → "Credentials"
2. Click "+ Create Credentials" → "OAuth client ID"
3. Select application type: **Web application**
4. Enter name: `QuantDinger Web Client`
5. Add "Authorized redirect URIs":
   ```
   http://localhost:5000/api/auth/oauth/google/callback
   ```
   > After deploying to server, add production URI (see below)
6. Click "Create"
7. Copy the generated **Client ID** and **Client Secret**

### Step 4: Configure .env File

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/auth/oauth/google/callback
```

---

## GitHub OAuth Configuration

### Step 1: Create GitHub OAuth App

1. Visit [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "OAuth Apps" → "New OAuth App"
3. Fill in application information:
   - **Application name**: `QuantDinger`
   - **Homepage URL**: `http://localhost:8080` (or your domain)
   - **Authorization callback URL**:
     ```
     http://localhost:5000/api/auth/oauth/github/callback
     ```
4. Click "Register application"

### Step 2: Get Credentials

1. On the application details page, copy the **Client ID**
2. Click "Generate a new client secret"
3. Immediately copy the **Client Secret** (shown only once)

### Step 3: Configure .env File

```bash
# GitHub OAuth
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret
GITHUB_REDIRECT_URI=http://localhost:5000/api/auth/oauth/github/callback
```

---

## Cloudflare Turnstile Configuration

Turnstile is a free, privacy-friendly CAPTCHA service provided by Cloudflare to prevent bot attacks.

### Step 1: Create Turnstile Widget

1. Visit [Cloudflare Turnstile](https://dash.cloudflare.com/?to=/:account/turnstile)
2. Click "Add site"
3. Fill in information:
   - **Site name**: `QuantDinger`
   - **Domain**: Add your domain (for local development, add `localhost`)
   - **Widget Mode**: Select `Managed` (recommended) or `Invisible`
4. Click "Create"

### Step 2: Get Keys

After creation, you will see:
- **Site Key**: Used by frontend, can be public
- **Secret Key**: Used by backend, keep it secret

### Step 3: Configure .env File

```bash
# Cloudflare Turnstile
TURNSTILE_SITE_KEY=your-site-key
TURNSTILE_SECRET_KEY=your-secret-key
```

---

## Deployment Configuration

When deploying to a server with a domain name, you need to update the configuration.

### Scenario 1: Same Domain for Frontend and Backend (Recommended)

Assuming your domain is `yourdomain.com`, with frontend and backend deployed under the same domain via nginx reverse proxy:
- Frontend: `https://yourdomain.com`
- Backend API: `https://yourdomain.com/api`

**.env Configuration:**
```bash
# Frontend URL (redirect after OAuth success)
FRONTEND_URL=https://yourdomain.com

# Google OAuth
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/auth/oauth/google/callback

# GitHub OAuth
GITHUB_REDIRECT_URI=https://yourdomain.com/api/auth/oauth/github/callback
```

### Scenario 2: Separate Domains for Frontend and Backend

Assuming:
- Frontend: `https://yourdomain.com`
- Backend API: `https://api.yourdomain.com`

**.env Configuration:**
```bash
FRONTEND_URL=https://yourdomain.com

GOOGLE_REDIRECT_URI=https://api.yourdomain.com/api/auth/oauth/google/callback

GITHUB_REDIRECT_URI=https://api.yourdomain.com/api/auth/oauth/github/callback
```

### Update OAuth Provider Settings

After deployment, you also need to update callback URLs in OAuth provider dashboards:

**Google Cloud Console:**
1. Go to "Credentials" page
2. Edit your OAuth client
3. Add production URL in "Authorized redirect URIs":
   ```
   https://yourdomain.com/api/auth/oauth/google/callback
   ```

**GitHub Developer Settings:**
1. Edit your OAuth App
2. Update "Authorization callback URL" to production URL

### Turnstile Domain Configuration

In Cloudflare Turnstile dashboard, make sure to add your production domains:
- `yourdomain.com`
- `www.yourdomain.com` (if used)

---

## FAQ

### Q: OAuth login shows "redirect_uri_mismatch" error

**A:** Callback URL mismatch. Please check:
1. `GOOGLE_REDIRECT_URI` or `GITHUB_REDIRECT_URI` in `.env`
2. Callback URL configured in OAuth provider dashboard
3. Both must match exactly (including http/https, port, path)

### Q: Turnstile verification keeps failing

**A:** Please check:
1. Are `TURNSTILE_SITE_KEY` and `TURNSTILE_SECRET_KEY` correct?
2. Is your current domain added to Turnstile's domain list?
3. For local development, make sure `localhost` is added

### Q: How to disable third-party login?

**A:** Leave the related configuration empty in `.env`:
```bash
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
```
The system will automatically hide third-party login buttons.

### Q: How to disable user registration?

**A:** Set in `.env`:
```bash
ENABLE_REGISTRATION=false
```

### Q: OAuth login succeeds but cannot redirect back to frontend

**A:** Please check if `FRONTEND_URL` is configured correctly, make sure it's the complete frontend page URL (including protocol).

---

## Related Links

- [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- [GitHub Developer Settings](https://github.com/settings/developers)
- [Cloudflare Turnstile](https://dash.cloudflare.com/?to=/:account/turnstile)
