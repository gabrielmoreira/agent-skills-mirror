# Search Intelligence Reference

<quality_tiers>

**Video Source Quality** (best → worst):

| Source | Quality | Typical Size (1080p movie) | Notes |
|--------|---------|---------------------------|-------|
| REMUX | Perfect — bit-for-bit disc copy | 30-80 GiB | Huge. Only for archivists or home theater. |
| BluRay | Excellent — encoded from disc | 5-15 GiB | Best balance for most users. |
| WEB-DL | Great — untouched streaming rip | 2-6 GiB | Netflix/Amazon quality. No re-encoding artifacts. |
| WEB / WEBRip | Good — captured from stream | 1-4 GiB | Slight quality loss vs WEB-DL. |
| HDTV | Decent — TV broadcast capture | 1-3 GiB | Broadcast artifacts, possible logos. |
| HDRip | Okay — ripped from streaming | 1-2 GiB | Variable quality. |
| DVDRip | Legacy — DVD source | 700 MiB - 1.5 GiB | Acceptable for old content only. |
| TS / Telesync | Bad — theater audio sync | 1-2 GiB | Audio from theater, video from cam or other source. |
| CAM | Terrible — filmed in theater | 1-2 GiB | Never recommend unless explicitly asked. |

**Resolution Quality** (best → worst):
- `2160p` / 4K / UHD — 4x 1080p detail. Needs 4K display + fast connection.
- `1080p` — The sweet spot for most users. Sharp, widely compatible.
- `720p` — Good for slower connections or smaller screens.
- `480p` / SD — Only acceptable for very old content or bandwidth constraints.

**Codec Efficiency** (best → worst):
- `AV1` — Most efficient, newest. Requires modern hardware/software to decode.
- `x265` / HEVC — 50% more efficient than x264. Same quality at half the size.
- `x264` / AVC — Universal compatibility. Larger files but plays everywhere.
- `XviD` — Ancient. Only found on old uploads.

</quality_tiers>

<scoring_system>

The tool assigns two scores (0-100 each):

**Quality Score** — based on parsed torrent name:
- Resolution: 2160p=40, 1080p=30, 720p=15, 480p=5
- Source: remux=30, bluray=25, web-dl=20, web=18, webrip=15, hdtv=10, cam=1
- Codec: x265=15, av1=15, x264=10, xvid=3
- HDR bonus: +10
- REMUX bonus: +5
- Max possible: 100

**Trust Score** — based on uploader status + seeder count:
- Status: admin/mod=50, vip=40, trusted=30, helper=20, member=0
- Seeders: ≥100=40, ≥50=30, ≥20=20, ≥5=10, ≥1=5
- Max possible: ~90 (VIP + 100 seeders)

**Combined ranking**: `quality × 0.4 + trust × 0.6`
Trust is weighted higher because a well-seeded VIP upload of a 720p is better than a dead 4K upload from an unknown user.

</scoring_system>

<query_strategies>

**TV Shows:**
- Search by show name only (e.g. "1670"), let the `season` command filter episodes
- If show name is common, add year: "invincible 2021"
- If no results, try without year, or with alternative name
- The API returns max 100 results, so very popular shows may not have all seasons in one search

**Movies:**
- Search by movie title: "dark knight rises"
- Add year to disambiguate: "dark knight rises 2012"
- Use `--cat video` to avoid matching ebooks/soundtracks
- Use `smart` command — it auto-filters CAM/TS

**Software/Apps:**
- Search by exact name + version: "photoshop 2024"
- Always check file list (`files` command) — `.exe` files should be expected
- Prefer VIP uploaders heavily for software (malware risk is real)

**General:**
- If first search fails, try alternate terms
- Use category filters to reduce noise
- The `--prefer` flag applies hard filters — if too restrictive, results may be empty

</query_strategies>

<content_type_detection>

The `smart` command detects content type by analyzing results:

- **TV Show**: >30% of results contain `S##E##` patterns → show season summary
- **Movie**: Most results are single-file video → rank by quality + trust
- **Ambiguous**: Falls through to general ranked list

Known edge cases:
- Shows with numbers in the title (e.g. "1670") may match unrelated content — the season/episode filter handles this
- Anime may use different numbering (e.g. just episode numbers, no season) — `season` command may miss these
- Specials tagged as `S00E##` are grouped under season 0

</content_type_detection>

<preference_filters>

The `--prefer` flag accepts comma-separated filters. All must match (AND logic).

| Filter | What it matches |
|--------|----------------|
| `2160p`, `1080p`, `720p`, `480p` | Exact resolution |
| `x265`, `x264`, `hevc`, `av1` | Exact codec |
| `bluray`, `web-dl`, `webrip`, `web`, `remux` | Exact source |
| `hdr` | HDR content only |
| `vip` | VIP uploaders only |
| `trusted` | VIP or trusted uploaders |

Examples:
- `--prefer "1080p,x265,vip"` — 1080p HEVC from VIP only
- `--prefer "2160p,hdr"` — 4K HDR content
- `--prefer "vip"` — Any quality, but only from VIP uploaders

If the filter returns zero results, the tool falls back to unfiltered results with a warning.

</preference_filters>

<recommendations_for_agents>

When the agent is picking torrents for the user:

1. **Always prefer VIP/trusted** unless the user explicitly says otherwise
2. **For movies**: recommend the highest-scoring result, but note the size tradeoff (REMUX = huge, BluRay x265 = sweet spot)
3. **For TV seasons**: pick consistent quality across episodes (same release group if possible)
4. **Flag anomalies**: if one episode is 500 MiB and others are 2 GiB, something's off
5. **Check seeder count**: anything under 5 seeders may be slow or stall
6. **Use `--json` mode** to get structured data for programmatic reasoning
7. **Minimize API calls**: use `grab` (1 call) or `season` (1 call) over `search` + `detail` + `magnet` (3 calls) to avoid rate limits

</recommendations_for_agents>
