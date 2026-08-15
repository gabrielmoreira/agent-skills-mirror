---
name: developer-onboarding
description: "Shortens developer time-to-first-value with copy-ready quickstarts, Hello World samples, activation funnels, and errors that name the fix. Use when writing getting-started docs, TTFV audits, or tiered sample apps. Do not use for signup-form CRO, pricing pages, or consumer brand campaigns."
version: 1.0.1
---

## When to Use

Use this skill when you need to get developers from signup to working code as fast as possible, then guide them to deeper engagement. Trigger phrases: developer onboarding, time to first value, quickstart guide, hello world tutorial, developer activation, onboarding checklist, sample apps, getting started experience, reduce time to first value.

You have about 10 minutes of developer attention. Every second of confusion, every error message without guidance, every "it should work but doesn't" moment costs you users.

## Prerequisites

Review the `/devmarketing-skills/skills/developer-audience-context` skill to understand your target developers. A hobbyist building side projects needs different onboarding than an enterprise architect evaluating tools for production. Review `/devmarketing-skills/skills/developer-signup-flow` to ensure signup flows smoothly into onboarding.

## Procedure

### 1. Define "First Value"

First value isn't "made an API call." First value is when the developer sees your tool doing something useful for them.

| Tool Type | First Value Moment |
|-----------|-------------------|
| API | Response returns meaningful data |
| SDK | Library performs expected function |
| Database | Query returns results |
| Hosting | App is live and accessible |
| Auth | User successfully logs in |
| Payment | Test charge processes |

### 2. Measure Time to First Value (TTFV)

Track timestamps at each stage:

```
signup_completed: 2024-01-15T10:00:00Z
dashboard_loaded: 2024-01-15T10:00:05Z
api_key_copied: 2024-01-15T10:01:30Z
first_api_call: 2024-01-15T10:04:45Z
first_successful_response: 2024-01-15T10:04:46Z  # TTFV = 4:46
```

**Benchmarks by category:**
- Simple APIs: <5 minutes
- SDKs requiring installation: <10 minutes
- Complex infrastructure: <30 minutes
- Self-hosted: <60 minutes

### 3. Remove TTFV Obstacles

Map every step and eliminate blockers. Common TTFV killers:

1. Email verification before dashboard access
2. API keys hidden in account settings
3. Quickstart assumes dependencies already installed
4. First example requires paid features
5. Error messages without resolution guidance
6. Docs search finds outdated tutorials

**TTFV audit process:**
1. Create new account (fresh browser, no cookies)
2. Screen record your first 30 minutes
3. Note every moment of confusion or friction
4. Time each step
5. Repeat with 5 different developer personas

### 4. Design the Quickstart Checklist

Use this ideal quickstart structure:

```markdown
# Quickstart: [Specific Goal] in 5 Minutes

What you'll build: [Screenshot or description of end result]

Prerequisites:
- Node.js 18+ (check: node --version)
- npm or yarn

## Step 1: Install the SDK
[One command, copy button]

## Step 2: Initialize with your API key
[Code with placeholder, copy button]

## Step 3: Make your first request
[Complete working example, copy button]

## Step 4: See the result
[Expected output shown]

## Next steps
- [Link to common second task]
- [Link to full documentation]
```

**Progress indicators (Stripe style):**
```
Your integration progress:
[x] Create account
[x] Get API keys
[ ] Install SDK
[ ] Make first API call
[ ] Handle webhooks
```

**Contextual next steps (Vercel style):**
```
You've deployed your first site.

What's next?
[ ] Add a custom domain
[ ] Set up environment variables
[ ] Enable analytics
```

### 5. Choose Interactive vs Static Tutorials

**Interactive tutorials work for:**
- Complex setup sequences
- Concepts that benefit from immediate feedback
- Onboarding flows where you control the environment
- Features requiring API keys or credentials

**Interactive tutorial tools:**
- Embedded code editors (CodeSandbox, StackBlitz)
- Terminal emulators (Instruqt, Killercoda)
- In-dashboard walkthroughs (Appcues, Pendo)
- Interactive notebooks (Jupyter, Observable)

**Static docs work better for:**
- Reference documentation
- Copy-paste code snippets
- Steps involving local development
- Content that changes frequently

**Best practice: Offer both.**
```
# Make Your First API Request

## Quick version (copy-paste)
[Code block with copy button]

## Interactive version
[Launch in StackBlitz] [Try in CodeSandbox]

## Video walkthrough
[5-minute embedded video]
```

**Interactive tutorial UX guidelines:**
- Do: Save progress automatically, allow skipping ahead, show estimated time remaining, provide escape hatch to static docs, work in mobile browsers (at least for viewing)
- Don't: Require account creation for tutorials, auto-play videos, lock content behind completed steps, time out idle sessions without warning, require specific IDE or browser

### 6. Build Sample Apps and Templates

Use a tiered approach:

1. **Minimal example** (Hello World): Single file, zero dependencies beyond your SDK, works in 30 seconds. Purpose: Prove the SDK works.
2. **Starter template** (Basic app): Simple folder structure, common patterns demonstrated, works in 5 minutes. Purpose: Starting point for real projects.
3. **Production template** (Full app): Production-ready architecture, auth, error handling, testing included, works in 30 minutes. Purpose: Reference implementation.

**Template organization:**
```
github.com/your-org/
├── examples/
│   ├── minimal/
│   │   ├── node/
│   │   ├── python/
│   │   └── go/
│   ├── starter/
│   │   ├── nextjs/
│   │   ├── express/
│   │   └── fastapi/
│   └── production/
│       ├── saas-starter/
│       └── internal-tool/
```

**Template health checklist:**
- [ ] CI runs against all templates weekly
- [ ] Dependencies updated monthly
- [ ] SDK version pinned and updated with releases
- [ ] README tested by new contributor quarterly
- [ ] Deprecation notices added before removal

### 7. Handle Onboarding Failures Gracefully

**Common failure points:**
1. Installation failures: Dependency conflicts, version mismatches, platform-specific issues
2. Authentication failures: Invalid API key, expired token, wrong environment (test vs production)
3. First request failures: Network issues, CORS problems, rate limiting, invalid request format

**Bad error message:**
```
Error: Request failed with status 401
```

**Good error message:**
```
Authentication failed: Invalid API key

Your API key starts with 'sk_test_' but you're calling the production endpoint.

To fix:
1. Use the production API key (starts with 'sk_live_'), or
2. Change endpoint to https://api.example.com/test/

Docs: https://docs.example.com/auth#environments
```

**Proactive failure prevention (detect common mistakes in real-time):**
```javascript
if (apiKey.startsWith('sk_test_') && endpoint.includes('/v1/')) {
  console.warn(
    'Warning: Using test API key with production endpoint. ' +
    'This will fail. Use production key or test endpoint.'
  );
}
```

**In-dashboard error recovery:**
```
Something went wrong with your integration.

We detected:
- Last API call: 2 hours ago
- Status: 401 Unauthorized
- Likely cause: API key rotated

[Regenerate API Key] [View Error Logs] [Contact Support]
```

### 8. Measure Activation Metrics

Activation = the moment a developer has enough success to keep using your product.

| Product | Activation Definition |
|---------|----------------------|
| Stripe | First successful test charge |
| Twilio | First SMS sent and delivered |
| Auth0 | First user authenticated |
| Vercel | First deploy accessible via URL |
| Algolia | First search returns results |

**Core metrics:**
- Activation rate: `Activated users / Signed up users × 100` (Benchmark: 20-40% for self-serve developer products)
- Time to activation: Median time from signup to activation event (Benchmark: <10 minutes for APIs, <1 hour for infrastructure)
- Activation by cohort: Track weekly or monthly cohorts to identify improvements

**Leading indicators:**

| Leading Indicator | Correlation to Activation |
|-------------------|---------------------------|
| Copied API key | 2x more likely |
| Viewed quickstart | 1.5x more likely |
| Installed SDK | 3x more likely |
| Joined Discord | 2.5x more likely |

**Lagging indicators:**

| Lagging Indicator | Meaning |
|-------------------|---------|
| Day 7 retention | Still using after a week |
| API calls in week 2 | Continued development |
| Upgrade to paid | Perceived enough value |
| Invited team member | Expanding usage |

**Activation funnel example:**
```
Signed up: 1,000
├── Visited dashboard: 950 (95%)
├── Viewed quickstart: 700 (74%)
├── Copied API key: 500 (71%)
├── Made first API call: 350 (70%)
├── Got successful response: 300 (86%)  ← Activation
├── Made 10+ API calls: 150 (50%)
└── Day 7 return: 100 (67%)
```

### 9. Design Onboarding Email Sequences

| Email | Timing | Purpose |
|-------|--------|---------|
| Welcome | Immediate | Confirm signup, provide key links |
| Getting started | +1 hour | Drive first API call if not done |
| Tips | +1 day | Share common patterns |
| Check-in | +3 days | Ask if stuck, offer help |
| Activation push | +7 days | Final nudge if not activated |

**Do:** Include code snippets (syntax highlighted), link to specific docs pages, offer direct reply for help, stop sequence once activated.
**Don't:** Send marketing content during onboarding, require clicks to view content, send more than one email per day, continue sequence after activation.

## Pitfalls

- **Too much context upfront:** Don't start with 500 words of background on OAuth 2.0. Jump to action: install the SDK and make your first authenticated request.
- **Assuming environment:** Don't just say `npm install`. Provide `npm install our-sdk`, `yarn add our-sdk`, and `pnpm add our-sdk`.
- **Hidden prerequisites:** Don't discover in Step 3 that Redis is required. List prerequisites upfront: `Redis 6+ running locally (docker run -p 6379:6379 redis)`.
- **Templates that don't work are worse than no templates.** Maintain them or remove them.
- **Multi-step wizards that can't be skipped.** Developers hate being locked into a flow.
- **"Complete your profile" blocking code access.** Let them see the code first.
- **Documentation requiring search to find quickstart.** The quickstart should be the most prominent link.
- **Quickstarts that assume too much setup.** Test with a clean environment.
- **Error messages without guidance.** Every error should include a fix suggestion or docs link.

## Verification

- [ ] TTFV audit completed with 5 different developer personas
- [ ] Quickstart follows the ideal structure (goal, prerequisites, numbered steps, expected output, next steps)
- [ ] Quickstart tested in a fresh environment with no prior setup
- [ ] All code snippets have copy buttons
- [ ] Error messages include resolution guidance and docs links
- [ ] Templates pass CI weekly
- [ ] Activation metrics tracked (activation rate, time to activation, cohort analysis)
- [ ] Email sequence stops once activated
- [ ] Onboarding flow tested on mobile browsers (at least for viewing)

## Related Skills

- `/devmarketing-skills/skills/developer-signup-flow` - Getting to the onboarding start
- `/devmarketing-skills/skills/developer-audience-context` - Who you're onboarding
- `/devmarketing-skills/skills/free-tier-strategy` - What they can do without paying
