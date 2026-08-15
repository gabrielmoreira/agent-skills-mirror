---
name: papers
description: "Fetches Hugging Face paper pages as markdown and the papers API for authors, linked models/datasets/spaces, GitHub, and project URLs. Use when the user shares an hf.co/papers or arXiv URL/ID or asks to summarize an AI research paper indexed there. Not for paywalled publisher PDFs or training on the paper corpus; never claim a paper is on Daily Papers just because it is indexed."
version: 1.0.1
---

# Hugging Face Paper Pages

Hugging Face Paper pages (hf.co/papers) is a platform built on top of arXiv (arxiv.org), specifically for AI and computer-science research papers. Users can submit papers at hf.co/papers/submit, which features them on the Daily Papers feed (hf.co/papers). Each day, users can upvote and comment. Each paper page allows authors to:

- Claim their paper (by clicking their name in the `authors` field). This makes the paper page appear on their Hugging Face profile.
- Link associated model checkpoints, datasets, and Spaces by including the HF paper or arXiv URL in the model card, dataset card, or Space README.
- Link the GitHub repository and/or project page URLs.
- Link the HF organization. This also makes the paper page appear on the organization page.

When someone mentions an HF paper or arXiv abstract/PDF URL in a model card, dataset card, or Space README, the paper is automatically indexed. Not all indexed papers appear in Daily Papers — that is a promotional feed. Papers can only be submitted to Daily Papers up to 14 days after their arXiv publication date.

## When to Use

Trigger this skill when any of the following apply:

- User shares a Hugging Face paper page URL (e.g. `https://huggingface.co/papers/2602.08025`)
- User shares a Hugging Face markdown paper page URL (e.g. `https://huggingface.co/papers/2602.08025.md`)
- User shares an arXiv URL (e.g. `https://arxiv.org/abs/2602.08025` or `https://arxiv.org/pdf/2602.08025`)
- User mentions an arXiv ID (e.g. `2602.08025`)
- User asks to summarize, explain, or analyze an AI research paper

## Prerequisites

- **No authentication** is required for public paper pages or read-only API endpoints.
- Write endpoints (claim authorship, index paper, update paper links) require `Authorization: Bearer $HF_TOKEN`. Use a placeholder like `YOUR_HF_TOKEN` — never embed live secrets.
- Windows host is primary. Use PowerShell-compatible `curl` (or `curl.exe`) commands. In PowerShell, prefer `curl.exe` to avoid alias conflicts with `Invoke-WebRequest`.

## Procedure

### 1. Parse the paper ID

Extract the arXiv ID from whatever the user provides:

| Input | Paper ID |
| --- | --- |
| `https://huggingface.co/papers/2602.08025` | `2602.08025` |
| `https://huggingface.co/papers/2602.08025.md` | `2602.08025` |
| `https://arxiv.org/abs/2602.08025` | `2602.08025` |
| `https://arxiv.org/pdf/2602.08025` | `2602.08025` |
| `2602.08025v1` | `2602.08025v1` |
| `2602.08025` | `2602.08025` |

Use the parsed ID in all API endpoints below.

### 2. Fetch the paper page as markdown

Prefer the `.md` endpoint for reliable machine-readable output:

```powershell
curl.exe -s "https://huggingface.co/papers/{PAPER_ID}.md"
```

This returns the HF paper page as markdown. It relies on the HTML version of the paper at `https://arxiv.org/html/{PAPER_ID}`.

Two exceptions:
- Not all arXiv papers have an HTML version. If the HTML version does not exist, the content falls back to the HTML of the Hugging Face paper page.
- If it returns a 404, the paper is not yet indexed on hf.co/papers. See [Pitfalls](#pitfalls).

Alternative — request markdown from the normal paper page URL:

```powershell
curl.exe -s -H "Accept: text/markdown" "https://huggingface.co/papers/{PAPER_ID}"
```

### 3. Get structured metadata (JSON)

Fetch the paper metadata as JSON:

```powershell
curl.exe -s "https://huggingface.co/api/papers/{PAPER_ID}"
```

Returns structured metadata that can include:

- `authors` — names and HF usernames (if claimed)
- `media` — media URLs (uploaded when submitting to Daily Papers)
- `summary` — abstract and AI-generated summary
- `project_page` and `github_repo` — linked URLs
- `organization` and engagement metadata (upvotes)

### 4. Find linked models, datasets, and spaces

Find models linked to the paper:

```powershell
curl.exe -s "https://huggingface.co/api/models?filter=arxiv:{PAPER_ID}"
```

Find datasets linked to the paper:

```powershell
curl.exe -s "https://huggingface.co/api/datasets?filter=arxiv:{PAPER_ID}"
```

Find Spaces linked to the paper:

```powershell
curl.exe -s "https://huggingface.co/api/spaces?filter=arxiv:{PAPER_ID}"
```

### 5. Get daily papers

Fetch the Daily Papers feed:

```powershell
curl.exe -s -H "Authorization: Bearer $env:HF_TOKEN" `
  "https://huggingface.co/api/daily_papers?p=0&limit=20&date=2017-07-21&sort=publishedAt"
```

Query parameters:
- `p` (integer): page number
- `limit` (integer): number of results, between 1 and 100
- `date` (string): RFC 3339 full-date, e.g. `2017-07-21`
- `week` (string): ISO week, e.g. `2024-W03`
- `month` (string): month value, e.g. `2024-01`
- `submitter` (string): filter by submitter
- `sort` (enum): `publishedAt` or `trending`

### 6. List papers

List arXiv papers sorted by published date:

```powershell
curl.exe -s -H "Authorization: Bearer $env:HF_TOKEN" `
  "https://huggingface.co/api/papers?cursor={CURSOR}&limit=20"
```

Query parameters:
- `cursor` (string): pagination cursor
- `limit` (integer): number of results, between 1 and 100

### 7. Search papers

Perform hybrid semantic and full-text search over paper title, authors, and content:

```powershell
curl.exe -s -H "Authorization: Bearer $env:HF_TOKEN" `
  "https://huggingface.co/api/papers/search?q=vision+language&limit=20"
```

Query parameters:
- `q` (string): search query, max length 250
- `limit` (integer): number of results, between 1 and 120

### 8. Index a paper (requires auth)

Insert a paper from arXiv by ID. If the paper is already indexed, only its authors can re-index it:

```powershell
curl.exe "https://huggingface.co/api/papers/index" `
  --request POST `
  --header "Content-Type: application/json" `
  --header "Authorization: Bearer $env:HF_TOKEN" `
  --data '{"arxivId": "{ARXIV_ID}"}'
```

Body:
- `arxivId` (string, required): arXiv ID to index, e.g. `2301.00001`
- Pattern: `^\d{4}\.\d{4,5}$`
- Response: empty JSON object on success

### 9. Claim paper authorship (requires auth)

Claim authorship of a paper for a Hugging Face user:

```powershell
curl.exe "https://huggingface.co/api/settings/papers/claim" `
  --request POST `
  --header "Content-Type: application/json" `
  --header "Authorization: Bearer $env:HF_TOKEN" `
  --data '{"paperId": "{PAPER_ID}", "claimAuthorId": "{AUTHOR_ENTRY_ID}", "targetUserId": "{USER_ID}"}'
```

Body:
- `paperId` (string, required): arXiv paper identifier being claimed
- `claimAuthorId` (string): author entry on the paper, 24-char hex ID
- `targetUserId` (string): HF user who should receive the claim, 24-char hex ID

### 10. Update paper links (requires auth)

Update the project page, GitHub repository, or submitting organization for a paper. The requester must be the paper author, the Daily Papers submitter, or a papers admin:

```powershell
curl.exe "https://huggingface.co/api/papers/{PAPER_OBJECT_ID}/links" `
  --request POST `
  --header "Content-Type: application/json" `
  --header "Authorization: Bearer $env:HF_TOKEN" `
  --data '{"projectPage": "https://example.com", "githubRepo": "https://github.com/org/repo", "organizationId": "{ORGANIZATION_ID}"}'
```

Path parameters:
- `paperId` (string, required): Hugging Face paper object ID (not the arXiv ID)

Body:
- `githubRepo` (string, nullable): GitHub repository URL
- `organizationId` (string, nullable): organization ID, 24-char hex ID
- `projectPage` (string, nullable): project page URL
- Response: empty JSON object on success

## Pitfalls

- **404 on `https://huggingface.co/papers/{PAPER_ID}` or `.md` endpoint**: the paper is not indexed on Hugging Face paper pages yet. Fall back to the arXiv page or PDF.
- **404 on `/api/papers/{PAPER_ID}`**: the paper may not be indexed on HF paper pages yet.
- **Paper ID not found**: verify the extracted arXiv ID, including any version suffix (e.g. `2602.08025v1`).
- **No HTML version on arXiv**: the `.md` endpoint falls back to the HF paper page HTML, which may be less detailed than the full paper.
- **PowerShell `curl` alias**: in PowerShell, `curl` is aliased to `Invoke-WebRequest` by default. Use `curl.exe` explicitly to invoke the real curl binary.
- **Write endpoints require auth**: claim authorship, index paper, and update paper links all require `Authorization: Bearer $HF_TOKEN`. Without it, you will get a 401/403.
- **Already-indexed papers**: only the paper's authors can re-index an already-indexed paper via `POST /api/papers/index`.
- **Update links uses paper object ID, not arXiv ID**: the `/api/papers/{PAPER_OBJECT_ID}/links` endpoint requires the HF internal paper object ID (24-char hex), not the arXiv ID. Retrieve it from the structured metadata endpoint first.
- **Daily Papers submission window**: papers can only be submitted to Daily Papers within 14 days of their arXiv publication date.

### Fallbacks

If the HF paper page does not contain enough detail for the user's question:

1. Check the regular paper page at `https://huggingface.co/papers/{PAPER_ID}`
2. Fall back to the arXiv page or PDF for the original source:
   - `https://arxiv.org/abs/{PAPER_ID}`
   - `https://arxiv.org/pdf/{PAPER_ID}`

## Verification

Confirm the paper ID is valid and the paper is indexed:

```powershell
curl.exe -s -o $null -w "%{http_code}" "https://huggingface.co/api/papers/2602.08025"
```

Expected output: `200` (paper is indexed). A `404` means the paper is not yet on HF paper pages.

Verify the markdown endpoint returns content:

```powershell
curl.exe -s "https://huggingface.co/papers/2602.08025.md" | Select-Object -First 5
```

Expected: first few lines of markdown content (title, authors, abstract, etc.).

Verify linked models exist:

```powershell
curl.exe -s "https://huggingface.co/api/models?filter=arxiv:2602.08025" | ConvertFrom-Json | Select-Object -First 3 modelId
```

Expected: list of model IDs linked to the paper, or an empty array if none are linked.

## Notes

- No authentication is required for public paper pages or read-only endpoints.
- Prefer the `.md` endpoint for reliable machine-readable output.
- Prefer `/api/papers/{PAPER_ID}` when you need structured JSON fields instead of page markdown.
- Use `curl.exe` in PowerShell to avoid the `Invoke-WebRequest` alias.
