# Workflow: Browse Top / Recent Torrents

<required_reading>
Read `references/categories.md` if the user wants to filter by category.
</required_reading>

<process>

**Step 1: Determine browse mode**

- **Top 100** — most seeded torrents, optionally by category
- **Recent** — most recently uploaded torrents, paginated

**Step 2: Fetch results**

Top 100:
```bash
npx tsx <skill-dir>/scripts/tpb.ts top100 --cat <category> --limit <n>
```

Direct API:
```bash
# All categories
curl -s 'https://apibay.org/precompiled/data_top100_all.json'

# Specific category (use numeric code, e.g. 200 for video)
curl -s 'https://apibay.org/precompiled/data_top100_200.json'
```

Recent:
```bash
npx tsx <skill-dir>/scripts/tpb.ts recent --limit <n> --page <n>
```

Direct API:
```bash
curl -s 'https://apibay.org/precompiled/data_top100_recent.json'
# Page 2:
curl -s 'https://apibay.org/precompiled/data_top100_recent_2.json'
```

**Step 3: Present and offer follow-up**

Same as search workflow — show table, offer magnet/detail/files for any result.

</process>

<success_criteria>
- Results displayed sorted by seeders
- Category filter applied correctly
- Pagination works for recent torrents
</success_criteria>
