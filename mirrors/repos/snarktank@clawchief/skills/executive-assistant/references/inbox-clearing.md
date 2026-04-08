# Inbox clearing

## Goal

Run inbox triage like a real executive assistant, not a passive notifier.

That means:

- clear low-risk items directly
- keep scheduling moving
- reduce Ryan's inbox burden
- escalate only when judgment, sensitivity, or strategy is required
- do not silently leave actionable messages untouched after reviewing them

## Thread-awareness rule

Before replying in an existing thread, inspect the thread headers and participant list first.

That means:

- check who is already in `To` / `CC`
- preserve those recipients when the thread should continue
- for any reply to an existing thread, use `python3 ~/.openclaw/workspace/clawchief/scripts/ea_gmail.py reply --message-id=...` instead of a fresh send with `Re:` in the subject
- do not handcraft reply subjects yourself; let the helper use `gws` threading tied to the concrete parent message
- do not use raw `--thread-id` as the reply mechanism for human email replies; use the concrete parent `MESSAGE_ID`
- add `--reply-all` for scheduling and coordination mail when the thread recipients should remain copied
- treat cancellations, reschedules, confirmations, corrections, follow-ups, and Ryan-delegated thread work as existing-thread replies unless inbox + sent prove there is no thread
- identify the exact Gmail `MESSAGE_ID` you will reply to before drafting the send
- if you cannot point to that reply target yet, do not send yet
- if you need to correct yourself in the same turn, update the in-thread reply plan instead of sending a second standalone note
- do not ask Ryan for an email address or identity that is already visible in the thread
- do not send a reply only to Ryan when the real intended recipient is already on the thread
- if Ryan emails R2 directly from one of Ryan's own addresses, treat that message as reply-required by default; do not classify it away as merely conversational and leave it untouched

## Safe to handle directly

Handle these without asking Ryan first:

- meeting scheduling, rescheduling, cancellations, and invite follow-up
- short acknowledgment replies for scheduling or operational coordination
- confirming receipt and saying what will happen next
- emails from Ryan that assign a task or request coordination: acknowledge quickly, then do the work or send a status update
- direct human emails from Ryan, including short questions or conversational check-ins: reply in-thread with an answer or brief acknowledgment even when no other EA action is needed
- sending workable time options after checking Ryan's calendar
- calendar invite creation/update/cancellation when authority is clear
- routine admin or vendor notices that just need to be read/archived
- obvious noise, newsletters, automated system mail, and non-actionable notifications
- straightforward factual replies when the answer is already clear from the thread or calendar
- direct business follow-up questions that only need a brief factual answer or a short holding reply

## Escalate to Ryan before replying

Escalate when the email is:

- legal, regulatory, or conflict-heavy
- financial, pricing, investor, fundraising, or contract-related
- press, podcast, speaking, or public-facing in a way that needs Ryan's voice
- a partnership or business-development opportunity with unclear value or positioning
- emotionally sensitive, personal, or reputationally risky
- strategically important and likely to change priorities or commitments
- unclear enough that a wrong reply would create confusion

## When a fast holding reply is appropriate

If something cannot be fully resolved in the current run but should not sit silently, send a short holding reply when it is low-risk to do so.

Use this by default for:

- direct unanswered questions from vendors, prospects, partners, or operators in an active thread
- non-sensitive business follow-ups where you need a little more time
- items waiting on Ryan but where a brief acknowledgment is better than silence

Example pattern:

```text
Thanks — got it. I’m checking this and will get back to you shortly.
```

Do not use a holding reply if silence is safer than speaking.

## Inbox state rules

After action:

- replied and done → mark read + archive
- acknowledged and now waiting on the other party → leave in inbox if needed, otherwise archive
- reviewed and no reply needed → mark read + archive
- waiting on the other party → leave in inbox
- waiting on Ryan → leave in inbox and Slack Ryan if action is needed
- direct Ryan email with no larger workflow attached → still reply in-thread, then mark read + archive if nothing else is pending
- if you intentionally leave an actionable email untouched, record the reason in the Slack update to Ryan

## Sweep limits

To keep cron runs healthy:

- inspect only the top recent actionable batch first
- fetch bodies only for likely-actionable messages
- prefer 5-10 messages per run over trying to clear the entire mailbox every time
- if the inbox is unusually deep, clear the highest-value batch first and continue next run
