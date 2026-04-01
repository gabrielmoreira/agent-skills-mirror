# Workflow: Smart Search (Auto-Detect Content Type)

<required_reading>
Read `references/search-intelligence.md` for quality tier guidance and scoring.
</required_reading>

<process>

**Step 1: Run smart search**

```bash
npx tsx <skill-dir>/scripts/tpb.ts smart "<query>" [--prefer "1080p,x265"] [--limit 10] [--json]
```

The `smart` command automatically:
1. Searches in video category first, falls back to all categories
2. **Detects TV shows** — if >30% of results have S##E## patterns, it's a TV show
3. **For TV shows**: shows available seasons, suggests `tpb season` for specific season
4. **For movies**: ranks all results by combined quality + trust score, filters out CAM/TS
5. Presents the #1 recommendation with its magnet link

**Step 2: Interpret the output**

For **movies** — the agent sees a ranked list. Key columns:
- `Score`: Combined quality (40%) + trust (60%) on 0-100 scale
- `Res`: Parsed resolution (2160p, 1080p, 720p)
- `Source`: bluray > web-dl > webrip > hdtv > cam/ts
- The `🏆 Recommended` pick is the #1 overall

For **TV shows** — the agent sees a season summary:
- How many seasons exist
- Episode count per season
- Guidance to use `tpb season` for a specific one

**Step 3: Apply user preferences**

If the user mentioned quality preferences, pass `--prefer`:
- "I want 1080p" → `--prefer "1080p"`
- "Best quality" → `--prefer "2160p"` or no filter (smart ranks by quality)
- "Small file" → sort JSON results by `size_bytes` ascending
- "VIP only" → `--prefer "vip"`

**Step 4: Present or hand off**

- For movies: show the recommendation + magnet, offer `open` command
- For TV shows: ask which season, then hand off to `season` workflow
- Always mention the quality tier of the recommendation

</process>

<success_criteria>
- Content type correctly auto-detected (movie vs TV show)
- CAM/TS quality automatically filtered for movies
- Results ranked by combined quality + trust score
- Best recommendation presented with magnet link
- User preferences applied when specified
</success_criteria>
