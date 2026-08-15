---
name: slack
description: "Routes Slack workspace tasks: search and read channels, threads, DMs, and canvases, then hand off composition. Trigger on Slack recap, triage, search, or post intent. Never finalize outbound mrkdwn here (slack-outgoing-message) and not for channel-create, message-edit, delete, or admin APIs."
version: 1.0.1
---

## When to Use

Use this skill as the **router** for any Slack-related task. Activate it when the user mentions any of the following trigger keywords or intents:

- **Read/search:** "check Slack," "find the message in #channel," "what did they say in the thread," "search Slack for…"
- **Summarize/recap:** "summarize the #ops thread," "recap the channel," "daily digest"
- **Draft/reply:** "draft a reply," "write a Slack update," "rewrite this for Slack"
- **Send/post:** "post this in #general," "send a DM to…," "schedule a Slack message"
- **Canvas:** "create a canvas," "update the canvas"
- **Triage:** "what do I need to respond to," "triage my Slack notifications"

Read the relevant Slack context first, then hand off to the most specific Slack workflow listed under **Related Skills**.

## Prerequisites

- A connected Slack workspace accessible through the Slack tool connector.
- The current Slack app surface supports: **reading/searching** channels, users, threads, and canvases; **writing** messages, drafts, scheduled messages, and canvases.
- Unsupported actions (creating channels, editing messages, deleting messages, admin actions) must be flagged immediately—do not attempt them.
- Windows host is primary. Use PowerShell for connector and tool calls.

## Procedure

### 1. Confirm support and scope

1. Before asking the user for details, confirm the requested action is supported by the current Slack app surface.
2. If the action is **unsupported**, say so immediately and offer the closest supported path. Do not collect unnecessary details first.
3. For **broad analysis** requests (workspace-wide conclusions, "what's happening across Slack"), fail fast if the connector cannot establish reliable coverage. Do not invent channel names or imply the user is in a channel. Ask for a candidate channel list, a narrower scope, or a question answerable from specific channels, threads, profiles, or search results.

### 2. Determine intent

| User says… | Route to |
| --- | --- |
| "Send / post / reply / share / create in Slack" | Write intent—follow directly. Do **not** downgrade to a draft unless the user asked for review-first. |
| "Draft / rewrite / review-first" | Draft workflow via [../slack-outgoing-message/SKILL.md](../slack-outgoing-message/SKILL.md) |
| "Summarize / recap this channel or thread" | [../slack-channel-summarization/SKILL.md](../slack-channel-summarization/SKILL.md) |
| "Daily digest across channels" | [../slack-daily-digest/SKILL.md](../slack-daily-digest/SKILL.md) |
| "Find messages needing a reply, draft replies" | [../slack-reply-drafting/SKILL.md](../slack-reply-drafting/SKILL.md) |
| "Triage what I need to read / reply / do" | [../slack-notification-triage/SKILL.md](../slack-notification-triage/SKILL.md) |
| "Slack analysis only" (no delivery) | Return result in chat. Do not post to Slack. |

### 3. Read Slack context

1. Use `slack_read_*`, `slack_list_*`, and `slack_search_*` tools to gather the needed context (channels, threads, users, canvases).
2. **Load `references/markdown.md`** (this skill folder) immediately before composing any outgoing Slack text. It covers emphasis, lists, links, quotes, mentions, and code.
3. If the task will produce outgoing Slack text or perform a Slack write, **switch to [../slack-outgoing-message/SKILL.md](../slack-outgoing-message/SKILL.md)** before finalizing, and reread that file's `## Formatting Rules` section immediately before any send, draft, schedule, or canvas creation.

### 4. Handle DM routing

1. When the same message targets multiple specific people, first search for an **existing group DM** with the right people. Prefer the group DM over duplicate one-to-one DMs.
2. If no suitable group DM exists, do **not** silently fan out separate DMs. Ask the user whether they want individual DMs or prefer to create a group DM themselves (the connector cannot create group DMs).

### 5. Resolve write targets from fresh data

1. Before acting on a relative message target ("last message," "latest reply," "above," "that message"), **re-read** the destination channel or thread and resolve the target from fresh results.
2. Do **not** reuse earlier reads for reactions, replies, edits, or other writes.
3. If multiple channels or threads share similar topics, identify the intended destination before drafting or posting.

### 6. Execute or draft

1. For **post-ready messages**: keep them short enough to scan quickly unless the user explicitly asked for a long-form announcement.
2. For **drafts**: use the `slack-outgoing-message` skill and follow its formatting rules.
3. **Preserve** exact channel names, thread context, links, code snippets, and owners from the source conversation unless the user asked for changes.
4. **Flag high-impact targets**: @channel, @here, mass mentions, and customer-facing channels must be called out to the user **before** posting.

### 7. Format output

- Prefer a short opener, a few tight bullets, and a clear ask or next step.
- Distinguish clearly between a **private summary for the user** and a **post-ready message for Slack**.
- When summarizing a thread, lead with the **latest status**, then list blockers, decisions, and owners.
- When drafting a reply, match the tone of the channel and avoid over-formatting.

## Tool Rate Limits

Slack tools have per-minute RPM quotas **by bucket**, not by individual tool:

| Bucket | Tools |
| --- | --- |
| **Search** | `slack_search_*` |
| **Read** | `slack_read_*`, `slack_list_*`, lookup-style tools |
| **Send/Write** | message, draft, schedule, canvas creation tools |

**Backoff rules:**

1. If a Slack tool returns **429**, do **not** retry immediately and do **not** switch to an equivalent tool in the same bucket.
2. If the response includes `Retry-After` or another explicit wait hint, follow it.
3. Otherwise, wait **~30 seconds** before calling that bucket again.
4. If the same bucket returns another 429, wait **~1 minute**, then **~2 minutes** after the next 429, continuing with exponential backoff.
5. A 429 in one bucket does **not** imply other buckets are exhausted. While waiting on one bucket, continue making useful progress with other buckets when safe.
6. If the task cannot be completed without the exhausted bucket after reasonable backoff, explain the rate limit to the user and return the best partial result or next step.

## Write Safety

- **Never** silently change channel names, thread context, links, code snippets, or owners from the source.
- **Always** re-read the destination before resolving relative targets ("last message," "that thread").
- **Always** flag @channel, @here, mass mentions, and customer-facing channels before posting.
- **Never** fan out DMs to multiple people without confirming the user's preference.
- **Never** claim support for creating channels, editing messages, deleting messages, or admin actions.

## Pitfalls

- **Inventing channel names or membership:** Do not imply the user is in a channel or present workspace-wide conclusions as authoritative without verified data. Ask for a candidate list instead.
- **Stale reads for writes:** Reusing earlier read results for replies, reactions, or edits can target the wrong message. Always re-read fresh.
- **Downgrading explicit sends to drafts:** If the user said "send" or "post," do not silently switch to a draft. Respect the explicit write intent.
- **Over-formatting replies:** Match channel tone. Excessive bold, headers, or bullet lists in a casual channel feel wrong.
- **Ignoring bucket rate limits:** A 429 on `slack_search_*` does not mean `slack_read_*` is also limited, but retrying the same bucket immediately will cascade failures.
- **Missing the markdown reference:** Forgetting to load `references/markdown.md` before composing outgoing text leads to incorrect Slack formatting (e.g., wrong mention syntax, broken links).
- **Confusing private summary with post-ready message:** Always label which output is for the user's eyes only versus what is safe to paste into Slack.

## Verification

After completing the task, verify:

1. **Support check:** The action taken is within the supported surface (read, search, write message/draft/scheduled message/canvas). If unsupported, the user was told and offered an alternative.
2. **Target resolution:** Any write target was resolved from fresh read results, not stale data.
3. **DM routing:** If multiple recipients were involved, the user confirmed group DM vs. individual DMs before any fan-out.
4. **High-impact flags:** @channel, @here, mass mentions, or customer-facing channels were flagged before posting.
5. **Formatting:** Outgoing Slack text followed `references/markdown.md` and the `slack-outgoing-message` skill's `## Formatting Rules`.
6. **Rate-limit handling:** No immediate retries on 429; backoff was applied per bucket.
7. **Output clarity:** Private summaries are distinguishable from post-ready Slack messages.

**Light fallback:** If Slack messages are missing, tell the user that Slack access may be unavailable, the workspace may be disconnected, or the wrong channel/thread may be in scope. Ask them to reconnect or clarify the destination.

## Related Skills

| Workflow | Skill |
| --- | --- |
| Message composition, rewrites, drafts, canvas-writing | [../slack-outgoing-message/SKILL.md](../slack-outgoing-message/SKILL.md) |
| Bounded channel recaps and thematic summaries | [../slack-channel-summarization/SKILL.md](../slack-channel-summarization/SKILL.md) |
| Daily digests across selected channels or topics | [../slack-daily-digest/SKILL.md](../slack-daily-digest/SKILL.md) |
| Find messages needing a response and prepare reply drafts | [../slack-reply-drafting/SKILL.md](../slack-reply-drafting/SKILL.md) |
| Triage for what to read, reply to, or do next | [../slack-notification-triage/SKILL.md](../slack-notification-triage/SKILL.md) |

## Examples

- "Summarize the incident thread in #ops and draft a calm update for leadership."
- "Turn these meeting notes into a short Slack post for the team channel."
- "Read the product launch thread and draft a reply that confirms the timeline."
- "Rewrite this long update so it lands well in Slack and still keeps the important links."
- "Search #engineering for messages about the deploy failure and tell me who owns the follow-up."
- "Post a brief heads-up in #general about tomorrow's maintenance window."
