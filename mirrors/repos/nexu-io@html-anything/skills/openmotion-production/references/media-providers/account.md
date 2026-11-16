# OpenDesign account models

Checked on 2026-11-15 against [OpenDesign source](https://github.com/nexu-io/open-design/tree/59e4f2ae85de7e7318a5e6bdcf3a34584c4b7582) and the command help of `@powerformer/vela-cli@0.1.10`. The CLI owns the account service contract; OpenMotion does not reproduce private authentication endpoints or bundle its binary.

The user signs in through **Settings → Account → Sign in with OpenDesign** and completes authorization in their browser. On first use, OpenMotion prepares the pinned connector in its private data directory. Credentials belong to this installation, are not copied from other apps, and are never returned to the Agent. Account models appear under provider ID `account`, alongside BYOK. A successful login establishes identity, not billing or generation acceptance; refresh subscription/usage for actual account balances.

Call `openmotion_media_use` with `action=inspect`, then `action=reference, provider=account`, then `action=models, provider=account, refresh=true`. Discovery uses the connector's remote model and media catalogues, including their enabled flags. Use only returned IDs and the provider's model parameter documentation; no model name or entitlement is guessed.

```json
{"action":"generate","provider":"account","projectId":"PROJECT_ID","requestId":"account-image-one","model":"CATALOGUE_MODEL_ID","modality":"image","prompt":"A ceramic cup","parameters":{}}
```

Image parameters supported by the connector boundary: `aspect_ratio`, `resolution`, `quality`, `size`. Video uses `modality=video`, and accepts `ratio`, `resolution`, `duration`, `generate_audio`. Speech uses `modality=audio`, `mode=text-to-speech`, and requires `parameters.voice`; other audio operations are not claimed. Unsupported parameters fail before submission.

The service executes one `image gen`, `video gen` or `audio speech` command with `--model`, `--prompt`, `--no-wait`, `--json`. It saves the returned task_id, polls only that task through the corresponding `get`, and validates the downloaded file before importing it into the original project. Poll local `action=status` with the original projectId/jobId; do not submit another task to check progress. Local requestId replay returns the original job.

Account session identity is captured when queuing. Signing out or switching identity prevents an old queued task from submitting under a new account. Failed CLI calls omit private stderr and cannot establish the exact remote error. Check account connectivity, available credits and original task history before retrying. Cancellation stops local work; it does not prove a remote cancellation or refund. Interrupted/uncertain paid requests are never automatically resubmitted or routed to another provider.
