# Output Templates

One template per thread style. Replace every [BRACKETED SLOT] with content extracted from the source. Never leave bracket text in the final output. If a step or insight is not in the source, skip that tweet rather than inventing content.

Adjust N to the actual tweet count (7-10) before numbering.

---

## Template 1: Data/Insight

Use for evidence-based articles with stats, research findings, or data points.

```
1/N [HOOK — the most surprising stat or finding from the article]

2/N [CONTEXT — what most people assume or the common approach]

3/N [FIRST DATA POINT — specific number or finding]

4/N [SECOND DATA POINT — specific number or finding]

5/N [THIRD DATA POINT OR IMPLICATION — what this means in practice]

6/N [COUNTERPOINT — the objection or nuance worth acknowledging]

7/N [TAKEAWAY — the single most useful thing to remember]

8/N [CTA — what to do next, source link if provided]
```

Worked example (API performance profiling article):

```
1/8 Most developers are optimising the wrong bottleneck. They profile query speed. The real problem is payload size.

2/8 Standard advice: add indexes, cache queries, tune your ORM. All fine. None of it addresses what's actually slow in 60% of cases.

3/8 We ran a trace on our most-used endpoint. 800ms response time. Query: 12ms. Serialization: 788ms. We were sending 4MB of data per request.

4/8 Switched to field selection. Users request only the fields they need. Average payload dropped from 4MB to 180KB.

5/8 Response time: 800ms to 90ms. No query changes. No cache layer. No infrastructure cost.

6/8 This doesn't apply if your queries are actually slow. Profile first. Don't assume.

7/8 The bottleneck is almost always what you're sending, not how fast you're finding it.

8/8 Full post in the replies. If this was useful, retweet tweet 1.
```

---

## Template 2: How-To

Use for tutorials, guides, and step-by-step articles.

```
1/N [HOOK — the result the reader achieves, or what most people miss]

2/N [WHY THIS MATTERS — the cost of not doing it, or who this is for]

3/N [STEP 1 — one action, one line]

4/N [STEP 2 — one action, one line]

5/N [STEP 3 — one action, one line]

6/N [STEP 4 OR KEY MISTAKE — common error at this stage]

7/N [RESULT — what happens when you follow the steps]

8/N [CTA]
```

Worked example (SSH key authentication setup):

```
1/8 You don't need a password to SSH into a server. Here's how to set it up in 10 minutes.

2/8 Password SSH leaves you open to brute force. Key auth locks that door. Most devs know this and still haven't done it.

3/8 Step 1: Generate your key pair. Run: ssh-keygen -t ed25519 -C your@email.com. Save to ~/.ssh/id_ed25519.

4/8 Step 2: Copy the public key to your server. Run: ssh-copy-id user@server-address. It adds your key to authorized_keys automatically.

5/8 Step 3: Test the connection. Run: ssh user@server-address. No password prompt means it worked.

6/8 Common mistake: forgetting to restrict permissions. Run chmod 700 ~/.ssh and chmod 600 ~/.ssh/authorized_keys on the server.

7/8 Once this is set up, you never type that password again. Every other tool — rsync, SCP, Git over SSH — inherits the key auth.

8/8 Full step-by-step in the replies. Works on Linux, macOS, and WSL.
```

---

## Template 3: Story/Journey

Use for personal experience articles, build logs, and lessons-learned posts.

```
1/N [HOOK — the end result or the key moment that changed things. Does not start with "I".]

2/N [SETUP — where you started, the problem]

3/N [DECISION — what you tried or changed]

4/N [WHAT HAPPENED — the unexpected result or outcome]

5/N [WHAT YOU LEARNED — the lesson]

6/N [WHAT YOU'D DO DIFFERENTLY — the advice for others]

7/N [TAKEAWAY — for the reader, not just you]

8/N [CTA]
```

Worked example (indie hacker launch story):

```
1/8 After 6 months of building in silence, we shipped. First paying customer came 4 hours later. Here's what went right and what nearly didn't.

2/8 We built a tool for devs to monitor API latency across providers. Nothing fancy. The problem was real — we had it ourselves.

3/8 3 months in, we almost pivoted. Users kept asking for Slack alerts. We said no. Stayed focused on the core latency chart.

4/8 Launch day: posted on HN Show. Got 230 upvotes. 140 signups in 24 hours. 3 converted to paid on day 1.

5/8 The Slack alerts users asked for? We shipped them in month 4. They became our top retention driver. We just needed to earn the right to build them.

6/8 Ship the dumb simple version first. Not because it's faster. Because it tells you what actually matters.

7/8 Feature requests are noise until you have users. Users tell you which noise is signal.

8/8 Full build log in the replies. What would you have done differently?
```

---

## Template 4: Hot Take

Use for opinion pieces, contrarian arguments, and counterintuitive claims.

```
1/N [THE CLAIM — the contrarian position stated directly]

2/N [THE ASSUMPTION — what most people believe and why]

3/N [THE EVIDENCE — what you actually observed or data that supports the claim]

4/N [THE IMPLICATION — what changes if the claim is true]

5/N [THE COUNTERARGUMENT — steelman the other side]

6/N [THE REBUTTAL — why you still hold the position]

7/N [THE NUANCE — when are you wrong? edge cases?]

8/N [CTA — ask for disagreement: "Tell me why I'm wrong."]
```

Worked example (standups are waste):

```
1/8 Daily standups don't solve coordination problems. They create them.

2/8 The logic: if everyone knows what everyone else is doing, blockers surface faster. Reasonable assumption. Wrong conclusion.

3/8 We tracked 3 months of standups. Average useful information exchanged per person: 12 seconds. Average time lost to context switching: 23 minutes per attendee.

4/8 If standups are your coordination layer, async is your alternative. But most teams treat async as standups with a time delay.

5/8 The counterargument: standups build team cohesion. True. But you can build cohesion cheaper with better rituals.

6/8 The real function of standups is making managers feel informed. That's a legitimate need. It's not a coordination mechanism.

7/8 This breaks down for teams that are genuinely blocked on each other daily. Short-cycle integration work, for instance. Know your context.

8/8 Tell me why I'm wrong. Full piece in the replies.
```

---

## Fill-in Rules

1. Replace every [BRACKETED SLOT] with content from the source material
2. Never leave bracket text in the output
3. Count characters for every tweet including the "N/N " prefix
4. Apply Writing Style rules: no em dashes, no semicolons, no banned words, no hashtags
5. If a step or point is not in the source, skip that tweet rather than inventing content
6. Adjust N to the actual tweet count (7-10)
7. The CTA tweet always goes last, always contains the source URL if one was provided
