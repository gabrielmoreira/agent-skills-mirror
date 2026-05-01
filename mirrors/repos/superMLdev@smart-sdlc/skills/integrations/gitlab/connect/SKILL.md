---
name: gitlab-connect
description: "Set up and verify GitLab integration using the GitLab CLI or API token. Use when the user says 'connect to GitLab', 'set up GitLab', or 'configure GitLab'."
---

# GitLab — Connect and Verify

## Goal

Verify GitLab CLI authentication (or API token) and store project details in config so branch creation, MR creation, and other GitLab skills work seamlessly.

---

## Step 1: Check GitLab CLI is Available

```bash
which glab && glab --version
```

If not found:
> "GitLab CLI (`glab`) is not installed. Install it from https://gitlab.com/gitlab-org/cli or run:
> - macOS: `brew install glab`
> - Ubuntu: `sudo apt install glab`
> - Windows: `winget install Glab.Glab`"

If `glab` is unavailable, fall back to API token (direct `curl` calls). Ask which approach to use.

---

## Step 2: Authenticate (CLI path)

```bash
glab auth login
```

Follow prompts:
1. GitLab instance: `gitlab.com` or your self-hosted URL
2. Authentication: Token (recommended) or Web Browser
3. Provide a Personal Access Token with scopes: `api`, `read_user`, `write_repository`

> Security note: provide the token interactively — do not paste it in this chat.

---

## Step 3: Verify Authentication

```bash
glab auth status
```

Should show: `✓ Logged in to {instance} as {username}`

---

## Step 4: Set Default Project

```bash
glab config set -g default_project "{namespace/project-name}"
```

Or configure via `_superml/config.yml`:
```yaml
integrations:
  gitlab:
    instance: "gitlab.com"
    namespace: "{namespace}"
    project: "{project-name}"
    default_branch: "main"
    connected: true
    connected_at: "{date}"
```

---

## Step 5: Verify Project Access

```bash
glab repo view {namespace/project-name}
```

---

## Done

> ✅ GitLab connected. You can now use `gitlab-create-branch` and `gitlab-create-mr`.
