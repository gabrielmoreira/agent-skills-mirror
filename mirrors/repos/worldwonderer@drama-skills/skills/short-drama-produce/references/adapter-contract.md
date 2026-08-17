# Adapter Contract

## Job file

```json
{
  "schema_version": "1.0",
  "job_id": "EP001-SHOT001-image",
  "modality": "image",
  "adapter": "studio-image",
  "prompt": "the complete prompt sent to production",
  "source": "剧集/EP001/storyboard/keyframe-prompts.md",
  "references": ["输入/approved-character-reference.png"],
  "outputs": ["剧集/EP001/制作成果/images/SHOT001.png"],
  "parameters": {"width": 1080, "height": 1920},
  "overwrite": false
}
```

- `modality`: `image`, `video`, `tts`, or `music`. `tts` is one bounded spoken
  utterance; `music` is a separately accepted timeline-level cue or song and
  must not be smuggled into every shot's video job.
- `source`: optional current project text/spec that owns the prompt.
- `references`: zero to sixteen current project files actually sent to production.
- `outputs`: one to sixteen unique paths rooted at top-level `production/` or
  `剧集|episodes/<EP>/制作成果|production/`; extensions must match the modality.
  A nested directory merely named `production` does not grant write access to
  protected input or delivery trees.
- `parameters`: provider-neutral public settings only. Secret-like keys are rejected.
- `overwrite`: must be explicitly true to replace an existing result.

`prepare` records internal digests of source/reference bytes and returns the exact confirmation phrase. Callers never
calculate those digests. A changed input requires prepare and confirmation again.

## Adapter config

Keep this file outside the project:

```json
{
  "adapters": {
    "studio-image": {
      "command": ["python3", "/opt/studio/image_adapter.py"],
      "timeout_seconds": 600
    }
  }
}
```

`command` is an argv array, never a shell string. Timeout is 1–3600 seconds. Do not put credentials in this file;
let the adapter read its environment or operating-system credential store.

## Adapter stdin

The adapter receives one UTF-8 JSON document as raw stdin bytes. Read the
binary stream (for example `json.load(sys.stdin.buffer)`) rather than relying
on the machine locale. The document contains the confirmed job plus:

- `run_id`: unique attempt ID;
- `project_root`: local absolute path to a private, run-scoped snapshot containing
  the exact confirmed `source` and `references`. It is not the live creator
  project and is deleted after the attempt.
- `output_root`: empty private, run-scoped staging directory owned by the
  production tool. Every adapter output source must be a direct regular-file
  child of this directory. The whole directory is deleted after success or
  failure.

It may translate provider-neutral parameters into its chosen SDK/API. Optional
provider adapters under `scripts/` document and implement known translations;
the project job remains provider-neutral, and adapter selection, model access,
polling and credentials stay in the external runtime configuration.

## Adapter stdout

On success, write one bounded UTF-8 JSON object to stdout. Portable adapters
should ASCII-escape JSON strings so Windows locale settings cannot corrupt
project paths:

```json
{
  "outputs": [
    {
      "target": "剧集/EP001/制作成果/images/SHOT001.png",
      "source": "/temporary/adapter/result.png"
    }
  ],
  "provider_job_id": "optional-public-id"
}
```

Targets must appear in exactly the confirmed order. Sources must be direct
regular-file children of `output_root`, not symlinks. The tool opens each source
without following links, copies the pinned bytes into the project, records
size/media type/checksum, and removes staging. It never stores adapter
stdout/stderr or environment values.

On a provider failure, an adapter may write only this whitelisted evidence to stdout:

```json
{
  "error": {
    "provider": "studio-image",
    "category": "rate_limit",
    "code": "rate_limit_exceeded",
    "http_status": 429,
    "request_id": "request_safe_123",
    "retryable": true
  }
}
```

Never include provider messages, response bodies, prompts, paths or credentials.
The production run record keeps only validated fields; malformed failure output
is replaced with a generic adapter exit code.

A nonzero exit, timeout, malformed response or mismatched output marks the run failed. Because the adapter may have
submitted paid work before failing locally, confirmation is consumed as soon as execution starts; retry only after a
new creator confirmation. A job with an unresolved `running` attempt cannot be prepared, confirmed, or run again;
wait for its terminal record or investigate the interrupted attempt first.

## Operational reconciliation

`production_tool.py audit <project>` reads only local production metadata and the
current output bytes. It reports terminal failures, retryable failures, recovered
jobs, unresolved running attempts, repeated content fingerprints, and missing or
changed outputs. Terminal state, recovery, and repeated output claims are ordered
by validated completion time rather than start time. For paths written more than
once, the latest completed successful claim is authoritative for this operational
check. Only attempts bound to the current stored job fingerprint can claim its
current outputs; older fingerprints remain visible as `superseded` attempt history.
A successful record must declare exactly the current job's output set and media
types before any output claim is trusted. Jobs, confirmations, run records, and the
production lock use pinned no-follow directories where directory FDs are available,
and reparse/identity checks on the portable fallback. A linked parent chain fails
closed instead of redirecting state outside the project.

The audit deliberately returns `quality_verdict: not_assessed`. A provider success,
retry recovery, file presence, size, or checksum proves execution/custody only; it
does not prove identity, performance, continuity, lip-sync, mix, edit, or audience
quality. Those claims require an authorized observation and a separate review.
