---
name: developer-advocacy
description: "Plans DevRel work: conference CFPs, talk prep, live-coding demos (10-3-1 checkpoints), podcast pitches, building-in-public, and advocacy metrics. Use when the user mentions developer advocacy, DevRel, CFP, conference talk, live coding, podcast guesting, or building in public. Not for product marketing copy, authoring SKILL.md, or implementing the product. Never skip audience context or share customer or security data while building in public."
version: 1.0.1
risk: unknown
source: https://github.com/jonathimer/devmarketing-skills/tree/main/skills/developer-advocacy
source_repo: jonathimer/devmarketing-skills
source_type: community
date_added: 2026-07-01
license: MIT
license_source: https://github.com/jonathimer/devmarketing-skills/blob/main/LICENSE
---

# Developer Advocacy

## When to Use

Use this skill when the user wants to plan or execute developer advocacy activities. Trigger phrases include:

- "developer advocacy" / "devrel"
- "conference talk" / "CFP" / "call for papers"
- "live coding" / "demo prep"
- "podcast" / "podcast pitch"
- "building in public" / "social presence"
- "advocacy metrics" / "advocacy report"

This skill covers the full advocacy lifecycle: finding conferences, writing talk proposals, preparing live demos, pitching and appearing on podcasts, building in public, managing social presence, and measuring impact.

## Prerequisites

1. **Load audience context first.** Before any advocacy work, read `.agents/developer-audience-context.md` to understand:
   - Who you're trying to reach (conferences they attend, podcasts they listen to)
   - What topics resonate (pain points, interests)
   - Your product's positioning (what story to tell)
   - Voice & tone (how formal/technical to be)

2. If the context file does not exist, run the `developer-audience-context` skill first to generate it.

3. **Templates live in this skill.** Use them at these moments:
   - Conference talk proposal — CFP template in §1.2.
   - Live coding demo — pre-demo checklist in §2.2.
   - Podcast guest pitch — pitch template in §3.2.
   - Monthly advocacy report — report template in §6.3.

## Procedure

### 1. Conference Talks

#### 1.1 Finding the Right Conferences

| Conference Type | Best For | Examples |
|-----------------|----------|----------|
| **Large industry** | Brand awareness, reach | KubeCon, AWS re:Invent, React Summit |
| **Regional** | Local community, accessible | Local meetups, city tech conferences |
| **Niche** | Targeted audience, expertise | GraphQL Conf, RustConf |
| **Company-hosted** | Ecosystem presence | Vercel Ship, GitHub Universe |
| **Unconferences** | Community connection | BarCamps, DevOpsDays |

#### 1.2 Writing a Talk Proposal (CFP)

**Winning formula:**

```
Specific Problem + Unique Angle + Clear Takeaways = Accepted Talk
```

**CFP Template:**

```markdown
# Title
[Action verb] + [specific outcome] + [with/using what]
Example: "Building Real-Time Features with Edge Functions and WebSockets"

# Abstract (100-200 words)
[Hook: Problem or curiosity gap]
[What you'll cover]
[What attendees will learn/be able to do]

# Description (detailed, for reviewers)
[Problem context]
[Why this approach]
[Talk structure]
[Your credibility to give this talk]

# Outline
- [Time] Introduction / Problem statement
- [Time] Section 1
- [Time] Section 2
- [Time] Section 3
- [Time] Live demo / walkthrough
- [Time] Key takeaways / Q&A

# Audience
[Who this is for]
[Prerequisite knowledge]
[What they'll learn]

# Bio
[Your relevant experience]
[Why you're qualified]
```

**Title patterns that work:**

| Pattern | Example |
|---------|---------|
| **How I X** | "How I Reduced Deploy Time by 80%" |
| **X in Y Minutes** | "Kubernetes Security in 15 Minutes" |
| **The X of Y** | "The Psychology of Error Messages" |
| **Beyond X** | "Beyond Console.log: Modern Debugging" |
| **X for Y** | "GraphQL for REST Developers" |
| **Lessons from X** | "Lessons from 1000 Production Outages" |

**Talk types:**

| Type | Length | Best For |
|------|--------|----------|
| **Lightning** | 5-10 min | Single concept, quick demo |
| **Standard** | 25-45 min | Technical deep-dive |
| **Keynote** | 45-60 min | Big picture, inspiring |
| **Workshop** | 2-4 hours | Hands-on learning |
| **Panel** | 30-60 min | Discussion, multiple perspectives |

#### 1.3 Talk Prep Checklist

| Phase | Tasks |
|-------|-------|
| **2 months before** | Outline, start slides, test demos |
| **1 month before** | Draft complete, first practice run |
| **2 weeks before** | Slides polished, demos solid, practice 3x |
| **1 week before** | Record yourself, get feedback, finalize |
| **Day before** | Test all tech, backup slides, rest |
| **Day of** | Arrive early, test A/V, hydrate |

### 2. Live Coding & Demos

#### 2.1 The 10-3-1 Rule

- Run your demo **10 times** in practice
- Have **3 checkpoints** you can jump to if stuck
- **1 backup** (video recording of it working)

#### 2.2 Pre-Demo Checklist

- [ ] Close unnecessary apps
- [ ] Clear browser history/tabs
- [ ] Notifications OFF (Slack, email, calendar)
- [ ] Font size: 24pt+ for terminal, 20pt+ for editor
- [ ] Git stash/branch for clean starting point
- [ ] Environment variables ready
- [ ] Test on the actual projector/screen if possible

#### 2.3 Demo Danger Zone — Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Internet fails** | Pre-record backup, local server |
| **Typo freezes you** | Practice typing same code 20x |
| **Error you can't fix** | Have working checkpoints to jump to |
| **Runs over time** | Time yourself, cut ruthlessly |
| **Code too small** | Zoom in, use large font (24pt+) |
| **Dark theme blinding** | Use high-contrast, light-friendly theme |

#### 2.4 Live Coding Tips

| Tip | Why |
|-----|-----|
| **Type slowly** | Audience needs to follow |
| **Narrate what you type** | "I'm creating a new handler..." |
| **Explain errors** | "This error means X, let me fix it" |
| **Use snippets** | For boilerplate, not core concepts |
| **Show the result** | Always run the code, show output |
| **Checkpoint commits** | `git checkout checkpoint-1` |

### 3. Podcast Guesting

#### 3.1 Finding Podcasts

| Approach | How |
|----------|-----|
| **Direct search** | "top [your tech] podcasts" |
| **Guest networks** | Podmatch, Matchmaker.fm |
| **Peer asks** | "What podcasts do you listen to?" |
| **Twitter search** | "[topic] podcast episode" |
| **Listen Notes** | Podcast search engine |

#### 3.2 Pitch Template

```
Subject: Guest Idea: [Specific Topic] for [Podcast Name]

Hi [Host Name],

I've been listening to [Podcast] for [time] — loved your episode on [specific episode].

I'd love to come on and talk about [specific topic]. Here's the angle:

[2-3 sentences on what you'd discuss and why it matters to their audience]

A bit about me:
- [Relevant credential 1]
- [Relevant credential 2]
- [Link to past podcast/talk]

Would this be a fit?

[Your name]
```

#### 3.3 Pre-Podcast Prep

| Prep Item | Details |
|-----------|---------|
| **Research the show** | Listen to 2-3 episodes, understand format |
| **Research the host** | Their interests, style, Twitter |
| **Prep talking points** | 3-5 main things you want to say |
| **Prep stories** | Specific examples, not generalities |
| **Audio setup** | Good mic, quiet room, headphones |
| **Water nearby** | You'll be talking a lot |

#### 3.4 During the Podcast

| Do | Don't |
|----|-------|
| Tell stories with specifics | Give generic advice |
| Pause before answering | Um and ah nervously |
| Disagree respectfully | Always agree to be polite |
| Promote subtly | Hard sell your product |
| Be concise | Ramble without structure |
| Show enthusiasm | Be monotone |

#### 3.5 Post-Podcast

| Action | Timing |
|--------|--------|
| Thank the host | Same day |
| Share when published | Immediately |
| Engage with comments | First week |
| Cross-promote | Your newsletter, blog |
| Stay in touch | Ongoing relationship |

### 4. Building in Public

#### 4.1 What to Share

| Category | Content Ideas |
|----------|---------------|
| **Progress** | "Shipped X today, here's what I learned" |
| **Challenges** | "Stuck on X, tried Y and Z, here's what worked" |
| **Decisions** | "Why we chose X over Y" |
| **Metrics** | Revenue, users, growth (transparently) |
| **Behind scenes** | Team, process, tools |
| **Learnings** | "Mistake we made and how we fixed it" |

#### 4.2 Build in Public Formats

| Format | Platform | Cadence |
|--------|----------|---------|
| **Tweet thread** | Twitter/X | Daily-weekly |
| **Changelog** | Blog, Notion, website | Weekly |
| **Indie hacker posts** | Indie Hackers, HN | Monthly |
| **Video update** | YouTube, Loom | Weekly-monthly |
| **Newsletter** | Email | Weekly |
| **Livestream** | Twitch, YouTube | Weekly |

#### 4.3 What NOT to Share

| Avoid | Why |
|-------|-----|
| **Customer data** | Privacy, trust |
| **Team conflicts** | Professionalism |
| **Security details** | Vulnerability |
| **Competitor attacks** | Looks petty |
| **Venting** | Not productive |

### 5. Social Presence (Twitter/X)

#### 5.1 Content Mix

| Content Type | % of Posts | Example |
|--------------|------------|---------|
| **Value content** | 60% | Tips, tutorials, insights |
| **Engagement** | 20% | Replies, retweets with commentary |
| **Personal** | 10% | Behind-the-scenes, personality |
| **Promotion** | 10% | Your product, talks, content |

#### 5.2 Tweet Formats That Work

| Format | Example |
|--------|---------|
| **Thread** | "10 things I learned building X" |
| **Hot take** | "Unpopular opinion: [opinion]" |
| **Quick tip** | "TIL: You can do X by..." |
| **Question** | "What's your favorite way to..." |
| **Meme/humor** | Tech jokes, relatable content |
| **Showcase** | "Just shipped X, here's how it works" |
| **Appreciation** | "Shoutout to @person for..." |

#### 5.3 Engagement Strategy

| Action | Frequency |
|--------|-----------|
| Tweet original content | Daily |
| Reply to others | 5-10x daily |
| Quote tweet with value | 2-3x weekly |
| DM interesting people | Weekly |
| Join Twitter Spaces | As relevant |

#### 5.4 Growing Your Presence

| Tactic | Implementation |
|--------|----------------|
| **Consistency** | Post daily, engage daily |
| **Niche down** | Be known for ONE thing first |
| **Reply game** | Add value to big accounts' tweets |
| **Collaborate** | Twitter Spaces, threads together |
| **Cross-promote** | Newsletter, talks, blog |

### 6. Measuring Impact

#### 6.1 Advocacy Metrics

| Activity | Metrics |
|----------|---------|
| **Talks** | Attendees, feedback scores, recording views |
| **Content** | Views, shares, engagement |
| **Social** | Followers, engagement rate, reach |
| **Podcasts** | Listener estimates, traffic spikes |
| **Community** | Growth, engagement, sentiment |

#### 6.2 Attribution Signals

Developer advocacy impact is notoriously hard to measure. Use these proxy metrics:

| Signal | What It Indicates |
|--------|-------------------|
| **Traffic spikes** | Content/talk/podcast drove visits |
| **"How did you hear about us?"** | Direct attribution |
| **Social mentions** | Brand awareness |
| **Inbound leads quality** | Community-qualified leads |
| **Conference invites** | Growing reputation |

#### 6.3 Monthly Advocacy Report

```markdown
# Developer Advocacy Report - [Month]

## Talks & Appearances
- [Talk 1]: [Conference], [Attendees], [Link]
- [Podcast 1]: [Show], [Episode link]

## Content Published
- [Article 1]: [Views], [Engagement]
- [Video 1]: [Views]

## Social Growth
- Twitter: +X followers, Y impressions
- Notable tweets: [Links]

## Community
- Discord/Slack: +X members, Y messages
- Notable threads/discussions

## Learnings
- What worked: [X]
- What didn't: [Y]
- Trying next: [Z]
```

### 7. Advocacy Career Path

| Level | Focus |
|-------|-------|
| **Junior DA** | Content creation, community support, talk prep |
| **Developer Advocate** | Talks, own content strategy, community building |
| **Senior DA** | Strategy, mentoring, major conferences |
| **Staff DA** | Cross-company impact, industry thought leadership |
| **Head of DevRel** | Team building, strategy, executive alignment |

| Skill | How to Develop |
|-------|----------------|
| **Public speaking** | Meetups, Toastmasters, practice |
| **Writing** | Blog consistently, get feedback |
| **Video** | YouTube, live streaming, improve iteratively |
| **Technical depth** | Build projects, contribute to OSS |
| **Community** | Moderate, organize events, connect people |

### 8. Tools

| Tool | Use Case |
|------|----------|
| **[Octolens](https://octolens.com)** | Monitor your name/brand across GitHub, Twitter, Reddit, HN, Stack Overflow. Track conference mentions. Find podcast opportunities. Measure share of voice. |
| **Cal.com / Calendly** | Schedule podcast appearances |
| **StreamYard** | Live streaming setup |
| **Descript** | Video/podcast editing |
| **Canva / Figma** | Slides and graphics |
| **Otter.ai** | Transcription for talks |
| **Notion** | Talk prep, content calendar |
| **Buffer / Typefully** | Social scheduling |

## Pitfalls

- **Skipping audience context.** Writing a CFP or pitch without loading `.agents/developer-audience-context.md` leads to generic proposals that get rejected. Always load context first.
- **No demo backup.** Live demos fail. If you have no pre-recorded fallback or checkpoint commits, you risk a blank screen in front of hundreds of attendees. Follow the 10-3-1 rule.
- **Hard-selling on podcasts.** Overt product pitches damage host relationships and reduce future invitations. Promote subtly; lead with value and stories.
- **Oversharing sensitive data.** Never share customer data, security details, or team conflicts when building in public. This breaks privacy, trust, and professionalism.
- **Ignoring attribution.** Advocacy without measurement is invisible to leadership. Always include proxy metrics and "how did you hear about us?" tracking in your reporting.
- **Inconsistent social presence.** Posting in bursts then going silent kills algorithmic reach. Post daily and engage daily for sustained growth.
- **Under-practicing talks.** One practice run is not enough. Aim for 3 full run-throughs in the final 2 weeks, plus a recording for self-review.

## Verification

1. **Audience context loaded:**
   ```powershell
   Test-Path .agents\developer-audience-context.md
   ```
   Expected output: `True`. If `False`, run the `developer-audience-context` skill first.

2. **CFP completeness check** — Confirm your proposal has all required sections:
   ```powershell
   Select-String -Path .\cfp-draft.md -Pattern "^# (Title|Abstract|Description|Outline|Audience|Bio)"
   ```
   Expected: 6 matching lines. If fewer, add the missing sections.

3. **Demo checkpoint commits exist:**
   ```powershell
   git tag --list "checkpoint-*"
   ```
   Expected: at least 3 tags (e.g., `checkpoint-1`, `checkpoint-2`, `checkpoint-3`).

4. **Font size for live coding** — Verify terminal and editor fonts are 24pt+ and 20pt+ respectively before the talk. Visually confirm on the projector if possible.

5. **Monthly report generated** — Confirm the report file exists and contains all sections:
   ```powershell
   Select-String -Path .\advocacy-report.md -Pattern "^## (Talks & Appearances|Content Published|Social Growth|Community|Learnings)"
   ```
   Expected: 5 matching lines.

## Related Skills

- `developer-audience-context` — Know who you're reaching
- `devrel-content` — Written content strategy
- `community-building` — Community management
- `open-source-marketing` — OSS-specific advocacy
- `hacker-news-strategy` — HN engagement

## Limitations

- Use this skill only when the task clearly matches its upstream source and local project context.
- Verify commands, generated code, dependencies, credentials, and external service behavior before applying changes.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
