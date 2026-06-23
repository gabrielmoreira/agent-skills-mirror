# How to Set Up Your Own Weekly Intelligence Digest in Cowork

This walks you through creating a personalized digest that searches the web for developments relevant to your work and delivers them to Slack on a schedule you choose.

## What You Get

A scheduled message in Slack — daily, weekly, or whatever cadence you want — covering the topics you care about, filtered for relevance to your role and company, with links so you can go deeper on anything that catches your eye.

## What You Need

Cowork installed, Slack connected in Cowork.

---

## How It Works

You paste one prompt into Cowork. Claude interviews you to understand your topics, filters, cadence, and delivery destination. It runs real searches and shows you a sample output. Once you confirm it looks right, it creates the scheduled task automatically. The whole setup takes about 15 minutes.

---

## The Prompt

Copy and paste this into Cowork:

```text
Help me set up a personalized intelligence digest — a scheduled message that searches the web for developments relevant to my work and delivers them to Slack.

Before building anything, interview me. Ask ONE question at a time, provide your recommendation for each decision, and confirm what you heard before moving on. Here's what you need to learn:

1. My role and company, so you understand what "relevant" means
2. What topics I want covered — these can be anything: regulatory areas, industry news, competitor activity, technical developments, social media signals, etc.
3. For each topic: what should be included vs. filtered out (what makes something relevant to my work?)
4. Where I want it delivered: a specific Slack channel (I'll create a private one if needed) or DM
5. Cadence: daily, weekly, bi-weekly — and what day/time
6. Any people, companies, jurisdictions, or products I want to track specifically

After the interview:

- Run real web searches across my topics
- Show me a sample of exactly what my digest would look like
- Get my feedback and make adjustments
- Only create the scheduled task once I confirm the sample looks good

Start by asking about my role and what topics matter most to my work right now.
```

---

## Tips

On topics: Be specific. "Regulatory developments" is too broad — "California and federal privacy laws affecting consumer apps" is useful. The more specific your topics, the better the signal-to-noise ratio.

On relevance filters: Think about what you'd actually forward to a colleague vs. what you'd ignore. Those instincts translate directly into filter rules.

On cadence: Weekly is the right default for most topics. Daily works if you're in an active regulatory or competitive situation where timing matters. Bi-weekly is fine for slower-moving areas.

On delivery: Create a private Slack channel (takes 30 seconds) rather than a DM. It gives you a searchable archive and makes it easy to add teammates later. To get the channel ID after creating it: click the channel name → scroll to the bottom of the details panel.

On the sample: Don't confirm it until it actually looks useful. If a section is consistently empty or noisy, adjust the topic framing before locking in the schedule.

On the scheduled task: Once created, you can always ask Cowork to "update my digest schedule" or "add a new topic to my digest" and it will adjust. Nothing is permanent.

---

## After Setup

Your digest skill files will be saved to your Cowork outputs folder. To make the digest triggerable on demand (in addition to the schedule), move the skill folder into ~/.claude/skills/. Then you can say "run my digest" any time you want a fresh one outside the normal schedule.
