---
name: pmc-official-download
description: Download PubMed/PMC literature using officially permitted PMC methods. Whenever the user wants to download PMC full text, batch-retrieve PMC Open Access Subset articles, save full text corresponding to PMID/PMCID locally, or needs to determine whether a PubMed article can be l...
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


# PMC Official Literature Download Skill

## Skill Objective

Converge "download PubMed literature" requests into a single legal, traceable PMC workflow:

- First determine whether the article can actually be obtained through official PMC channels
- Only use officially permitted PMC services
- After downloading, retain source, license, and timestamp information for future reproducibility

The core of this skill is not "get any full text as fast as possible" but rather "only obtain legally accessible PMC content through officially permitted methods."

## Trigger Scenarios

Use this skill first when the user has requests like:

- "Help me download this PubMed article"
- "Save the PMC full text corresponding to this PMID/PMCID"
- "Batch download PMC Open Access Subset"
- "Only use official methods to download articles from PMC"
- "Help me determine if this article can be legally downloaded from PMC"

If the user mentions Sci-Hub, mirror sites, bulk web scraping, bypassing restrictions, or similar approaches, refuse those paths directly and explain feasible alternatives using official PMC methods.

## Permitted Official Channels

Only use the following official PMC channels:

- `PMC Cloud Service`
- `PMC FTP Service`
- `PMC OAI-PMH Service`
- `PMC OA Web Service`
- `E-utilities`
- `BioC API`

These are services explicitly permitted by PMC for automated retrieval or downloading. Do not use any other automated scraping methods.

## Workflow

### Step 1: Confirm What the User Actually Needs

First confirm three things:

- Whether the input is a `PMID`, `PMCID`, `DOI`, or title keywords
- Whether the user wants a single full-text article, batch download, or just metadata
- Whether the target format is `XML`, `JSON`, plain text, or `PDF`

If the user only provides a `PMID`, first map it to a `PMCID`, because whether it can be legally downloaded from PMC depends on whether the article exists in the PMC accessible collection.

### Step 2: Determine Whether Legal Download is Possible

First determine whether the article belongs to a PMC accessible collection:

- `PMC Open Access Subset`
- `PMC Author Manuscript Collection`

If not in these collections, do not attempt to bypass restrictions or look for unofficial sites.

State directly:

- This article cannot be obtained through official PMC full-text download channels
- If the user needs it, I can help them use the abstract, citation information instead, or look for other legally public sources

### Step 3: Select the Official Method

Choose the most appropriate official channel by scenario:

- For single full-text articles, prefer machine-readable content via `BioC API`
- When retrieving `XML/JSON` by `PMID` or `PMCID`, prefer `BioC API`
- When batch-syncing a local mirror, prefer `PMC OA Web Service` or `PMC Cloud Service`
- For more general retrieval, location, and record-keeping, use `E-utilities`
- For batch metadata harvesting, use `OAI-PMH`
- When article packages, `XML`, `PDF`, media files, or supplementary materials are needed, prefer `PMC FTP Service` or `PMC Cloud Service`

Notes:

- Only download `PDF` when it is explicitly provided in the official article package
- Do not scrape publisher web pages or third-party hosting pages to obtain `PDF`
- If the current article package does not contain a `PDF`, inform the user honestly

### Step 4: Leave an Audit Trail When Saving Locally

When downloading, save the following information whenever possible:

- Original identifier
- Source service name
- Download timestamp
- License/collection information
- Local file path

Recommended output directory:

```text
pmc-downloads/<identifier>/
```

If writing JSON metadata, use UTF-8 encoding and preserve original Chinese text — do not force-escape Chinese characters.

## Recommended Single-Article Download Method

If the user wants full text for a single `PMID` / `PMCID` and accepts `XML` or `JSON`, prefer the helper script bundled with this skill:

```text
python scripts/download_pmc_bioc.py
```

This script only uses the official PMC `BioC API` and is suitable for downloading the machine-readable version of a single publicly accessible full-text article.

## Recommended Batch Download Method

If the user wants to batch-pull PMC public collections, follow these principles:

- Prefer using `Cloud Service`, `FTP Service`, or `OA Web Service` from the official PMC dataset page
- Do not hardcode old download paths
- If the official page indicates download location or service migration, defer to the current PMC documentation

## Output Format

When answering the user, include the following information whenever possible:

- Whether this article can be downloaded through official PMC channels
- Which official service was used
- The downloaded file type
- File save location
- If download is not possible, provide a clear reason

## Prohibited Actions

- Using unofficial mirrors, piracy sites, or third-party full-text repositories is prohibited
- Bulk web scraping of PMC page content is prohibited
- Bypassing license restrictions is prohibited
- Treating "can access the web page" as equivalent to "can automate batch downloads" is prohibited

## Failure Handling

If an official channel does not return content, troubleshoot in the following order:

1. Check if the identifier is incorrect
2. Check if the article is not in the PMC accessible collection at all
3. Check if the target format is not supported by that service
4. Check if the current article has license restrictions

If still failing, honestly inform the user of the reason it cannot be downloaded and provide official alternative paths.

## Practical Pitfalls

These are the most common gotchas with this skill — pay special attention when handling:

- The `citation_pdf_url` on article pages is often just a PDF viewer page, not necessarily a directly saveable binary PDF
- Before actually downloading, first use `PMC OA Web Service` to verify whether the `PMCID` is open, then get the official `pdf` link
- Official `ftp://ftp.ncbi.nlm.nih.gov/...` links can usually be changed to `https://ftp.ncbi.nlm.nih.gov/...`, which is more stable in local environments
- After downloading, always check if the file header starts with `%PDF` to avoid saving HTML as PDF by mistake
- Even if a title looks like "recent 3-year OA literature," it may not actually be in PMC's Open Access collection — do not judge downloadability by title alone
- For `PMID`, do not assume it can directly download full text — first map to `PMCID`, then determine downloadability

## Command Line Usage

Prefer the unified entry point — do not rely on modifying constants at the top of scripts, and do not make yourself remember two script names:

```bash
python scripts/download_pmc.py --pmcid PMC13011518 --pmcid PMC11656652 --pmcid PMC11787101
python scripts/download_pmc.py --identifier PMC11787101
```

If the user has already provided a set of `PMCID`s, `PMID`s, or download directory, pass them directly to `download_pmc.py` rather than temporarily modifying code. Only fall back to the underlying scripts when you explicitly need to debug BioC or PDF details separately.

## When to Use

- Use this skill when the user explicitly needs to perform the core task of pmc-official-download and has provided the minimum executable input.
- Use this skill when you need a structured deliverable rather than general advice.
- Use this skill when the current task can be completed using this skill's bundled scripts, templates, or reference materials.

## When Not to Use

- Do not proceed when required input files, identifiers, parameters, or context are missing — ask the user to provide them first.
- Do not assume capabilities beyond this skill's declared scope when the user requests external operations or inferences.
- Do not proceed without user confirmation when overwriting existing results, executing high-cost batch operations, or expanding task scope.

## Required Inputs

| Field | Required | Format/Source | Example | If Missing |
|---|---|---|---|---|
| User task description | Yes | Text | Research question, writing goal, analysis objective | Stop and ask user to provide |
| Primary input material | Depends on task | Text, file path, ID, table, or literature | PMID, PDF, CSV, DOCX, keywords, etc. | Specify which material type is missing |
| Output preference | No | Text | Language, format, target journal, template | Use skill default format |

## Output Contract

- Primary output: Structured result or target file aligned with this skill's objective.
- Optional output: Intermediate check notes, issue list, supplementary suggestions, or generated file paths.
- Format requirement: Unless the user specifies otherwise, prefer stable, reviewable Markdown or JSON; if the skill's bundled script requires a fixed format, use that format.
- If partially complete: Must explicitly mark as PARTIAL and state which steps are completed and which remain.

## Failure Handling

- Missing critical input: Explicitly state which fields, files, or identifiers are missing and pause.
- Script, template, or resource execution failure: Report the failing step, likely cause, and recovery suggestions — do not silently degrade.
- Partial completion only: Return the verified portion first, then list remaining blockers and suggested next steps.

## User Checkpoints

- Before executing batch processing, overwriting files, long-running searches, or multi-stage generation, confirm scope and output format with the user.
- Before proceeding when a key judgment is ambiguous, evidence is insufficient, or the workflow is entering the next stage, confirm with the user.


## Input Validation

This skill accepts requests that match the documented purpose of `pmc-official-download` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `pmc-official-download` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Quick Validation

- Check that key scripts, templates, or reference file paths this skill depends on exist.
- Check that the final output contains the core fields, sections, or files specified for this task.
- Check that results clearly mark assumptions, limitations, and incomplete items.
