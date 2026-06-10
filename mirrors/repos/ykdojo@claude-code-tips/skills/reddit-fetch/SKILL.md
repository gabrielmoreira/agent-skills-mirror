---
name: reddit-fetch
description: Fetch content from Reddit using the curl JSON API. Use when accessing Reddit URLs, researching topics on Reddit, or when Reddit returns 403/blocked errors.
---

# Reddit Fetch

Reddit's public JSON API works by appending `.json` to any Reddit URL.

## Listing hot/new/top posts

```bash
curl -s -L -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "https://old.reddit.com/r/SUBREDDIT/hot.json?limit=15"
```

Replace `hot` with `new`, `top`, or `rising` as needed. For `top`, add `&t=day` (or `week`, `month`, `year`, `all`).

## Fetching a specific post + comments

```bash
curl -s -L -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "https://old.reddit.com/r/SUBREDDIT/comments/POST_ID.json?limit=20"
```

The response is a JSON array: `[0]` is the post, `[1]` is the comment tree.

## Searching within a subreddit

```bash
curl -s -L -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "https://old.reddit.com/r/SUBREDDIT/search.json?q=QUERY&restrict_sr=on&sort=new&limit=15"
```

## Parsing the JSON

Use jq to extract what you need:

```bash
# List posts
curl -s -L -o /tmp/reddit_result.txt -w "%{http_code}" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  'https://old.reddit.com/r/SUBREDDIT/hot.json?limit=15'

jq -r '.data.children[] | .data | "\(.title)\n   \(.score) pts | \(.num_comments) comments | u/\(.author) | id: \(.id)\n"' /tmp/reddit_result.txt

# List comments from a specific post (the [1] element has comments)
jq -r '.[1].data.children[] | select(.kind == "t1") | .data | "u/\(.author) (\(.score) pts):\n  \(.body[:300])\n"' /tmp/reddit_thread.txt
```

Key details:
- Fetch to temp file first, then parse - avoids pipe-related encoding issues
- `-o /tmp/file` and `-w "%{http_code}"` saves the response and prints the HTTP status (useful for debugging empty responses)
- `-L` follows redirects (old.reddit.com sometimes redirects)
- Single-quoted URL avoids shell interpretation of `&` in query strings
- `.body[:300]` truncates long comment bodies (jq 1.7+)

## Rate limiting

Reddit's JSON API rate-limits aggressively:

- **Don't fire parallel requests.** Make them sequentially with `sleep 2` or `sleep 3` between each.
- If a request returns empty (0 bytes), wait 3-5 seconds and retry.
- If you get HTTP 429, back off for 10-15 seconds.
- A good pattern: fetch one search result listing, parse it, then fetch individual threads one at a time with delays.
