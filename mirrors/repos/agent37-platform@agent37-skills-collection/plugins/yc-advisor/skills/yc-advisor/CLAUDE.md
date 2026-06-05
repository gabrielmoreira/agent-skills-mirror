# YC Advisor Skill - Developer Guide

This document explains how the YC Advisor skill was built, how to maintain it, and how to add new content.

## Overview

The YC Advisor skill provides access to Y Combinator's library of startup resources (~448 articles, videos, podcasts). It uses a **tiered retrieval system** to efficiently navigate large amounts of content.

## Directory Structure

```
yc-advisor/
├── SKILL.md              # Skill definition (instructions for Claude)
├── CLAUDE.md             # This file (developer documentation)
├── .gitignore            # Excludes runtime files
├── references/           # All content files
│   ├── *.md              # 448 reference files (essays, transcripts)
│   ├── index.yaml        # Structured metadata for all resources
│   ├── quick-index.md    # Lightweight discovery index (~500 lines)
│   ├── summaries.md      # Detailed summaries (~4300 lines)
│   ├── learning-paths.md # Curated resource sequences
│   └── frameworks/       # Decision frameworks
│       ├── should-i-start-a-startup.md
│       ├── solo-vs-cofounder.md
│       └── ...
└── scripts/              # Maintenance scripts
    ├── generate_index.py
    ├── generate_quick_index.py
    ├── generate_summaries.py
    ├── add_cross_references.py
    ├── fetch_transcripts.py
    ├── merge_resources.py
    └── transcript_manager.py
```

## How the Data Was Created

### Initial Data Collection (Manual/Offline Process)

The original data was scraped from ycombinator.com/library using an external process. This produced markdown files with:
- Title, Author, Type, URL
- YouTube ID (for videos)
- Full content (essays) or stub placeholders (videos without transcripts)

**Important:** There is no automated script to discover NEW YC Library content. The initial scrape was done offline and the results were placed in a folder (e.g., `/Users/.../Downloads/yc_library_final`).

### Merging New Scrapes

`merge_resources.py` merges a new scrape into the existing skill:

```bash
# From the scripts/ directory
python merge_resources.py --dry-run  # Preview changes
python merge_resources.py            # Apply changes (creates backup)
```

This script:
1. Compares new scrape with existing references
2. Replaces overlapping files with new content
3. Keeps current-only files (frameworks, custom content)
4. Adds new-only files
5. Normalizes format (`**Source:**` → `**URL:**`, etc.)

**Note:** You must manually update `NEW_DIR` path in the script to point to your new scrape location.

### Fetching YouTube Transcripts

Many video files are "stubs" with just metadata. Two scripts fetch transcripts:

**Option 1: Simple batch fetch**
```bash
pip install youtube-transcript-api
python fetch_transcripts.py --dry-run  # See what needs transcripts
python fetch_transcripts.py --limit 10 # Fetch first 10
python fetch_transcripts.py            # Fetch all
```

**Option 2: Robust cron-friendly fetch**
```bash
python transcript_manager.py --status  # Check current status
python transcript_manager.py --batch 15  # Process 15 videos
python transcript_manager.py --reset   # Reset rate-limited for retry
```

The transcript manager:
- Tracks status per video (pending, success, no_transcript, rate_limited)
- Handles rate limiting gracefully
- Can run as a cron job: `*/30 * * * * cd /path/to/scripts && python transcript_manager.py --batch 15`

### Regenerating Indexes

After adding/modifying content, regenerate the index files:

```bash
# Run in order (each depends on the previous)
python generate_index.py         # Creates index.yaml from .md files
python generate_quick_index.py   # Creates quick-index.md + adds line counts
python generate_summaries.py     # Creates summaries.md
python add_cross_references.py   # Adds related resources to index.yaml
```

## Reference File Format

Each reference file follows this structure:

```markdown
# [Title]

**Author:** [Author Name]
**Type:** [Essay|Video|Podcast]
**URL:** https://www.ycombinator.com/library/[CODE]-[slug]
**YouTube ID:** [optional, for videos]

---

[Full content here - essay text or video transcript]
```

File naming: `[CODE]-[descriptive-slug].md`
- The CODE (e.g., `8z`, `JW`) is YC's library ID from the URL
- Example: `8z-how-to-get-startup-ideas.md`

## Adding New Content Manually

To add a single new resource:

1. Create a new file in `references/` with the format above
2. Use the YC Library URL code as the filename prefix
3. Run the index regeneration scripts

## What's NOT Automated

1. **Discovery of new YC Library content** - No script scrapes ycombinator.com/library for new entries
2. **Creating stub files** - Must be done manually or via external scraping process
3. **Updating learning-paths.md** - Curated manually
4. **Updating frameworks/** - Curated manually

## Scripts Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `merge_resources.py` | Merge new scrape into skill | After external scraping |
| `fetch_transcripts.py` | Simple transcript fetch | One-time bulk fetch |
| `transcript_manager.py` | Robust transcript fetch with tracking | Ongoing/cron use |
| `generate_index.py` | Generate index.yaml | After any content change |
| `generate_quick_index.py` | Generate quick-index.md | After index.yaml changes |
| `generate_summaries.py` | Generate summaries.md | After content changes |
| `add_cross_references.py` | Add related resources | After index.yaml changes |

## Runtime Files (Not Checked In)

These files are generated at runtime and excluded via `.gitignore`:

- `scripts/*.log` - Log files from transcript fetching
- `scripts/transcript_status.json` - Tracks transcript fetch status
- `scripts/failed_transcripts.txt` - List of failed transcript fetches
- `references_backup_*/` - Backups created by merge script
- `*.zip` - Archive files

## Future Improvements

To fully automate adding new YC content, you would need:

1. A scraper that discovers new entries from ycombinator.com/library
2. Creates stub files with metadata and YouTube IDs
3. Then runs the existing transcript and index scripts

This would require:
- Scraping the YC Library listing pages
- Extracting metadata (title, author, type, URL, YouTube ID)
- Creating stub markdown files
- Running `transcript_manager.py` to fill in transcripts
- Running the index generation scripts
