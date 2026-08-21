---
name: hugging-face-papers
description: Reads Hugging Face paper pages as markdown and queries the papers API for authors, linked models/datasets/spaces, GitHub, and project URLs. Use when the user shares an hf.co/papers or arXiv URL or ID, or asks to summarize an AI paper on that index. Not for keyword arXiv search (arxiv), sentence-transformers training, or model-card eval tables (hugging-face-evaluation).
version: 1.0.1
risk: unknown
source: https://github.com/huggingface/skills/tree/main/skills/huggingface-papers
source_repo: huggingface/skills
source_type: official
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/huggingface/skills/blob/main/LICENSE
---

# Hugging Face Paper Pages

Hugging Face Paper pages (hf.co/papers) is a platform built on top of arXiv (arxiv.org) for AI and computer science research papers. Users submit papers at hf.co/papers/submit, which features them on the Daily Papers feed (hf.co/papers). Each day, users upvote and comment on papers. Each paper page allows authors to:

- Claim their paper by clicking their name in the `authors` field. The paper then appears on their Hugging Face profile.
- Link associated model checkpoints, datasets, and Spaces by including the HF paper or arXiv URL in the model card, dataset card, or Space README.
- Link the GitHub repository and/or project page URLs.
- Link the HF organization. The paper page then appears on the organization page.

When someone mentions an HF paper or arXiv abstract/PDF URL in a model card, dataset card, or Space README, the paper is automatically indexed. Not all indexed papers are submitted to Daily Papers—submission is for promotion. Papers can only be submitted to Daily Papers within 14 days of their arXiv publication date.

## When to Use

- User shares a Hugging Face paper page URL (e.g. `https://huggingface.co/papers/2602.08025`)
- User shares a Hugging Face markdown paper page URL (e.g. `https://huggingface.co/papers/2602.08025.md`)
- User shares an arXiv URL (e.g. `https://arxiv.org/abs/2602.08025` or `https://arxiv.org/pdf/2602.08025`)
- User mentions an arXiv ID (e.g. `2602.08025`)
- User asks you to summarize, explain, or analyze an AI research paper

## Prerequisites

- **Network access** to `https://huggingface.co` and `https://arxiv.org`.
- **`curl`** available on the host. On Windows PowerShell, `curl` is an alias for `Invoke-WebRequest` by default; use `curl.exe` to invoke the real curl binary, or use `Invoke-RestMethod` as an alternative.
- **`HF_TOKEN`** environment variable set when calling write endpoints (claim authorship, index paper, update links). Public read endpoints require no authentication.

### Windows PowerShell notes

- Use `curl.exe` instead of `curl` to avoid the PowerShell alias for `Invoke-WebRequest`.
- For `HF_TOKEN`, set it in the current session:

  ```powershell
  $env:HF_TOKEN = "YOUR_TOKEN_HERE"
  ```

- In PowerShell, use double quotes for JSON bodies and escape inner double quotes, or use a here-string.

## Procedure

### Step 1 — Parse the paper ID

Extract the arXiv ID from whatever the user provides:

| Input | Paper ID |
| --- | --- |
| `https://huggingface.co/papers/2602.08025` | `2602.08025` |
| `https://huggingface.co/papers/2602.08025.md` | `2602.08025` |
| `https://arxiv.org/abs/2602.08025` | `2602.08025` |
| `https://arxiv.org/pdf/2602.08025` | `2602.08025` |
| `2602.08025v1` | `2602.08025v1` |
| `2602.08025` | `2602.08025` |

Use the extracted ID in any of the API endpoints below.

### Step 2 — Fetch the paper page as markdown

```powershell
curl.exe -s "https://huggingface.co/papers/2602.08025.md"
```

This returns the Hugging Face paper page as markdown. It relies on the HTML version of the paper at `https://arxiv.org/html/{PAPER_ID}`.

Two exceptions:
- Not all arXiv papers have an HTML version. If the HTML version does not exist, the content falls back to the HTML of the Hugging Face paper page.
- A 404 means the paper is not yet indexed on hf.co/papers. See [Pitfalls](#pitfalls).

Alternative request using the Accept header:

```powershell
curl.exe -s -H "Accept: text/markdown" "https://huggingface.co/papers/2602.08025"
```

### Step 3 — Fetch structured metadata (JSON)

```powershell
curl.exe -s "https://huggingface.co/api/papers/2602.08025"
```

Returns structured metadata that can include:

- Authors (names and HF usernames, if claimed)
- Media URLs (uploaded during Daily Papers submission)
- Summary (abstract) and AI-generated summary
- Project page and GitHub repository
- Organization and engagement metadata (upvote count)

### Step 4 — Find linked models, datasets, and Spaces

Find models linked to the paper:

```powershell
curl.exe -s "https://huggingface.co/api/models?filter=arxiv:2602.08025"
```

Find datasets linked to the paper:

```powershell
curl.exe -s "https://huggingface.co/api/datasets?filter=arxiv:2602.08025"
```

Find Spaces linked to the paper:

```powershell
curl.exe -s "https://huggingface.co/api/spaces?filter=arxiv:2602.08025"
```

### Step 5 — Fetch Daily Papers feed

```powershell
curl.exe -s -H "Authorization: Bearer $env:HF_TOKEN" `
  "https://huggingface.co/api/daily_papers?p=0&limit=20&date=2017-07-21&sort=publishedAt"
```

- Endpoint: `GET /api/daily_papers`
- Query parameters:
  - `p` (integer): page number
  - `limit` (integer): number of results, between 1 and 100
  - `date` (string): RFC 3339 full-date, e.g. `2017-07-21`
  - `week` (string): ISO week, e.g. `2024-W03`
  - `month` (string): month value, e.g. `2024-01`
  - `submitter` (string): filter by submitter
  - `sort` (enum): `publishedAt` or `trending`

### Step 6 — List papers (sorted by published date)

```powershell
curl.exe -s -H "Authorization: Bearer $env:HF_TOKEN" `
  "https://huggingface.co/api/papers?cursor={CURSOR}&limit=20"
```

- Endpoint: `GET /api/papers`
- Query parameters:
  - `cursor` (string): pagination cursor
  - `limit` (integer): number of results, between 1 and 100

### Step 7 — Search papers (hybrid semantic + full-text)

```powershell
curl.exe -s -H "Authorization: Bearer $env:HF_TOKEN" `
  "https://huggingface.co/api/papers/search?q=vision+language&limit=20"
```

- Endpoint: `GET /api/papers/search`
- Query parameters:
  - `q` (string): search query, max length 250
  - `limit` (integer): number of results, between 1 and 120
- Searches over paper title, authors, and content.

### Step 8 — Index a paper from arXiv

Insert a paper from arXiv by ID. If already indexed, only its authors can re-index it.

```powershell
curl.exe "https://huggingface.co/api/papers/index" `
  --request POST `
  --header "Content-Type: application/json" `
  --header "Authorization: Bearer $env:HF_TOKEN" `
  --data '{"arxivId": "2301.00001"}'
```

- Endpoint: `POST /api/papers/index`
- Body:
  - `arxivId` (string, required): arXiv ID to index, e.g. `2301.00001`
- Pattern: `^\d{4}\.\d{4,5}$`
- Response: empty JSON object on success

### Step 9 — Claim paper authorship

```powershell
curl.exe "https://huggingface.co/api/settings/papers/claim" `
  --request POST `
  --header "Content-Type: application/json" `
  --header "Authorization: Bearer $env:HF_TOKEN" `
  --data '{"paperId": "2602.08025", "claimAuthorId": "AUTHOR_ENTRY_ID", "targetUserId": "USER_ID"}'
```

- Endpoint: `POST /api/settings/papers/claim`
- Body:
  - `paperId` (string, required): arXiv paper identifier being claimed
  - `claimAuthorId` (string): author entry on the paper being claimed, 24-char hex ID
  - `targetUserId` (string): HF user who should receive the claim, 24-char hex ID
- Response: paper authorship claim result, including the claimed paper ID

### Step 10 — Update paper links

Update the project page, GitHub repository, or submitting organization. The requester must be the paper author, the Daily Papers submitter, or a papers admin.

```powershell
curl.exe "https://huggingface.co/api/papers/{PAPER_OBJECT_ID}/links" `
  --request POST `
  --header "Content-Type: application/json" `
  --header "Authorization: Bearer $env:HF_TOKEN" `
  --data '{"projectPage": "https://example.com", "githubRepo": "https://github.com/org/repo", "organizationId": "ORGANIZATION_ID"}'
```

- Endpoint: `POST /api/papers/{paperId}/links`
- Path parameters:
  - `paperId` (string, required): Hugging Face paper object ID (not the arXiv ID)
- Body:
  - `githubRepo` (string, nullable): GitHub repository URL
  - `organizationId` (string, nullable): organization ID, 24-char hex ID
  - `projectPage` (string, nullable): project page URL
- Response: empty JSON object on success

## Pitfalls

- **404 on `https://huggingface.co/papers/{PAPER_ID}` or `.md` endpoint**: the paper is not indexed on Hugging Face paper pages yet. Fall back to arXiv (`https://arxiv.org/abs/{PAPER_ID}` or `https://arxiv.org/pdf/{PAPER_ID}`).
- **404 on `/api/papers/{PAPER_ID}`**: the paper may not be indexed on Hugging Face paper pages yet.
- **Paper ID not found**: verify the extracted arXiv ID, including any version suffix (e.g. `v1`).
- **PowerShell `curl` alias**: on Windows, `curl` defaults to `Invoke-WebRequest`. Always use `curl.exe` to invoke the real curl binary, or use `Invoke-RestMethod` with equivalent parameters.
- **JSON quoting in PowerShell**: single-quoted JSON strings with `curl.exe` work reliably. If using double quotes, inner double quotes must be escaped or use a here-string.
- **Write endpoints require auth**: claim authorship, index paper, and update paper links all require `Authorization: Bearer $HF_TOKEN`. Public read endpoints do not.
- **`POST /api/papers/{paperId}/links` uses the HF paper object ID**, not the arXiv ID. Using the arXiv ID here will fail.
- **arXiv ID pattern for indexing**: must match `^\d{4}\.\d{4,5}$`. Versioned IDs (e.g. `2602.08025v1`) are not accepted by the index endpoint.
- **Not all arXiv papers have an HTML version**: the `.md` endpoint may fall back to the HF paper page HTML, which is less detailed than the arXiv HTML.
- **Daily Papers submission window**: papers can only be submitted to Daily Papers within 14 days of their arXiv publication date.

## Verification

1. **Verify a paper is indexed and fetchable as markdown**:

   ```powershell
   curl.exe -s "https://huggingface.co/papers/2602.08025.md" | Select-Object -First 20
   ```

   Expected: markdown content of the paper page. A 404 or empty response means the paper is not indexed.

2. **Verify structured metadata is available**:

   ```powershell
   curl.exe -s "https://huggingface.co/api/papers/2602.08025"
   ```

   Expected: a JSON object containing `paperId`, `title`, `authors`, `summary`, and optionally `githubRepo`, `projectPage`, and `upvotes`.

3. **Verify linked models exist**:

   ```powershell
   curl.exe -s "https://huggingface.co/api/models?filter=arxiv:2602.08025"
   ```

   Expected: a JSON array of model objects, or an empty array `[]` if none are linked.

4. **Verify search works**:

   ```powershell
   curl.exe -s -H "Authorization: Bearer $env:HF_TOKEN" "https://huggingface.co/api/papers/search?q=vision+language&limit=5"
   ```

   Expected: a JSON array of matching paper objects.

5. **Verify `curl.exe` is the real curl binary on Windows**:

   ```powershell
   curl.exe --version
   ```

   Expected: version string starting with `curl 8.x.x ...`. If this fails, install curl or use `Invoke-RestMethod` as an alternative.

## Notes

- No authentication is required for public paper pages.
- Write endpoints (claim authorship, index paper, update links) require `Authorization: Bearer $HF_TOKEN`.
- Prefer the `.md` endpoint for reliable machine-readable output.
- Prefer `/api/papers/{PAPER_ID}` when you need structured JSON fields instead of page markdown.
- If the Hugging Face paper page does not contain enough detail, fall back to:
  - `https://huggingface.co/papers/{PAPER_ID}` (regular paper page)
  - `https://arxiv.org/abs/{PAPER_ID}` (arXiv abstract)
  - `https://arxiv.org/pdf/{PAPER_ID}` (arXiv PDF)

## Limitations

- Use this skill only when the task clearly matches its upstream product or API scope.
- Verify commands, API behavior, pricing, quotas, credentials, and deployment effects against current official documentation before making changes.
- Do not treat generated examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
