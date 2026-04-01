# Workflow: Search Torrents

<required_reading>
Read `references/search-intelligence.md` for quality tiers and scoring.
Read `references/categories.md` if filtering by category.
</required_reading>

<process>

**Step 1: Determine search parameters**

Extract from user request:
- **Query** — what they're looking for
- **Category** — video, audio, apps, games, ebooks, etc. (default: all)
- **Quality preference** — resolution, codec, trust level (optional)
- **Limit** — how many results to show (default: 10-20)

**Step 2: Choose the right command**

- Simple search: `tpb search "<query>" --cat <cat> --limit <n>`
- With quality filter: `tpb search "<query>" --cat video --prefer "1080p,x265,vip"`
- Agent-parseable: add `--json` flag

The `search` command enriches every result with:
- Parsed resolution, codec, source, HDR status
- Quality score (0-100) and trust score (0-100)
- Pre-built magnet link (no second API call needed)

**Step 3: Present results**

Table includes: seeders, leechers, size, quality score, resolution, category, name.

**Step 4: Offer next actions**

- Get magnet: `tpb grab "<query>"` or copy from result hash
- Open in client: `tpb open <id>`
- View files: `tpb files <id>`
- Refine search with different terms/quality/category

</process>

<success_criteria>
- Results displayed sorted by seeders (highest first)
- Quality scores and parsed metadata visible
- Preference filters applied when specified
- Torrent IDs shown for follow-up actions
</success_criteria>
