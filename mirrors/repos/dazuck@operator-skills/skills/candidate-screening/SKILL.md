---
name: candidate-screening
description: Screen job candidates from Greenhouse using AI-powered evaluation. Use when asked to "screen candidates", "review applicants", "run candidate screening", "check new applications", or "evaluate candidates".
---

# Finding Great Candidates

Goal: Identify candidates we'd be **thrilled** to have on the team. Not "can do the job" — candidates we're excited about.

> "Our first 100 people are our cultural co-founders."

## What Makes Someone Great (Universal Traits)

These traits apply to EVERY role. A candidate missing any of these is unlikely to be great.

### 1. High Agency

**What it is**: Takes initiative. Makes things happen. Doesn't wait for permission or perfect conditions.

**How to spot it**:

- Started something from nothing (project, company, community, initiative)
- Identified problems and solved them without being asked
- Phrases like "I noticed X wasn't working, so I..." or "I proposed..."
- Built things with limited resources
- Career moves that show they created opportunity vs. waited for it

**Red flags**:

- Passive language ("I was assigned to...", "My manager asked me to...")
- No examples of self-initiated work
- Lots of "we" with no clear individual contribution
- Job history of only joining established teams/processes

### 2. Grit & Resilience

**What it is**: Perseveres through hard things. Doesn't quit when it gets difficult.

**How to spot it**:

- Shipped something hard (long timeline, technical challenges, organizational friction)
- Stayed with a problem until solved vs. moving on when stuck
- Built something despite obstacles (funding, team, technical, market)
- Career shows persistence (didn't job-hop at first sign of difficulty)
- Specific stories of overcoming setbacks

**Red flags**:

- Lots of short stints without clear upward moves
- Vague explanations for leaving ("it wasn't a good fit")
- No examples of pushing through difficulty
- Blame-shifting to circumstances

### 3. Evidence of Impact

**What it is**: Demonstrable results. Outcomes, not just activities.

**How to spot it**:

- Metrics at ANY scale: "10x'd revenue", "reduced costs 60%", "shipped to 5M users"
- Promotions and increasing scope over time (trajectory)
- Concrete examples: "built X which did Y"
- Results even in resource-constrained environments
- Would their bosses rate them 8+ and hire them again?

**Red flags**:

- Vague: "worked on", "contributed to", "helped with"
- No metrics even for senior roles
- Flat trajectory (same level/scope over years)
- Titles without corresponding impact stories

### 4. Technical Depth

**What it is**: Everyone should code, build, or have deep technical understanding.

**How to spot it**:

- GitHub/portfolio with real projects
- Technical blog posts or writing
- Can explain complex systems simply
- Specific technical choices and tradeoffs mentioned
- For non-eng: deep understanding of how things work, technical curiosity

**Red flags**:

- Avoids technical detail
- Can't explain their technical work
- No evidence of building things
- Relies entirely on others for technical decisions

### 5. AI-Native

**What it is**: Uses AI tools daily, understands implications, sees opportunities.

**How to spot it**:

- Mentions specific tools: Claude, ChatGPT, Cursor, Copilot
- Built something with AI or integrated AI into workflow
- Understands AI capabilities and limitations
- Excited about AI, not fearful
- Uses AI to accelerate their own work

**Red flags**:

- No mention of AI tools
- Seems unaware of AI capabilities
- Treats AI as novelty vs. fundamental shift
- Behind the curve on modern tools

### 6. Communication Excellence

**What it is**: Writes clearly, explains complex ideas simply, collaborates well.

**How to spot it** (their APPLICATION is a sample!):

- Clear, structured writing
- Gets to the point
- Explains technical concepts accessibly
- Good questions in interviews
- Public writing/speaking if available

**Red flags**:

- Rambling or unclear application
- Can't articulate their own work
- Jargon-heavy without substance
- Poor writing quality

### 7. World-Class at Something

**What it is**: Top 1% in at least one domain. Demonstrable excellence.

**How to spot it**:

- Recognized expertise: patents, publications, talks, awards
- Deep mastery evident in how they discuss their domain
- Built something impressive in their area
- Others seek them out for this expertise
- "The person you call" for X

**Red flags**:

- Average across the board
- No area of clear strength
- Jack of all trades, master of none
- Can't point to what they're best at

### 8. Interesting Person

**What it is**: Curious, diverse interests, unique perspective. Someone you'd want at dinner.

**How to spot it**:

- Unusual background or path
- Hobbies/interests outside work
- Asks interesting questions
- Learns continuously
- Brings different perspective to problems

**Red flags**:

- One-dimensional
- No interests outside work
- Generic responses
- Nothing memorable about them

---

## Role-Specific Traits

Beyond universal traits, each role has specific requirements:

### Engineering Roles (Full-Stack, Software, AI Lead)

- Shipped production code at scale
- System design thinking
- Code quality/testing discipline
- Open source contributions (bonus)
- Technical leadership/mentorship (for senior)

### AI Application Engineer

- Deep in AI research community
- Translates research → shipped features
- Built AI evaluation/experimentation systems
- Rapid prototyping ability
- Stays current with latest developments

### Community Manager

- Always-on presence and reliability
- Crisis management experience
- Multi-channel management (Discord, Telegram, X)
- Clear, accurate communication under pressure
- Domain community experience (web3, developer, B2B, etc.)

### Program / Event Manager

- Public-facing comfort and energy
- Operational excellence
- Event/program management at scale
- Builds playbooks and systems
- AI-powered automation of workflows

### Technical Account Manager

- Technical depth + customer empathy
- Problem-solving under pressure
- Clear communication of technical concepts
- Project management discipline
- Relationship building

---

## The Screening Process

### Step 1: Run the Screen

If you have a screening tool (e.g., a Greenhouse integration script):

```bash
cd [YOUR_SCREENING_TOOL_PATH] && npm run screen -- --days-back 1 --min-score 70
```

Common variations:

```bash
# Last 7 days, specific role
npm run screen -- --days-back 7 --job-id [JOB_ID]

# Higher bar (80+), tag in Greenhouse
npm run screen -- --min-score 80 --tag-greenhouse

# All options
npm run screen -- --days-back 7 --min-score 75 --tag-greenhouse --send-slack
```

If you don't have a screening tool, pull candidates from Greenhouse manually or via the Greenhouse API and feed them to Claude for evaluation using the framework below.

### Step 2: Read the Output

```bash
cat [YOUR_SCREENING_TOOL_PATH]/output/daily-digest-$(date +%Y-%m-%d).md
```

### Step 3: Deep Dive on Top Candidates

For anyone scoring 75+, provide deeper analysis with **links always included**:

```markdown
## [Name] — [Score]/100

**Links**: [Greenhouse](https://app4.greenhouse.io/people/[CANDIDATE_ID]/applications/[APP_ID]/redesign) | [LinkedIn](URL or "Not provided")

### Universal Traits Assessment

| Trait         | Signal   | Evidence                        |
| ------------- | -------- | ------------------------------- |
| High Agency   | ✅/⚠️/🚩 | [specific quote or observation] |
| Grit          | ✅/⚠️/🚩 | [specific quote or observation] |
| Impact        | ✅/⚠️/🚩 | [specific quote or observation] |
| Technical     | ✅/⚠️/🚩 | [specific quote or observation] |
| AI-Native     | ✅/⚠️/🚩 | [specific quote or observation] |
| Communication | ✅/⚠️/🚩 | [specific quote or observation] |
| World-Class   | ✅/⚠️/🚩 | [specific quote or observation] |
| Interesting   | ✅/⚠️/🚩 | [specific quote or observation] |

### Role-Specific Fit

[Assessment against role requirements]

### Why We'd Be Thrilled

- [Specific exceptional signals]

### Questions to Probe

- [Specific areas needing verification]

### Verdict

[Must Interview / Worth Exploring / Pass]
```

### Step 4: Summary Table with Links

Always conclude with a summary table including clickable links:

```markdown
## Summary

| Candidate | Score   | Verdict   | Greenhouse  | LinkedIn              |
| --------- | ------- | --------- | ----------- | --------------------- |
| [Name]    | [Score] | [Verdict] | [View](URL) | [Profile](URL) or N/A |
```

---

## Job IDs

Add your Greenhouse job IDs here to filter screening by role:

| ID           | Role              |
| ------------ | ----------------- |
| [JOB_ID_1]   | [Role Name]       |
| [JOB_ID_2]   | [Role Name]       |
| [JOB_ID_3]   | Open Application  |

---

## The Bar

> "90% confidence that this person can do a job only 10% of candidates could do."

We're not asking "can they do the job?" We're asking "would we be thrilled to work with them every day?"

- **Must Interview**: Multiple strong signals across traits, world-class at something, high skill AND will
- **Worth Exploring**: Promising but questions remain — needs interview to resolve
- **Pass**: Missing must-haves, too many red flags, or just "fine"

When in doubt, pass. Better to miss someone good than hire someone mediocre.
