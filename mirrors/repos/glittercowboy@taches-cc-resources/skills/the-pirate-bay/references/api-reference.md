# API Reference: apibay.org

<overview>
The Pirate Bay's public JSON API. No auth required. The `thepiratebay.org` website is a thin JavaScript frontend that calls this API from the browser.

Base URL: `https://apibay.org`

**Rate limiting:** The API returns `429 Too Many Requests` if called too rapidly. The cooldown is IP-based and can last several minutes. Avoid rapid consecutive calls — batch your needs (search → pick result → get magnet in one `detail` call rather than separate calls). The `detail` endpoint returns all info needed to construct a magnet link.
</overview>

<endpoints>

**Search: `GET /q.php`**

| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Search query (required). Also accepts `user:<username>` and `category:<code>` prefixes |
| `cat` | string | Category code filter. `0` = all. See categories.md |

Response: Array of torrent objects (max 100), sorted by seeders descending.

No-results response: Single object with `id: "0"`, `info_hash: "0000000000000000000000000000000000000000"`.

```json
[{
  "id": "74529374",
  "name": "Example Torrent Name",
  "info_hash": "7D67FDA84CF144CFB643395DCC1768FDCF6B7046",
  "leechers": "2",
  "seeders": "116",
  "size": "2198308",
  "num_files": "3",
  "username": "spy1984",
  "added": "1707094666",
  "status": "vip",
  "category": "601",
  "imdb": ""
}]
```

---

**Torrent Detail: `GET /t.php`**

| Param | Type | Description |
|-------|------|-------------|
| `id` | string | Torrent ID (required) |

Response: Single torrent object with additional fields: `descr` (description text), `language`, `textlanguage`.

---

**File List: `GET /f.php`**

| Param | Type | Description |
|-------|------|-------------|
| `id` | string | Torrent ID (required) |

Response: Array of file objects.

```json
[
  { "name": ["filename.ext"], "size": [2198110] },
  { "name": ["another.txt"], "size": [56] }
]
```

Note: `name` and `size` are wrapped in arrays (quirk of the API).

---

**Top 100: `GET /precompiled/data_top100_{slug}.json`**

Slugs: `all`, or numeric category codes (`100`, `200`, `300`, `400`, `500`, `600`).
Also subcategories: `207` (HD Movies), `208` (HD TV), etc.

Response: Array of 100 torrent objects. **Fields are numbers, not strings** (unlike search results).

---

**Recent: `GET /precompiled/data_top100_recent.json`**

Paginated: `data_top100_recent_2.json`, `data_top100_recent_3.json`, etc.

Response: Array of ~50 recently uploaded torrents.

</endpoints>

<uploader_status>

| Status | Badge | Meaning |
|--------|-------|---------|
| `vip` | 🟢 | Verified long-term uploader — high trust |
| `trusted` | 🟡 | Community-trusted uploader |
| `helper` | 🔵 | Site helper |
| `moderator` / `supermod` / `admin` | ⭐ | Site staff |
| `member` | — | Regular user — verify content carefully |

</uploader_status>

<magnet_link_construction>

Magnet links are assembled client-side. Formula:

```
magnet:?xt=urn:btih:<INFO_HASH>&dn=<URL_ENCODED_NAME><TRACKER_LIST>
```

Tracker list (append as `&tr=<encoded_tracker>` for each):

```
udp://tracker.opentrackr.org:1337
udp://open.stealth.si:80/announce
udp://tracker.torrent.eu.org:451/announce
udp://tracker.bittor.pw:1337/announce
udp://public.popcorn-tracker.org:6969/announce
udp://tracker.dler.org:6969/announce
udp://exodus.desync.com:6969
udp://open.demonii.com:1337/announce
udp://glotorrents.pw:6969/announce
udp://tracker.coppersurfer.tk:6969
udp://torrent.gresille.org:80/announce
udp://p4p.arenabg.com:1337
udp://tracker.internetwarriors.net:1337
```

</magnet_link_construction>

<special_queries>

```
# Search by user
q=user:spy1984

# Browse category
q=category:601

# Top 100 (via search endpoint)
q=top100:all
q=top100:200
q=top100:recent
```

</special_queries>
