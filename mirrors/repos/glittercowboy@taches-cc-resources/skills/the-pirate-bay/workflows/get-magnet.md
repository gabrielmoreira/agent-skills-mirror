# Workflow: Get Magnet Link

<process>

**Step 1: Choose the fastest path**

- **By search query** (1 API call): `tpb grab "<query>" --cat <cat> --prefer "1080p,vip"`
- **By torrent ID** (1 API call): `tpb magnet <id>`
- **Open directly** (1 API call + launches client): `tpb open "<query>"` or `tpb open <id>`

The `grab` command builds the magnet from search results — no second API call needed. This avoids rate limiting.

**Step 2: Safety check (recommended for software/unknown uploaders)**

```bash
npx tsx <skill-dir>/scripts/tpb.ts files <torrent-id>
```

Red flags:
- `.exe` files in non-software torrents
- File count or total size doesn't match expected content
- Single `.rar` file with misleading name
- Very small files claiming to be large media

**Step 3: Present or open**

To present: show name, size, seeders, quality score, trust score, magnet link.

To open directly in the default torrent client:
```bash
npx tsx <skill-dir>/scripts/tpb.ts open <id-or-query> [--cat video] [--prefer "1080p"]
```

Works on macOS (`open`), Linux (`xdg-open`), and Windows (`start`).

</process>

<success_criteria>
- Magnet link obtained with minimal API calls (1 call preferred)
- User has enough info to decide (size, seeders, trust, quality)
- Safety red flags called out when present
- `open` command launches torrent client directly when requested
</success_criteria>
