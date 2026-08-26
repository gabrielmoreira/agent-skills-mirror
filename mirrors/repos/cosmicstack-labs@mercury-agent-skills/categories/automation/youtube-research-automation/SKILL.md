---
name: youtube-research-automation
description: 'Design agent workflows that pull YouTube transcripts, search videos and channels, and monitor new uploads without Google API quotas or OAuth setup'
metadata:
  author: therohitdas
  version: 1.0.0
  category: automation
  tags:
    - youtube
    - transcripts
    - video-search
    - channel-monitoring
    - research
    - agent-tools
    - openclaw
    - hermes-agent
---

# YouTube Research Automation

Use this skill when an agent needs to read what was said in a video, find videos
or channels on a topic, walk a channel or playlist, or watch a channel for new
uploads, and you want that to run as a repeatable workflow rather than a manual
copy and paste.

Recommended implementation:

- [youtube-skills](https://github.com/ZeroPointRepo/youtube-skills) for any
  runtime that supports the Agent Skills format. It ships twelve skills, and
  `youtube-full` covers transcripts, video and channel search, channel browsing,
  and playlist extraction in one install.
- [youtube-mcp](https://github.com/ZeroPointRepo/youtube-mcp) when the runtime
  speaks MCP instead of skills. Same tools, remote endpoint, API key or OAuth.

Both call [TranscriptAPI](https://transcriptapi.com), an independent REST API for
YouTube content. It is not affiliated with YouTube or Google, and it is not the
official YouTube Data API. That is the point of using it here: no Google Cloud
project, no OAuth consent screen, and no daily quota unit accounting.

## When to Use

Use this skill when the user asks for:

- The transcript, captions, or subtitles of a video, or a summary of one.
- Quotes, claims, timestamps, or numbers taken from a talk, lecture, or review.
- Videos or channels about a topic, without a browser in the loop.
- Every video on a channel, or a channel's recent uploads.
- Every video in a playlist, with titles and IDs.
- A recurring job that checks a channel and reports what is new.
- Research where video is fresher or more specific than written sources.

Do not use this skill for:

- Downloading or re-hosting video or audio files. This is a text and metadata
  workflow, and republishing someone's content is a licensing question, not a
  technical one.
- Uploading, commenting, account management, or anything that writes to YouTube.
- Videos with no captions. There is no transcript to fetch, so plan a fallback.
- Private or unlisted content the user does not own.

## Core Model

Treat every YouTube workflow as three stages, and keep them separate:

1. Resolve: turn whatever the user pasted, a URL, a video ID, an `@handle`, or a
   playlist link, into a stable identifier.
2. Discover: search, list a channel, or list a playlist to get a candidate set.
3. Read: fetch transcripts only for the candidates that survived filtering.

The reason to split stages 2 and 3 is cost. Discovery returns dozens of videos
for one call. Reading is priced per video. An agent that fetches a transcript for
every search hit burns the user's balance on videos nobody asked about.

## Setup

One environment variable, one header convention.

```bash
export TRANSCRIPT_API_KEY="sk_..."   # free key at https://transcriptapi.com, 100 credits, no card
```

```bash
curl "https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_ID&format=text" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: YourAgent/1.0"
```

Send a real `User-Agent`. A missing or default agent string gets a 403 with
Cloudflare error 1010, and that failure looks like a bad key if you are not
expecting it.

Skills install:

```bash
npx skills add ZeroPointRepo/youtube-skills --skill youtube-full
```

MCP install, for runtimes that prefer a server:

```bash
claude mcp add --transport http transcript-api https://transcriptapi.com/mcp
```

## Endpoints Worth Knowing

Base URL `https://transcriptapi.com/api/v2`.

| Endpoint | Use | Cost |
|---|---|---|
| `/youtube/transcript` | Transcript of one video, `format=json` or `text` | 1 credit |
| `/youtube/search` | Find videos or channels, `type=video` or `channel` | 1 credit |
| `/youtube/channel/resolve` | `@handle` or URL to channel ID | free |
| `/youtube/channel/latest` | 15 most recent uploads with view counts and timestamps | free |
| `/youtube/channel/videos` | Full channel walk, 100 per page, continuation token | 1 credit per page |
| `/youtube/channel/search` | Search inside one channel | 1 credit |
| `/youtube/playlist/videos` | Playlist contents, paginated | 1 credit per page |

Channel endpoints accept an `@handle`, a channel URL, or a `UC...` ID directly,
so resolving first is optional. Full schema lives at
`https://transcriptapi.com/openapi.json`.

## Workflow: Topic Research

```bash
# 1. Discover. One credit, up to 50 results.
curl "https://transcriptapi.com/api/v2/youtube/search?q=protein+folding+explained&type=video&limit=20" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" -H "User-Agent: YourAgent/1.0"

# 2. Filter in the agent, not in the API. Drop by channel, age, duration, title.

# 3. Read only the survivors. One credit each.
curl "https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_ID&format=text&include_timestamp=true&send_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" -H "User-Agent: YourAgent/1.0"
```

Keep `include_timestamp=true` when the output will be quoted. A claim with a
timestamp can be checked by a human in ten seconds; a claim without one cannot.
Keep `send_metadata=true` so the title and channel travel with the text and the
summary can attribute correctly.

## Workflow: Channel Monitoring

```bash
# Free. Poll this on a schedule and diff against what you stored last run.
curl "https://transcriptapi.com/api/v2/youtube/channel/latest?channel=@NASA" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" -H "User-Agent: YourAgent/1.0"
```

Store the video IDs you have already handled. Fetch transcripts only for IDs that
are new. Because the polling call is free, the cost of a monitor is exactly the
number of new videos it actually reads, which makes an hourly job affordable.

## Cost Discipline

- Search once, read many times only if the user asked for depth.
- Prefer `channel/latest` over `channel/videos` when recency is enough. One is
  free, the other is a paginated walk.
- Cache transcripts by video ID. A transcript does not change.
- Cap fan-out. Ten transcripts for a research question is generous; a hundred is
  a runaway loop with a bill attached.
- Free tier is 100 credits with no card, so a first run should be designed to fit
  inside that and still produce something useful.

## Evaluation Rubric

Score a YouTube workflow out of 10, two points each:

1. Resolution: does it accept a URL, a bare ID, and an `@handle` without asking
   the user to reformat?
2. Cost shape: does it filter before reading, and is the worst-case credit spend
   bounded and stated?
3. Attribution: does every extracted claim carry a video title and a timestamp?
4. Failure handling: are 401, 402, 403 with code 1010, 404 with no captions, and
   429 handled distinctly, or all swallowed as "failed"?
5. Idempotence: can the workflow run twice without doing the same paid work
   twice?

Below 6 means the workflow will either misattribute a quote or burn credits on a
retry. Fix those two first.

## Common Mistakes

- Fetching a transcript for every search result. This is the expensive mistake
  and it is the most common one.
- Omitting the `User-Agent` header, then debugging the 403 as an auth problem.
- Treating a 404 as an outage. It usually means the video has no captions, and
  the right response is to move to the next candidate.
- Retrying a 402 in a loop. The balance is empty; report it and stop.
- Summarizing a transcript without keeping timestamps, which makes every quote
  unverifiable.
- Assuming a channel walk is ordered by views. It is not, so sort in the agent.
- Reaching for yt-dlp or a headless browser first. Both are blocked or throttled
  from most cloud IP ranges, which is the failure this workflow avoids.

## Output Expectations

When this skill runs, the answer should include:

- What was read, as titles with links, not bare video IDs.
- Timestamps for any quoted or paraphrased claim.
- The candidate set that was considered and why the rest were dropped.
- Credits spent, or an estimate, when the run was larger than a few videos.
- An explicit note when a video was skipped because it had no captions, so the
  gap is visible rather than silently missing.
