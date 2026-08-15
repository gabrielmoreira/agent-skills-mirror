---
name: slack-outgoing-message
description: "Composes and delivers Slack-bound text through slack_send_message, slack_send_message_draft, slack_schedule_message, or slack_create_canvas, including ID mentions and draft_already_exists stops. Use when the user asks to send, post, reply, draft, schedule, or create a Slack canvas. Not for read-only search, channel recap, or notification triage (slack)."
version: 1.0.1
---

# Slack Outgoing Message

## Overview

Use this skill whenever the task involves producing final Slack text for a send, draft, scheduled message, or canvas. If another Slack skill is used to read or summarize source context, switch to this skill before finalizing outgoing text.

Use `slack` to read or analyze Slack context; use this skill to produce the final outgoing message.

## When to Use

- The user asks to **send, post, reply, share, or create** something in Slack.
- The user asks for a **draft** or review-first workflow before sending.
- The user asks to **schedule** a message for future delivery.
- The user asks to create a **canvas** or doc in Slack.
- You are refining or formatting Slack-bound text that will be delivered via a Slack write tool.

Do **not** use this skill for read-only Slack tasks (searching, summarizing, reading channel history). Use the generic `slack` skill for those.

## Prerequisites

- A Slack connector/runtime that exposes `slack_send_message`, `slack_send_message_draft`, `slack_create_canvas`, and/or `slack_schedule_message`.
- Sufficient context to identify the destination: channel name/ID, thread timestamp, DM recipient, or group DM participants.
- Before finalizing any outgoing Slack text, follow this file's **Formatting Rules** and Slack's mrkdwn mention contract (https://api.slack.com/reference/surfaces/formatting).

## Procedure

1. **Identify the intended destination** before drafting.
   - Channel (public or private), thread reply, 1:1 DM, or group DM.
   - If the destination is unclear, ask the user before writing.

2. **Determine the execution mode** from the user's request:
   - Explicit **send / post / reply / share** → use the direct write action (`slack_send_message`).
   - Explicit **draft / review-first / later manual send** → use `slack_send_message_draft`.
   - Explicit **future delivery** or the user supplied a send time → use `slack_schedule_message`.
   - Explicit **canvas / doc** request → use `slack_create_canvas`.

3. **Apply Slack formatting** before authoring:
   - Follow **Formatting Rules** in this file plus the live Slack tool contract: emphasis, lists, links, code, and ID mentions (`<@U…>`, `<#C…>`).
   - Author the message body to that contract. Official mrkdwn: https://api.slack.com/reference/surfaces/formatting

4. **Resolve mentions before writing** (when the message should tag a person or group):
   - Resolve **user mentions** and use Slack syntax: `<@U123456>`.
   - Resolve **Slack user groups** only when the runtime exposes a way to do so, and use syntax: `<!subteam^S123456>`.
   - Do **not** rely on bare `@name` text in outgoing Slack messages.
   - If you cannot resolve the correct user or group, tell the user and compose the message without implying the mention will notify them.

5. **Draft the message body**:
   - Prefer a short opener, a few tight bullets, and a clear ask or next step.
   - Preserve source links, code, owners, dates, and commitments unless the user explicitly asked for edits.
   - Do not invent approvals, decisions, or follow-through.

6. **Execute the appropriate tool call**:
   - For a direct send: call `slack_send_message` with the resolved destination and message text.
   - For a draft: call `slack_send_message_draft`.
   - For scheduled delivery: call `slack_schedule_message` with the requested send time.
   - For a canvas: call `slack_create_canvas`.

7. **Report the result** to the user:
   - Confirm what was sent, drafted, scheduled, or created.
   - If a draft was created, remind the user it is attached and pending their review/send.
   - If a tool returned an error, surface it verbatim and stop.

## Intent Rules

- If the user explicitly asks to **send, post, reply, share, or create** something in Slack, perform that write action directly. Do not create a draft or ask for approval only because the message text is being generated during the turn.
- Use a **draft** only when the user explicitly asks for a draft, review-first workflow, or later/manual send.
- If the destination, wording, or requested action is unclear, **clarify before writing**.
- If the user asks for an unsupported Slack write action, **say so immediately** and offer the closest supported path instead of drafting something unrelated.

## Tool Guardrails

- Treat optional Slack tool parameters as **absent-by-default**. Only include a parameter when you have a concrete resolved value for it.
- `thread_ts` is valid **only** for replies in an existing thread. For normal channel posts, DMs, and new group DMs, **omit the `thread_ts` key entirely**.
- `slack_create_canvas` is an **immediate write, not a draft**. Use it only when the user explicitly asked for a canvas, doc, or immediate Slack write of that form.
- Use `slack_schedule_message` **only** when the user explicitly asked for future delivery or supplied a send time.
- `slack_send_message_draft` **cannot overwrite** an existing attached draft. Do not claim that you verified the destination is draft-free before calling the tool.
- If `slack_send_message_draft` returns `draft_already_exists`, **stop immediately**. Tell the user there is already an attached draft in that destination and that Slack cannot overwrite it.
- Current Slack app support here is centered on **messages, drafts, scheduled messages, canvases, and read/search flows**. Do not claim support for creating channels, editing messages, deleting messages, or resolving Slack user groups when the runtime does not expose those actions.

## Destination Safety

- If the user wants to **cc, mention, or tag** someone, first check whether that person is already in the destination channel or group DM when the connector makes that practical. If you cannot verify it, do not imply the mention will notify them.
- Treat `@here`, `@channel`, `@everyone`, and similar broad notifications as **high-impact**. Do not add them unless the user explicitly asked for them.

## Formatting Rules

- Write concise Slack-ready text that follows the live tool contract and Slack mrkdwn mention syntax (`<@U…>`, `<#C…>`).
- Prefer a short opener, a few tight bullets, and a clear ask or next step.
- Use explicit Slack mention syntax only when you resolved the target successfully.
- Preserve source links, code, owners, dates, and commitments unless the user asked for edits.
- Do not invent approvals, decisions, or follow-through.

## Pitfalls

- **Bare `@name` text does not notify.** Slack requires `<@U...>` or `<!subteam^S...>` syntax. If you cannot resolve the ID, tell the user rather than faking a mention.
- **Adding `thread_ts` to a non-thread message** will cause the message to thread onto an unrelated parent or error out. Omit it entirely for top-level posts.
- **Assuming a draft destination is empty.** `slack_send_message_draft` cannot overwrite. If you get `draft_already_exists`, stop and inform the user.
- **Using `slack_create_canvas` when the user only wanted a message.** Canvas is an immediate write to a Slack doc surface, not a channel post. Confirm the user wants a canvas before calling it.
- **Broad mentions (`@here`, `@channel`, `@everyone`) without explicit user request.** These are high-impact and disruptive. Never add them speculatively.
- **Inventing Slack capabilities.** Do not claim the runtime can create channels, edit/delete messages, or resolve user groups unless those actions are actually exposed.
- **Drafting when the user said "send."** If the user explicitly asked to send or post, perform the write directly. Do not downgrade to a draft out of caution.

## Verification

After executing a Slack write action, confirm success:

- **Direct send (`slack_send_message`)**: The tool should return a message identifier or confirmation (e.g., `ok` with a `ts` value). Confirm to the user: "Message sent to `#channel-name`."
- **Draft (`slack_send_message_draft`)**: The tool should return a draft confirmation. Confirm to the user: "Draft attached in `#channel-name` — review and send when ready."
- **Scheduled message (`slack_schedule_message`)**: The tool should return a scheduled message identifier. Confirm to the user: "Message scheduled for `<datetime>` in `#channel-name`."
- **Canvas (`slack_create_canvas`)**: The tool should return a canvas URL or identifier. Confirm to the user: "Canvas created: `<url>`."
- **Error case**: If any tool returns an error (e.g., `draft_already_exists`, `channel_not_found`, `invalid_auth`), surface the error verbatim to the user and stop. Do not retry silently or fabricate a success.

## Related Skills

- `slack` — read, search, and analyze Slack context. Use this to gather source material before switching to `slack-outgoing-message` for the final write.
