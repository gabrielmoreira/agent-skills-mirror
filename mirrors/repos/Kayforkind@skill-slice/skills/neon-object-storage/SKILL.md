---
name: neon-object-storage
description: "Provisions Neon S3-compatible object storage that copy-on-write branches with a Neon Postgres project for uploads, images, documents, and avatars. Use when files must stay in sync with rows across preview and dev branches via SigV4 path-style S3. Not for Vercel Blob or Edge Config (vercel-storage), standalone AWS S3/R2 without Neon, or enabling storage on existing non-us-east-2 projects."
version: 1.0.1
risk: unknown
source: https://github.com/neondatabase/agent-skills/tree/main/skills/neon-object-storage
source_repo: neondatabase/agent-skills
source_type: official
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/neondatabase/agent-skills/blob/main/LICENSE
---

# Neon Object Storage

Neon Object Storage is an S3-compatible object store that branches with your Neon Postgres project. Every branch gets its own isolated, copy-on-write storage state, so files and database rows stay in sync across dev, preview, staging, and production. It speaks the S3 API (SigV4, path-style addressing only), so the AWS SDKs, `boto3`, the AWS CLI, and presigned URLs all work without a proprietary client.

> **Preview feature.** Object Storage is early access and only available on **new** projects in the **`us-east-2`** region. It cannot be enabled on existing projects. If the user does not yet have access, point them to the private beta sign-up: <https://neon.com/blog/were-building-backends#access>.

## When to Use

Reach for this skill when the user needs to store files (images, uploads, generated assets, documents, backups) and **any** of the following are true:

- **They already use Neon Postgres and don't want a second provider.** One backend, one bill, one CLI, one set of branches — instead of standing up and wiring a separate AWS S3 / R2 / Supabase Storage account. The same Neon credential that backs the database backs storage.
- **Files must stay in sync with the database across environments.** Storage branches _together with_ your Postgres data. Fork a branch and the child instantly inherits the parent's buckets and objects at that point in time — copy-on-write, so no data is duplicated. A preview branch gets a consistent snapshot of _both_ the rows and the files they reference, and writes on the child never touch the parent.
- **They want safe, throwaway environments.** Upload, overwrite, and delete files in a preview/CI branch without any risk to production data, then drop the branch.
- **They want standard S3 tooling.** Built on S3 semantics and speaks the S3 API, so the AWS SDKs, `boto3`, the AWS CLI, and presigned URLs all work — reliable and familiar, with no proprietary client.

If the user has no Neon project, isn't on Postgres, and just needs a standalone CDN-backed asset store, a dedicated object store may fit better — but the moment branch-consistent files + rows matter, this is the reason to use it.

## Prerequisites

1. **A Neon project in `us-east-2`.** Object Storage is preview-only and cannot be retrofitted onto existing projects in other regions. Confirm the user's project is new and in `us-east-2` before proceeding.
2. **The Neon CLI** (`neon`) installed and authenticated. Verify:
   ```powershell
   neon --version
   neon auth whoami
   ```
3. **A linked branch.** Run `neon link` in the project root if not already linked (see the `neon` skill for the branch-first workflow, `link`/`checkout`, and `neon.ts` basics).
4. **Node.js 18+** if using the Files SDK or AWS SDK client examples below.
5. **AWS SDK peer dependencies** if using the Files SDK (install step in Procedure).

## Procedure

### 1. Declare buckets in `neon.ts`

Object storage is part of the `neon.ts` infrastructure-as-code config. Declare buckets under `preview.buckets`, keyed by bucket name:

```typescript
// neon.ts
import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  preview: {
    buckets: {
      images: {}, // private by default
      "public-assets": { access: "public_read" },
    },
  },
});
```

Two access modes are supported:
- **`private`** (default) — every operation requires a credential.
- **`public_read`** — anonymous reads allowed; writes still require authentication.

### 2. Provision the declared buckets

Reconcile the declaration against the linked branch the Terraform way:

```powershell
neon config status   # print the branch's live config (which buckets exist)
neon config plan      # dry-run diff of what apply would change
neon config apply     # create the declared buckets  (neon deploy is an alias)
```

`neon deploy` is an alias for `neon config apply`. Use either.

> **Branch-scoped provisioning.** When a `neon.ts` is present, `neon checkout` applies the policy as it _creates_ a branch, so a fresh preview/CI branch comes up with its buckets already provisioned (and copy-on-write objects inherited from the parent). Checking out an _existing_ branch does **not** reconcile it — run `neon deploy` to apply changes.

### 3. Pull S3 credentials into your local environment

Provisioning (`config apply` / `deploy`), `link`, and `checkout` also pull the branch's S3 credentials into your local `.env.local` automatically. If you need to refresh them manually:

```powershell
neon env pull            # writes the branch's vars into .env (or .env.local)
# or, without writing a file, inject at runtime:
neon-env run -- <your dev command>
```

Neon injects **AWS-standard** S3 env vars so the AWS SDKs work from the environment with zero extra config:

| Variable                 | Meaning                                             |
| ------------------------ | --------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`      | S3 Access Key ID (the branch credential's token id) |
| `AWS_SECRET_ACCESS_KEY`  | S3 Secret Access Key                                |
| `AWS_ENDPOINT_URL_S3`    | Branch S3 endpoint URL                              |
| `AWS_REGION`             | Region, e.g. `us-east-2`                            |

Credentials are branch-scoped and valid for that branch and all its descendants.

### 4. Read and write objects — Files SDK (recommended)

The simplest, most portable way to read and write objects is the [Files SDK](https://files-sdk.dev) with its `neon` adapter — a small, unified storage API (`upload`, `download`, `url`, `list`, `exists`, `copy`, `delete`, `signedUploadUrl`) over web-standard I/O. It uses the AWS S3 client under the hood, configured appropriately for Neon, and relabels errors as `Neon error` — so there's nothing to misconfigure. Reach for this first.

Install it alongside the AWS S3 peer dependencies the adapter uses internally:

```powershell
npm install files-sdk @aws-sdk/client-s3 @aws-sdk/s3-presigned-post @aws-sdk/s3-request-presigner
```

The adapter resolves its endpoint, region, and credentials from the same injected `AWS_*` env vars — pass only the bucket name:

```typescript
import { Files } from "files-sdk";
import { neon } from "files-sdk/neon";

const files = new Files({ adapter: neon({ bucket: "images" }) });

// Upload — body may be a Buffer, Uint8Array, Blob, File, ReadableStream, or string
await files.upload("generated/cat.jpg", fileBuffer, { contentType: "image/jpeg" });

// Download
const file = await files.download("generated/cat.jpg");
const bytes = new Uint8Array(await file.arrayBuffer());

// Presigned GET — share without exposing credentials (defaults to a 1h expiry)
const url = await files.url("generated/cat.jpg", { expiresIn: 3600 });

// Plus: files.exists(), files.list({ prefix }), files.copy(), files.delete(), files.signedUploadUrl()
```

Swap the adapter import (`files-sdk/s3`, `files-sdk/r2`, `files-sdk/gcs`, …) and the rest of your code is unchanged.

### 5. Read and write objects — AWS S3 client (alternative)

Neon speaks the S3 API directly, so you can drop down to the AWS SDK whenever you prefer the native client or already depend on it. The credentials, endpoint, and region are read from the standard AWS env chain, so the only setting you pass is `forcePathStyle: true` — **Neon requires path-style addressing, so the S3 client must set it**:

```typescript
import { S3Client } from "@aws-sdk/client-s3";

const s3 = new S3Client({
  forcePathStyle: true, // REQUIRED: Neon uses path-style addressing
});
```

If you prefer typed access instead of reading `process.env` directly, `parseEnv` (from `@neon/env`) returns a validated `env.storage` namespace (`accessKeyId`, `secretAccessKey`, `endpoint`, `region`) derived from your `neon.ts` — see the `neon` skill.

Then upload, download, and presign with the raw command objects:

```typescript
import { PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const BUCKET = "images";

// Upload
await s3.send(
  new PutObjectCommand({
    Bucket: BUCKET,
    Key: "generated/cat.jpg",
    Body: fileBuffer,
    ContentType: "image/jpeg",
  }),
);

// Download
const res = await s3.send(
  new GetObjectCommand({ Bucket: BUCKET, Key: "generated/cat.jpg" }),
);
const bytes = await res.Body?.transformToByteArray();

// Presigned GET — share without exposing credentials
const url = await getSignedUrl(
  s3,
  new GetObjectCommand({ Bucket: BUCKET, Key: "generated/cat.jpg" }),
  { expiresIn: 3600 },
);
```

### 6. Canonical pattern: pair storage with the database on a branch

The canonical pattern for pairing storage with the database on a branch:

1. An agent generates an image.
2. `PutObject` into the `images` bucket.
3. A row is inserted in Postgres.
4. A presigned URL is returned on read.

Store the bucket **key** (not the bytes) in a Postgres column, and presign on read. Because both the row and the object live on the same branch, they branch together and never drift.

### 7. CLI bucket and object commands

The `neon` CLI also has first-class bucket/object commands for scripting and one-off operations:

```powershell
neon bucket create|list|delete
neon bucket object put|get|list|delete
```

## Pitfalls

- **Region lock.** Object Storage is preview-only and only available on **new** projects in **`us-east-2`**. It cannot be enabled on existing projects or other regions. Always confirm the project qualifies before proceeding.
- **`forcePathStyle: true` is mandatory.** Neon uses path-style addressing. If you omit this from the AWS S3 client, requests will fail. The Files SDK `neon` adapter sets it for you.
- **SigV4 only.** Neon does not support other S3 auth schemes. The AWS SDK uses SigV4 by default, so this is usually a non-issue, but custom clients must implement SigV4.
- **Checking out an existing branch does not reconcile it.** `neon checkout` applies the `neon.ts` policy only when it _creates_ a branch. For an existing branch, run `neon deploy` to apply changes.
- **Credentials are branch-scoped.** A credential is valid for its branch and all descendants. If you switch branches, you must re-pull env vars (`neon env pull`) or the S3 client will use the wrong branch's credentials.
- **No live secrets in code.** Never hardcode `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY`. Always read from the injected environment or `.env.local`. Use `YOUR_KEY` placeholders in examples.
- **Don't store bytes in Postgres.** Store the bucket **key** in a Postgres column and presign on read. Storing raw bytes defeats the purpose of object storage and bloats the database.
- **Preview feature is evolving.** APIs, CLI flags, pricing, and quotas may change. Always verify against the official Neon docs before making changes. Fetch any doc page as markdown by appending `.md` to the URL or by requesting `Accept: text/markdown`.

## Verification

1. **Confirm the project is in `us-east-2`:**
   ```powershell
   neon config status
   ```
   Output should show the region as `us-east-2`.

2. **Confirm buckets are provisioned:**
   ```powershell
   neon config status
   ```
   The listed buckets should match your `neon.ts` declaration.

3. **Confirm env vars are present locally:**
   ```powershell
   Get-Content .env.local | Select-String "AWS_"
   ```
   You should see `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL_S3`, and `AWS_REGION`.

4. **Dry-run a config change before applying:**
   ```powershell
   neon config plan
   ```
   Review the diff; it should show only the intended bucket additions/changes.

5. **Test an upload/download round-trip** (Files SDK):
   ```typescript
   await files.upload("test/probe.txt", "hello");
   const file = await files.download("test/probe.txt");
   console.log(new TextDecoder().decode(await file.arrayBuffer())); // "hello"
   await files.delete("test/probe.txt");
   ```

6. **Verify against official docs** (always recommended before production changes):
   ```powershell
   Invoke-WebRequest -Uri "https://neon.com/docs/storage/overview.md" -Headers @{ "Accept" = "text/markdown" }
   ```

## Further reading

- <https://neon.com/docs/storage/overview.md>
- <https://neon.com/docs/storage/get-started.md>
- <https://neon.com/docs/storage/buckets.md>
- <https://neon.com/docs/storage/objects.md>
- <https://neon.com/docs/storage/authentication.md>
- <https://neon.com/docs/storage/s3-compatibility.md>
- <https://neon.com/docs/storage/troubleshooting.md>
- <https://files-sdk.dev> — Files SDK docs (the `neon` adapter)
- <https://neon.com/docs/llms.txt> — docs index for LLMs
- Beta sign-up: <https://neon.com/blog/were-building-backends#access>

## Related skills

- **`neon`** — Neon infrastructure-as-code (`neon.ts`), branch-first workflow (`link`/`checkout`), `parseEnv` from `@neon/env`, and the full config reference. Load this skill when the user needs to understand the `neon.ts` file, branch creation, or typed env access.

## Limitations

- Use this skill only when the task clearly matches its upstream product or API scope.
- Verify commands, API behavior, pricing, quotas, credentials, and deployment effects against current official documentation before making changes.
- Do not treat generated examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
