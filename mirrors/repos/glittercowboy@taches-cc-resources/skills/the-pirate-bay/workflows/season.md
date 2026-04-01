# Workflow: Get a TV Season

<required_reading>
Read `references/search-intelligence.md` for quality tier guidance.
</required_reading>

<process>

**Step 1: Extract parameters from user request**

- **Show name** — the TV series title
- **Season number** — which season (default: 1)
- **Quality preference** — resolution, codec, trust level (optional)

**Step 2: Run the season command**

```bash
npx tsx <skill-dir>/scripts/tpb.ts season "<show>" --s <n> [--prefer "1080p,vip"] [--json]
```

Use `--json` when you need to reason about results programmatically (e.g. check for missing episodes, compare quality scores, make recommendations).

The command:
1. Searches for the show in the video category
2. Filters to `S{nn}E{nn}` pattern matching the target season
3. Picks the **best torrent per episode** (highest combined quality + trust score)
4. Detects **season packs** (torrents with just `S{nn}` and no episode number)
5. Reports **missing episodes** if the episode range has gaps
6. Outputs all magnet links in episode order

**Step 3: Handle edge cases**

- **No results**: Try alternate show names (e.g. "1670" vs "1670 show", year suffixes)
- **Missing episodes**: Report which are missing; suggest checking with a broader search
- **Season pack available**: Note it as an alternative to individual episodes (often simpler)
- **Mixed quality**: If different episodes have different resolutions, note the inconsistency

**Step 4: Present results**

Human mode shows:
- Episode table (EP, seeders, size, quality score, status, name)
- Missing episode warnings
- Season packs if available
- All magnet links at the bottom, ready to copy

JSON mode returns structured data with per-episode magnet links, scores, and metadata.

**Step 5: Offer to open**

If the user wants to start downloading immediately:
```bash
# Open all magnets (one per episode) — each opens in the torrent client
for magnet in <magnets>; do open "$magnet"; sleep 1; done
```

</process>

<success_criteria>
- All available episodes for the season are found and listed
- Best quality torrent selected per episode (prefers VIP + high seeders + good resolution)
- Missing episodes clearly called out
- Season packs surfaced as alternatives
- Magnet links ready for bulk copy or direct opening
</success_criteria>
