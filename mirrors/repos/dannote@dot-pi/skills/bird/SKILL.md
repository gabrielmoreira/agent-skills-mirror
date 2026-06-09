---
name: bird
description: X/Twitter CLI for posting tweets, reading threads, searching, and fetching news. Use when user asks to tweet, reply, read tweets, search X/Twitter, get mentions, view bookmarks, likes, followers, following, user timelines, or fetch trending news/topics.
---

# bird — X/Twitter CLI

This skill targets my `@dannote/bird-premium` package, which installs a `bird` binary. It is a fork of/derived from Peter Steinberger's original `steipete/bird` CLI, but uses the documented paid X API v2 instead of undocumented web GraphQL/cookie endpoints.

- Package: `@dannote/bird-premium`
- Original project credited: `steipete/bird`
- Transport: official X API v2 with OAuth 1.0a and Bearer Token auth

## Install

```bash
# one-shot (no install)
bunx @dannote/bird-premium whoami

# or install globally
npm install -g @dannote/bird-premium
# or: pnpm add -g @dannote/bird-premium
# or: bun add -g @dannote/bird-premium
```

## Authentication

Env vars:

- **Bearer Token (app-only):** `X_BEARER_TOKEN`
- **OAuth 1.0a (user context):** `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`

Bearer Token enables: search, read, user, user-tweets, followers, following
OAuth 1.0a adds: tweet, reply, like, retweet, bookmark, follow, home, whoami, mentions

## Commands

### Post & Reply

```bash
bird tweet "Hello world"
bird tweet "Quote this" --quote <tweet-id>
bird reply <tweet-id-or-url> "Reply text"
```

### Read

```bash
bird read <tweet-id-or-url>
```

### Search

```bash
bird search "query" -n 20
```

Search covers the last 7 days.

### Mentions

```bash
bird mentions -n 5
bird mentions <username> -n 5
```

### Timelines

```bash
bird home -n 20
bird user-tweets <username> -n 20
bird user-tweets <username> --no-replies --no-retweets
bird list-timeline <list-id> -n 20
```

### Bookmarks & Likes

```bash
bird bookmarks -n 10
bird likes -n 10
bird likes <username> -n 10
bird bookmark <tweet-id>
bird unbookmark <tweet-id>
bird like <tweet-id>
bird unlike <tweet-id>
```

### Social Graph

```bash
bird followers <username> -n 20
bird following <username> -n 20
bird follow <username>
bird unfollow <username>
```

### Retweets

```bash
bird retweet <tweet-id>
bird unretweet <tweet-id>
```

### User Profile

```bash
bird user <username>
```

### Account

```bash
bird whoami
bird check
```

### Delete

```bash
bird delete <tweet-id>
```

## Global Options

| Flag               | Description            |
| ------------------ | ---------------------- |
| `--json`           | JSON output            |
| `-n, --count <n>`  | Number of results      |
| `--cursor <token>` | Resume from cursor     |

## JSON Output Schema

Tweet objects:

- `id`, `text`, `author` (`{username, name}`), `authorId`
- `createdAt`, `conversationId`, `inReplyToStatusId`
- `replyCount`, `retweetCount`, `likeCount`
- `quotedTweet` (nested)

User objects (following/followers):

- `id`, `username`, `name`, `description`
- `followersCount`, `followingCount`, `isBlueVerified`
