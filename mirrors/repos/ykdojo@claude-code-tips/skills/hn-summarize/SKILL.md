---
name: hn-summarize
description: Fetch and summarize Hacker News / hckrnews.com top stories, articles, and their comment threads. Use when asked to summarize HN front-page stories, a specific HN story plus its discussion, or "the top N from hckrnews".
---

# HN Summarize

`hckrnews.com` is a JavaScript-rendered front end - curling it returns an empty shell, so **do not scrape it**. Instead use the official Hacker News APIs (Firebase + Algolia), which give the same stories with points, comment counts, and full comment trees. These APIs return plain JSON, so plain `curl` works fine.

## 1. Current top stories (the "top 10")

`topstories.json` returns 500 story IDs in front-page rank order. Take the first N and look up each item.

```bash
curl -sL 'https://hacker-news.firebaseio.com/v0/topstories.json' -o /tmp/top.json
python3 -c "
import json,urllib.request
ids=json.load(open('/tmp/top.json'))[:10]
for i,sid in enumerate(ids,1):
    d=json.load(urllib.request.urlopen(f'https://hacker-news.firebaseio.com/v0/item/{sid}.json'))
    print(f\"{i}. {d.get('title')} | {d.get('score')} pts | {d.get('descendants',0)} comments | id {sid}\")
    print(f\"   {d.get('url','(text post)')}\")
"
```

## 2. Find a specific story by topic (Algolia search)

```bash
curl -sL 'https://hn.algolia.com/api/v1/search?query=YOUR+QUERY&tags=story' -o /tmp/s.json
python3 -c "
import json
for h in json.load(open('/tmp/s.json'))['hits'][:8]:
    print(h['objectID'], '|', h.get('points'), 'pts |', h.get('num_comments'), 'comments |', h['title'])
    print('   ', h.get('url'))
"
```

- Add `&numericFilters=created_at_i>UNIXTS` to restrict to recent stories (avoids matching an old duplicate of the same headline).
- `search` ranks by relevance; `search_by_date` ranks by recency.
- Pick the `objectID` with the highest points/comments - that's the live front-page discussion.

## 3. Fetch a story + its comment tree

```bash
curl -sL 'https://hn.algolia.com/api/v1/items/OBJECT_ID' -o /tmp/hn.json
```

The response is a nested tree: top-level `children` are root comments, each with their own `children`. Flatten and print root comments in thread order (HN's default ranking ≈ this order):

```bash
python3 -c "
import json,re
d=json.load(open('/tmp/hn.json'))
def clean(t):
    t=re.sub('<[^>]+>',' ',t)
    for a,b in [('&#x27;',chr(39)),('&gt;','>'),('&lt;','<'),('&amp;','&'),('&quot;','\"')]:
        t=t.replace(a,b)
    return re.sub(' +',' ',t).strip()
for c in d.get('children',[])[:15]:
    if c.get('text'):
        print(f\"{c.get('author')}: {clean(c['text'])[:550]}\")
        print('---')
"
```

Note: Algolia's per-comment `points` field is now always `null`, so sort by thread order (already roughly HN's ranking) rather than by points. For deeper threads, recurse into `children` and track depth.

## 4. Fetch the linked article

Fetch the story's article with `curl -sL <url>`, then strip tags with `sed 's/<[^>]*>//g'` to extract readable text, or grep for the key sentences. If the page is JS-heavy or paywalled, try a Wayback Machine snapshot:

```bash
curl -sL 'http://archive.org/wayback/available?url=ARTICLE_URL' -o /tmp/wb.json
python3 -c "import json;print(json.load(open('/tmp/wb.json'))['archived_snapshots'].get('closest',{}).get('url'))"
```

Then fetch the snapshot URL the same way. If the host blocks outbound `curl` requests, fetch through a container or proxy you have available.

## Summary format

For each story give: title, points, comment count, source, a few sentences on what the article says, then **comment themes** - group the discussion into 3-6 recurring threads (agreement, rebuttals, tangents) rather than listing comments one by one. Note when the top thread is a critical/contrarian take, since that's common on HN.
