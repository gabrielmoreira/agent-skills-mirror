---
name: hugging-face-cli
description: "Operates the Hugging Face Hub via the hf CLI (replaces huggingface-cli): download/upload models datasets spaces, auth, cache, buckets, jobs, inference endpoints, collections, papers, and webhooks. Use when the task is Hub file or repo operations from a terminal. Not for training loops, Gradio Space Python, or treating huggingface_hub Python as the primary interface."
version: 1.0.1
risk: unknown
source: https://github.com/huggingface/skills/tree/main/skills/hf-cli
source_repo: huggingface/skills
source_type: official
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/huggingface/skills/blob/main/LICENSE
---

## When to Use

Use this skill when you need to interact with the Hugging Face Hub via the `hf` CLI. This includes:
- Downloading, uploading, and managing models, datasets, and spaces.
- Handling authentication and managing local cache.
- Managing Hugging Face Buckets.
- Running or scheduling jobs on Hugging Face infrastructure.
- Deploying and managing Inference Endpoints.
- Interacting with collections, discussions, papers, and webhooks.

## Prerequisites

- The `hf` CLI must be installed.
- A Hugging Face account and Access Token (set as `HF_TOKEN` environment variable or passed via `--token`).
- Windows host is primary (PowerShell). If using bash commands from external sources, ensure you have a compatible shell (e.g., Git Bash, WSL) or adapt them.

## Procedure

### 1. Installation

Install the `hf` CLI by downloading the installer script, reviewing it, and running it locally.

**PowerShell (Windows Host)**:
```powershell
$tmpdir = New-Item -ItemType Directory -Path (Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString()))
$installScript = Join-Path $tmpdir.FullName "hf-install.sh"
Invoke-WebRequest -Uri "https://hf.co/cli/install.sh" -OutFile $installScript
# Review the script before running
Get-Content $installScript
# Run the script (requires bash, e.g., via Git Bash or WSL)
bash $installScript
Remove-Item -Recurse -Force $tmpdir.FullName
```

*Note: The `hf` command replaces the deprecated `huggingface-cli` command.*

### 2. Authentication

Authenticate using a token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

```powershell
# Recommended: Set HF_TOKEN environment variable
$env:HF_TOKEN = "YOUR_KEY"

# Or login via browser
hf auth login

# Verify login
hf auth whoami
```

### 3. Core Commands

#### Downloading and Uploading
- **Download a model**:
  ```powershell
  hf download openai-community/gpt2 --local-dir ./gpt2
  ```
- **Upload a folder**:
  ```powershell
  hf upload my-username/my-model ./local-folder --type model
  ```
- **Upload large folder (resumable)**:
  ```powershell
  hf upload-large-folder my-username/my-model ./large-folder --type model
  ```

#### Managing Repositories
- **List models**:
  ```powershell
  hf models list --search "gpt2" --limit 10
  ```
- **Create a new repo**:
  ```powershell
  hf repos create my-username/my-new-repo --type model --private
  ```

#### Jobs
- **Run a job**:
  ```powershell
  hf jobs run ubuntu:latest "echo hello" --flavor cpu-basic
  ```
- **Schedule a job**:
  ```powershell
  hf jobs scheduled run "0 0 * * *" ubuntu:latest "echo daily" --flavor cpu-basic
  ```

#### Inference Endpoints
- **Deploy from catalog**:
  ```powershell
  hf endpoints catalog deploy --repo openai-community/gpt2
  ```

#### Cache Management
- **List cache**:
  ```powershell
  hf cache list
  ```
- **Prune detached revisions**:
  ```powershell
  hf cache prune --dry-run
  ```

### 4. Mounting Repos as Local Filesystems

Use `hf-mount` to mount Hub repositories or buckets as local filesystems.

**PowerShell Installation**:
```powershell
$tmpdir = New-Item -ItemType Directory -Path (Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString()))
$installScript = Join-Path $tmpdir.FullName "hf-mount-install.sh"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/huggingface/hf-mount/main/install.sh" -OutFile $installScript
# Review the script
Get-Content $installScript
# Run the script (requires bash)
sh $installScript
Remove-Item -Recurse -Force $tmpdir.FullName
```

**Usage**:
```powershell
# Mount a repo (read-only)
hf-mount start repo openai-community/gpt2 ./gpt2-mount
# Mount a bucket (read-write)
hf-mount start --hf-token $env:HF_TOKEN bucket myuser/my-bucket ./data-mount
# Unmount
hf-mount stop ./data-mount
```

## Pitfalls

- **Deprecated CLI**: The `huggingface-cli` command is deprecated. Use `hf` instead. Auth commands are now under `hf auth` (e.g., `hf auth whoami`).
- **Token Security**: Do not hardcode tokens in scripts. Prefer setting the `HF_TOKEN` environment variable.
- **Large Uploads**: For large folders, use `hf upload-large-folder` instead of `hf upload` to ensure resumability.
- **Shell Compatibility**: The provided install scripts are bash scripts. On Windows, ensure you have Git Bash, WSL, or a similar environment to execute them, or use PowerShell equivalents as shown in the Procedure.
- **Irreversible Actions**: `hf repos delete` and `hf buckets delete` are irreversible. Always double-check the target ID and use `--dry-run` where available.
- **Scope Limitations**: Use this skill only when the task clearly matches its upstream product or API scope. Verify commands, API behavior, pricing, quotas, credentials, and deployment effects against current official documentation before making changes. Do not treat generated examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.

## Verification

1.  **Check CLI Version**:
    ```powershell
    hf version
    ```
    *Expected output*: Prints the current `hf` version (generated with `huggingface_hub v1.21.0` or later).

2.  **Verify Authentication**:
    ```powershell
    hf auth whoami
    ```
    *Expected output*: Your Hugging Face username and account details.

3.  **List Cached Repositories**:
    ```powershell
    hf cache list
    ```
    *Expected output*: A list of locally cached repositories and revisions.

4.  **Check Environment**:
    ```powershell
    hf env
    ```
    *Expected output*: Information about the current environment, including token status and cache directory.
