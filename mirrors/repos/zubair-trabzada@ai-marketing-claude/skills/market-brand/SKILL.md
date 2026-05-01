# Brand Voice Analysis and Guidelines Generation

## Skill Purpose
Analyze a brand's voice, tone, and messaging across all available channels and generate a comprehensive brand voice guidelines document. This skill examines how a brand communicates, identifies patterns and inconsistencies, and produces actionable guidelines that any writer or marketer can follow to maintain brand consistency.

## When to Use
- User wants to understand or document a brand's voice
- User needs brand voice guidelines for a team, freelancers, or agency
- User wants to ensure consistency across marketing channels
- User is rebranding or refining their brand identity
- User wants to compare their brand voice to competitors
- Triggered by `/market brand <url>` or `/market brand`

## How to Execute

### Step 1: Gather Source Material
To analyze a brand's voice, examine content from multiple sources. Prioritize in this order:

**Primary Sources (must analyze):**
1. **Homepage** -- The most curated representation of the brand
2. **About page** -- How the brand describes itself
3. **Product/service pages** -- How they present their offerings

**Secondary Sources (analyze if available):**
4. **Blog posts** (at least 3-5 recent posts)
5. **Social media profiles** (bio, recent posts, engagement style)
6. **Email newsletters** (welcome email, recent sends)
7. **Customer-facing copy** (error messages, onboarding flows, help docs)

**Tertiary Sources:**
8. **Job postings** -- Reveals internal culture and values
9. **Press releases** -- Formal communication style
10. **Ad copy** -- Paid messaging approach
11. **Video scripts or podcast transcripts** -- Spoken brand voice

Use browser tools or the analyze_page.py script to access web content. For social media, check the website for social links and analyze the linked profiles.

### Step 2: Voice Dimension Analysis
Map the brand's voice along four primary dimensions. Each dimension is a spectrum, not a binary.

#### Dimension 1: Formal <-----> Casual
Where does the brand fall on the formality spectrum?

| Signal | Formal | Casual |
|---|---|---|
| Contractions | Avoids them ("do not", "cannot") | Uses them freely ("don't", "can't") |
| Sentence structure | Complex, longer sentences | Short, punchy sentences |
| Vocabulary | Professional, industry-standard | Conversational, everyday words |
| Greetings | "Dear valued customer" | "Hey there!" |
| Pronouns | Third person ("the company", "one") | First/second person ("we", "you") |
| Humor | Rare or absent | Frequent, natural |
| Slang/colloquialisms | Never | Occasionally or frequently |

**Score: 1 (extremely formal) to 10 (extremely casual)**

**Evidence required:** Quote 3-5 specific examples from the source material that support your rating.

#### Dimension 2: Serious <-----> Playful
How much levity does the brand inject into its communication?

| Signal | Serious | Playful |
|---|---|---|
| Tone | Authoritative, measured | Light-hearted, fun |
| Metaphors | Rare, conservative | Creative, unexpected |
| Exclamation marks | Rare | Frequent |
| Emoji use | Never | Sometimes or often |
| Wordplay/puns | Never | Enjoys them |
| Error messages | "An error has occurred" | "Oops! Something went sideways" |
| Self-deprecation | Never | Occasionally |

**Score: 1 (extremely serious) to 10 (extremely playful)**

#### Dimension 3: Technical <-----> Simple
How much domain expertise does the brand assume in its audience?

| Signal | Technical | Simple |
|---|---|---|
| Jargon | Uses industry terms freely | Avoids or explains all jargon |
| Acronyms | Uses without definition | Spells out on first use |
| Detail level | In-depth explanations | High-level overviews |
| Audience assumption | Expert audience | General audience |
| Data/statistics | Frequent, detailed | Occasional, simplified |
| Examples | Complex, domain-specific | Simple, relatable analogies |

**Score: 1 (extremely technical) to 10 (extremely simple)**

#### Dimension 4: Reserved <-----> Bold
How much personality and confidence does the brand project?

| Signal | Reserved | Bold |
|---|---|---|
| Claims | Hedged ("we believe", "may help") | Direct ("we guarantee", "the best") |
| Opinions | Neutral, balanced | Strong, opinionated |
| Competitive references | Avoids mentioning competitors | Directly compares |
| Personality | Professional, understated | Distinctive, memorable |
| Promises | Conservative | Ambitious |
| Controversy | Avoids | Embraces when aligned with values |

**Score: 1 (extremely reserved) to 10 (extremely bold)**

### Step 3: Tone Spectrum Mapping

Beyond the four dimensions, map how the brand's tone shifts across different contexts:

| Context | Typical Tone | Example |
|---|---|---|
| Homepage | [Confident/Welcoming/Urgent/etc.] | "[quote from homepage]" |
| Product description | [Informative/Persuasive/Technical/etc.] | "[quote]" |
| Blog post | [Educational/Conversational/Authoritative/etc.] | "[quote]" |
| Social media | [Casual/Engaging/Promotional/etc.] | "[quote]" |
| Error/404 page | [Apologetic/Humorous/Helpful/etc.] | "[quote]" |
| Email subject lines | [Direct/Curious/Urgent/etc.] | "[quote]" |
| CTA buttons | [Action-oriented/Benefit-driven/Urgent/etc.] | "[quote]" |
| Customer support | [Empathetic/Professional/Friendly/etc.] | "[quote]" |

### Step 4: Brand Personality Framework

Map the brand to one of five core personality archetypes (brands may blend 1-2):

#### The 5 Archetypes

**1. The Authority**
- Characteristics: Expert, trustworthy, data-driven, established
- Voice: Confident but not arrogant, educational, precise
- Industries: Finance, healthcare, B2B enterprise, legal, consulting
- Example brands: McKinsey, IBM, Mayo Clinic
- Key phrases: "Research shows...", "Our experts...", "Industry-leading..."

**2. The Innovator**
- Characteristics: Forward-thinking, disruptive, visionary, tech-savvy
- Voice: Exciting, future-focused, sometimes provocative
- Industries: Tech, SaaS, startups, renewable energy
- Example brands: Tesla, Stripe, Notion
- Key phrases: "Reimagine...", "The future of...", "We're building..."

**3. The Friend**
- Characteristics: Warm, approachable, helpful, relatable
- Voice: Conversational, empathetic, inclusive, encouraging
- Industries: Consumer products, education, community platforms
- Example brands: Mailchimp, Slack, Duolingo
- Key phrases: "We get it...", "You've got this...", "Here to help..."

**4. The Rebel**
- Characteristics: Bold, challenging conventions, irreverent, passionate
- Voice: Direct, opinionated, sometimes confrontational, memorable
- Industries: Lifestyle, fitness, creative industries, direct-to-consumer
- Example brands: Nike, Oatly, Cards Against Humanity
- Key phrases: "Stop settling for...", "The truth is...", "We're done with..."

**5. The Guide**
- Characteristics: Wise, patient, methodical, trustworthy
- Voice: Clear, instructional, supportive, knowledgeable
- Industries: Education, professional development, tools, platforms
- Example brands: HubSpot, Khan Academy, Ahrefs
- Key phrases: "Here's how to...", "Step by step...", "The complete guide to..."

**Assessment:**
- Primary archetype: [which one and why]
- Secondary archetype: [if applicable]
- Archetype fit: [Strong/Moderate/Weak -- how well does the brand embody this archetype?]

### Step 5: Vocabulary Analysis

Identify patterns in the brand's word choices:

#### Words They Use Frequently
Analyze all source material and identify the 15-20 most characteristic words or phrases. Organize by category:

**Action words:** (verbs they favor)
- e.g., "build", "scale", "transform", "streamline"

**Descriptive words:** (adjectives they use)
- e.g., "powerful", "simple", "enterprise-grade", "effortless"

**Value words:** (words that reflect their values)
- e.g., "transparent", "sustainable", "inclusive", "innovative"

**Industry-specific terms:**
- e.g., "workflow", "pipeline", "conversion", "engagement"

#### Words They Avoid
Identify words that are notably absent or that would feel out of character:

- Words that are too casual for the brand (if formal)
- Words that are too technical for the brand (if simple)
- Competitor terminology they deliberately avoid
- Industry cliches they seem to sidestep

#### Signature Phrases
Does the brand have any recurring phrases, taglines, or linguistic patterns?

- Tagline: [if they have one]
- Recurring phrases: [patterns you notice]
- Linguistic patterns: [e.g., always starts sentences with verbs, uses dashes frequently, favors short paragraphs]

### Step 6: Competitor Voice Comparison

Compare the brand's voice to 2-3 key competitors:

**Voice Comparison Matrix:**
| Dimension | [Brand] | Competitor 1 | Competitor 2 | Competitor 3 |
|---|---|---|---|---|
| Formal <> Casual | X/10 | X/10 | X/10 | X/10 |
| Serious <> Playful | X/10 | X/10 | X/10 | X/10 |
| Technical <> Simple | X/10 | X/10 | X/10 | X/10 |
| Reserved <> Bold | X/10 | X/10 | X/10 | X/10 |
| Primary Archetype | [type] | [type] | [type] | [type] |

**Differentiation Assessment:**
- How distinct is the brand's voice from competitors?
- Where do voices overlap? (potential differentiation opportunity)
- What voice territory is unoccupied in the competitive landscape?
- Specific recommendations for vocal differentiation

### Step 7: Consistency Audit

Assess voice consistency across all analyzed channels:

| Channel | Voice Consistency | Notes |
|---|---|---|
| Homepage | Consistent/Mostly/Inconsistent | [specific observations] |
| About page | Consistent/Mostly/Inconsistent | [notes] |
| Blog | Consistent/Mostly/Inconsistent | [notes] |
| Social media | Consistent/Mostly/Inconsistent | [notes] |
| Email | Consistent/Mostly/Inconsistent | [notes] |
| Product pages | Consistent/Mostly/Inconsistent | [notes] |

**Common Consistency Issues:**
- Different writers creating noticeably different tones
- Social media voice drastically different from website
- Formal website copy but casual email newsletters
- Blog content written in a completely different voice than product pages
- Error messages or microcopy that feels off-brand
- Old pages that haven't been updated to match current brand voice

**Overall Consistency Score:** X/10

### Step 8: Brand Messaging Hierarchy

Document the brand's messaging from most distilled to most expanded:

#### Level 1: Tagline (under 10 words)
The most compressed form of the brand message.
- Current: "[existing tagline or suggested one]"
- Assessment: Does it capture the core value proposition?

#### Level 2: Value Propositions (1 sentence each)
3-5 core value propositions that support the brand promise.
1. "[Value prop 1]"
2. "[Value prop 2]"
3. "[Value prop 3]"

#### Level 3: Elevator Pitch (30 seconds / 75 words)
A conversational explanation of what the brand does and why it matters.
"[Draft elevator pitch based on analyzed content]"

#### Level 4: Boilerplate (100-150 words)
The standard "about us" paragraph used in press releases, email signatures, and speaker bios.
"[Draft boilerplate based on analyzed content]"

#### Level 5: Full Brand Story (300-500 words)
The complete narrative of who the brand is, what they stand for, and why they exist.
- Current status: [Exists/Partial/Missing]
- Recommendations for improvement

### Step 9: Generate Brand Voice Documentation

Create the comprehensive Do's and Don'ts guide:

#### Voice Chart

```
OUR VOICE IS:                    OUR VOICE IS NOT:
--------------------------------------------------
[Characteristic 1]              [Anti-characteristic 1]
e.g., "Confident"               e.g., "Arrogant"

[Characteristic 2]              [Anti-characteristic 2]
e.g., "Helpful"                 e.g., "Condescending"

[Characteristic 3]              [Anti-characteristic 3]
e.g., "Clear"                   e.g., "Dumbed down"

[Characteristic 4]              [Anti-characteristic 4]
e.g., "Bold"                    e.g., "Aggressive"
```

#### Writing Do's and Don'ts

**DO:**
- [Specific writing instruction based on analysis]
- [Example: "Use contractions to sound natural (we're, you'll, it's)"]
- [Example: "Lead with the benefit, not the feature"]
- [Example: "Use active voice in all headlines and CTAs"]
- [Example: "Address the reader directly with 'you' and 'your'"]

**DON'T:**
- [Specific anti-patterns based on analysis]
- [Example: "Don't use jargon without explaining it"]
- [Example: "Don't use passive voice in calls-to-action"]
- [Example: "Don't use exclamation marks more than once per paragraph"]
- [Example: "Don't start sentences with 'We' -- focus on the customer"]

### Step 10: Copy Samples in Identified Voice

Provide 5-8 sample copy pieces written in the identified brand voice so the team has concrete examples to reference:

**1. Homepage Headline:**
"[Sample headline in the brand voice]"

**2. Product Description Paragraph:**
"[Sample product description in the brand voice]"

**3. Blog Post Opening:**
"[Sample blog intro in the brand voice]"

**4. Social Media Post:**
"[Sample social post in the brand voice]"

**5. Email Subject Line:**
"[Sample subject line in the brand voice]"

**6. CTA Button Text:**
"[Sample CTA text in the brand voice]"

**7. Error Message:**
"[Sample error message in the brand voice]"

**8. Customer Thank You Message:**
"[Sample thank you message in the brand voice]"

## Output Format

Generate a file called `BRAND-VOICE.md` with:

```markdown
# Brand Voice Guidelines
## [Brand Name]
### Analysis Date: [Date]

---

## Voice Summary
[2-3 sentence summary of the brand voice, personality, and key characteristics]

---

## Voice Dimensions

### Formal <-----> Casual: [X/10]
[Evidence and explanation]

### Serious <-----> Playful: [X/10]
[Evidence and explanation]

### Technical <-----> Simple: [X/10]
[Evidence and explanation]

### Reserved <-----> Bold: [X/10]
[Evidence and explanation]

### Visual Voice Map
```
Formal                                    Casual
|----[X]----------------------------------|
Serious                                   Playful
|--------[X]------------------------------|
Technical                                 Simple
|------------------[X]--------------------|
Reserved                                  Bold
|------------[X]--------------------------|
```

---

## Brand Personality
- Primary Archetype: [Archetype]
- Secondary Archetype: [Archetype]
- [Explanation and evidence]

---

## Tone by Context
| Context | Tone | Example |
|---|---|---|
| [context] | [tone] | "[example]" |

---

## Vocabulary

### Words We Use
[Organized word lists]

### Words We Avoid
[Words that don't fit the brand]

### Signature Phrases
[Recurring patterns and phrases]

---

## Voice Chart
| Our Voice IS | Our Voice IS NOT |
|---|---|
| [trait] | [anti-trait] |

---

## Writing Guidelines

### Do's
- [specific guidelines]

### Don'ts
- [specific anti-patterns]

---

## Brand Messaging Hierarchy

### Tagline
[tagline]

### Value Propositions
1. [value prop]

### Elevator Pitch
[pitch]

### Boilerplate
[boilerplate]

---

## Copy Samples
[8 examples of copy in the brand voice]

---

## Competitor Voice Comparison
[Comparison matrix and differentiation analysis]

---

## Consistency Audit
[Channel-by-channel assessment]
- Overall Consistency Score: [X/10]

---

## Recommendations
### Immediate Actions
1. [recommendation]

### Voice Evolution Opportunities
1. [recommendation]

### Consistency Improvements
1. [recommendation]
```

## Key Principles
- Brand voice analysis requires reading like a detective. Every word choice, punctuation decision, and sentence structure reveals something about how the brand wants to be perceived.
- Always provide EVIDENCE for every assessment. Don't just say "the brand is casual" -- quote specific examples that prove it.
- The brand voice guide should be usable by someone who has never worked with the brand before. A new copywriter should be able to read this document and write on-brand content.
- Copy samples are the most valuable part of the deliverable. People learn voice by example, not by description. Make the samples diverse (headlines, body copy, social, email, error messages) so writers have references for every context.
- Voice and tone are different. Voice is the consistent personality. Tone shifts based on context (a customer complaint response is different from a product launch announcement, but both should be in the same voice).
- If the brand's voice is inconsistent across channels, frame it as an opportunity to strengthen their brand, not as a failure. Consistency issues are common and fixable.
- If the user has run `/market competitors` previously, use that data for the competitor voice comparison section.
- The voice dimensions should be plotted visually (text-based spectrum) so stakeholders can quickly understand the positioning at a glance.
