---
name: app-store-optimization
description: "Optimize App Store product pages for search visibility and conversion. Covers App Store Optimization ASO strategy, keyword research and keyword field optimization, app title and subtitle keyword placement, App Store description writing for conversion, promotional text rotation strategy, screenshot caption writing and ordering, in-app review prompt timing with RequestReviewAction and AppStore.requestReview, Custom Product Pages for audience segments, in-app events for search indexing, product page A/B testing experiments, localized metadata optimization across markets, and ratings and review management. Use when improving App Store discoverability, optimizing keyword strategy, writing App Store descriptions or promotional text, planning screenshot captions, setting up Custom Product Pages, configuring in-app review prompts, creating in-app events, running product page optimization tests, or developing a ratings management strategy."
---

# App Store Optimization (ASO)

Search visibility and conversion optimization for App Store product pages. This skill covers strategic metadata decisions -- which keywords to target, how to structure descriptions for conversion, and how to use Custom Product Pages and in-app events for discoverability. For metadata compliance rules (character limits, screenshot device requirements, rejection triggers), see the `app-store-review` skill.

## Contents

- [Overview](#overview)
- [Title and Subtitle Strategy](#title-and-subtitle-strategy)
- [Keyword Field Strategy](#keyword-field-strategy)
- [Description Structure](#description-structure)
- [Promotional Text](#promotional-text)
- [Screenshot and Preview Optimization](#screenshot-and-preview-optimization)
- [In-App Review Prompts](#in-app-review-prompts)
- [Custom Product Pages](#custom-product-pages)
- [In-App Events](#in-app-events)
- [Product Page Optimization](#product-page-optimization)
- [Ratings and Review Management](#ratings-and-review-management)
- [Localized Metadata Optimization](#localized-metadata-optimization)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Overview

ASO has two pillars:

1. **Search visibility** -- ranking for relevant queries so users find the app.
2. **Conversion rate** -- convincing users who land on the product page to download.

Apply this skill when a developer asks about improving discoverability, keyword strategy, download conversion, or any product page element that affects either pillar.

For metadata format rules and compliance guardrails, see the `app-store-review` skill. This skill assumes the developer is working within those constraints and focuses on strategy.

## Title and Subtitle Strategy

Apple indexes the app name and subtitle for search. Together they provide 60 characters (30 + 30) of indexed, high-visibility keyword real estate.

### Positioning framework

| Pattern | When to use | Example |
|---------|-------------|---------|
| **Brand -- Keyword** | Established brand with recognition | `Notion -- Notes & Docs` |
| **Keyword -- Brand** | New app competing on category terms | `Budget Tracker -- Pennywise` |
| **Brand + Keyword blend** | Brand name contains a keyword naturally | `Headspace: Sleep & Meditation` |

### Rules

- Do not repeat words between the name and subtitle -- Apple indexes both, so duplicates waste characters.
- Front-load the highest-value keyword in whichever field has more room.
- Avoid generic filler words ("the", "best", "app") -- they consume space without search value.
- The subtitle should communicate the primary value proposition, not a tagline.

## Keyword Field Strategy

The keyword field is 100 characters, comma-separated, no spaces after commas. See the `app-store-review` skill for the full format rules. This section focuses on which keywords to choose and how to prioritize them.

### Research process

1. **Competitor audit** -- identify the top 5-10 competitors in the category and note which keywords appear in their titles, subtitles, and descriptions.
2. **Category analysis** -- identify terms users associate with the app's category that competitors may be missing.
3. **Search Ads signals** -- run Apple Search Ads discovery campaigns to surface high-intent queries with actual impression and tap data.
4. **Iterate each release** -- update keywords based on Search Ads performance, App Analytics impressions, and conversion data.

### Prioritization

Rank candidate keywords by three factors:

| Factor | Weight | Signal |
|--------|--------|--------|
| **Relevance** | Highest | Does the keyword describe what the app actually does? |
| **Search volume** | Medium | Are users actually searching for this term? |
| **Competition** | Lower | How many apps target this keyword? |

Relevance always wins. A high-volume keyword that does not describe the app will get impressions but not conversions.

### Tactical rules

- Deduplicate against title and subtitle -- Apple already indexes those words.
- Use singular forms only -- Apple matches both singular and plural from singular.
- Omit the category name -- Apple adds the app's primary category to search automatically.
- Omit spaces after commas -- they count against the 100-character limit.
- Consider abbreviations and common misspellings if they are genuine search terms.
- Place highest-value keywords first -- there is some evidence that position affects ranking weight.

**See:** [references/keyword-research-methodology.md](references/keyword-research-methodology.md) for the full research process, scoring framework, and indexing details.

## Description Structure

The App Store description does not affect search ranking -- Apple does not index it for keyword matching. It does affect conversion: users who expand the description are evaluating whether to download.

### Four-part structure

1. **Hook** (first 1-3 lines) -- the only text visible before the "more" fold. Lead with the strongest benefit or differentiator. This is the most important copy on the page.
2. **Feature highlights** -- 4-6 short feature descriptions. Use Unicode bullet characters (•) since the App Store does not render markdown. Focus on outcomes, not technical details.
3. **Social proof** -- awards, press quotes, user count milestones, or notable ratings. One or two lines.
4. **Call to action** -- a closing line encouraging the download. Keep it short and benefit-focused.

### Formatting notes

- The App Store does not render markdown, HTML, or rich text. Use plain text with Unicode characters for structure.
- Short paragraphs with line breaks between them. Walls of text kill conversion.
- Write per locale -- translate the structure, not the words. See [Localized Metadata Optimization](#localized-metadata-optimization).

## Promotional Text

Promotional text is the only metadata field changeable without submitting a new binary. It appears above the description and is limited to 170 characters.

### Rotation strategy

Update promotional text to match current context:

| Trigger | Example text |
|---------|-------------|
| **Feature launch** | `New: Collaborate in real time with shared workspaces` |
| **Seasonal event** | `Plan your holiday travel -- route sharing now available` |
| **Award or press** | `Winner of Apple Design Award 2025` |
| **Sale or promotion** | `Premium features free through January` |
| **In-app event** | `Join the Spring Challenge -- starts March 15` |

Do not leave promotional text static across releases. If there is nothing timely to promote, rotate between the app's strongest selling points.

## Screenshot and Preview Optimization

Most users never scroll past the first 3 visible screenshots. These slots determine whether a user engages with the full product page or moves on.

### First 3 screenshots

- Lead with the primary value proposition -- the screen that best demonstrates why someone should download.
- Never place onboarding, splash, or loading screens in the first 3 slots.
- Each screenshot should demonstrate a different benefit or feature.

### Caption writing

- Write benefit-oriented captions, not feature labels. "Never miss a deadline" converts better than "Calendar View".
- Keep captions to 2-5 words above the screenshot and one short line below.
- Use action verbs: "Track", "Share", "Discover", "Build".

### Ordering strategy

| Slot | Purpose |
|------|---------|
| 1 | Primary value proposition -- the single best reason to download |
| 2 | Core differentiator -- what sets this app apart from competitors |
| 3 | Secondary feature -- the next strongest selling point |
| 4+ | Supporting features, social proof, or edge cases |

### App preview video

If a preview video is present, it occupies the first slot. The first frame becomes the poster image when autoplay is disabled -- choose a frame that works as a standalone screenshot.

For screenshot device requirements and compliance rules, see the `app-store-review` skill.

## In-App Review Prompts

StoreKit provides two APIs for requesting ratings:

**SwiftUI** -- use `RequestReviewAction` via the environment:

```swift
@Environment(\.requestReview) private var requestReview

func onTaskCompleted() {
    requestReview()
}
```

**UIKit** -- use `AppStore.requestReview(in:)`:

```swift
if let scene = view.window?.windowScene {
    AppStore.requestReview(in: scene)
}
```

### System behavior

- The system enforces a maximum of 3 prompts per 365-day period per device for users who have not yet rated the app.
- The API is a request, not a guarantee -- StoreKit decides whether to show the prompt.
- During development, the prompt always appears. In TestFlight, it never appears.

### Prompt timing

| Good triggers | Bad triggers |
|---------------|-------------|
| After completing a meaningful task | On first launch |
| After achieving a milestone or streak | Immediately after an error or crash |
| After a positive in-app moment | During onboarding |
| After the user has been active for several sessions | In response to a button tap |

Do not gate the prompt behind a "Rate this app?" dialog -- Apple discourages intercepting the system prompt and may reject apps that pre-screen.

### Persistent review link

For a settings screen or "Rate us" option, link directly to the App Store review page using the URL format:

```
https://apps.apple.com/app/id{APP_ID}?action=write-review
```

This opens the review writing screen directly and is not subject to the 3x/year system limit.

For the full StoreKit API surface, see the `storekit` skill.

## Custom Product Pages

Custom Product Pages allow up to 35 variant product pages per app. Each variant can have different screenshots, app preview videos, and promotional text -- tailored to a specific audience or acquisition channel.

### Use cases

| Audience | Customization |
|----------|--------------|
| **Paid search ads** | Screenshots matching the search intent of the ad group keywords |
| **Social media campaign** | Screenshots and captions tailored to the campaign creative |
| **Feature-specific landing** | Lead screenshot showing the specific feature being promoted |
| **Seasonal campaign** | Seasonal screenshots and promotional text |

### Setup

- Each Custom Product Page gets a unique App Store URL usable in ad campaigns, deep links, and web pages.
- Pages can be localized independently.
- Create pages in App Store Connect under the Custom Product Pages tab.
- Name pages descriptively for internal tracking (e.g., "Search-FitnessTracking", "Social-HolidayCampaign").

**See:** [references/product-page-variants.md](references/product-page-variants.md) for setup details, URL structure, and campaign mapping strategy.

## In-App Events

In-app events surface in App Store search results, on the Today tab, and in personalized recommendations. They increase visibility during the event window and can re-engage lapsed users.

### Event types

| Badge | When to use |
|-------|-------------|
| **Challenge** | Time-limited goals users can work toward |
| **Competition** | Head-to-head or leaderboard contests |
| **Live Event** | Real-time experiences (concerts, sports, streams) |
| **Major Update** | Significant new features or redesigns |
| **New Season** | Seasonal content refreshes |
| **Premiere** | First-time content availability |
| **Special Event** | Limited-time promotions or celebrations |

### Metadata limits

| Field | Limit |
|-------|-------|
| Event name | 30 characters |
| Short description | 50 characters |
| Long description | 120 characters |
| Event card image | Required (1920x1080 or similar 16:9) |

### Strategy

- Schedule events around feature releases, seasonal moments, or content drops.
- Use the event name and short description as additional keyword surfaces -- Apple indexes event metadata for search.
- Events appear on the product page and in search results, giving the app a visual badge that increases tap-through rate.
- Overlap events strategically: end the current event as the next one begins to maintain continuous search visibility.

**See:** [references/product-page-variants.md](references/product-page-variants.md) for event scheduling templates.

## Product Page Optimization

App Store Connect provides native A/B testing for product page elements.

### What can be tested

- App icon (alternate icons)
- Screenshots (order, content, captions)
- App preview video

Only one treatment can be tested at a time. The default product page serves as the control.

### Test design

- Run tests for a minimum of 7 days to account for day-of-week variation.
- Ensure sufficient traffic for statistical significance -- low-traffic apps may need longer test durations.
- Test one variable at a time (e.g., screenshot order OR caption copy, not both simultaneously).
- Changes to the default locale only affect that locale.

### Interpreting results

- Focus on conversion rate lift (impressions-to-downloads), not absolute download numbers.
- App Store Connect shows confidence intervals -- do not apply a winning treatment until the test reaches statistical significance.
- After applying a winner, wait before starting the next test to establish a clean baseline.

## Ratings and Review Management

Average rating affects both conversion and search ranking. The threshold effects are significant: apps below 4.0 stars see measurably lower conversion, and apps above 4.5 stars convert noticeably better.

### Review response strategy

- Respond to negative reviews in App Store Connect -- a professional response improves perceived quality even without changing the rating number.
- Acknowledge the issue, state what is being done (or has been fixed), and keep the tone neutral.
- Turn negative reviews into keyword signals -- users describe problems using search-relevant language.

### Rating reset

When submitting a new version, you can choose to reset the displayed rating. Use this strategically:

| Situation | Recommendation |
|-----------|---------------|
| Current rating is significantly below the app's quality after major improvements | Reset |
| Current rating is strong (4.5+) | Do not reset |
| Bug fix release with no quality improvement | Do not reset |
| Major redesign with mixed early feedback expected | Wait for stabilization, then reset on a subsequent update |

## Localized Metadata Optimization

Localizing ASO is not the same as translating the app UI. Keyword strategy, descriptions, and screenshot captions must be researched and written per market, not machine-translated from the primary locale.

### Key principles

- **Research keywords per market.** The most-searched term for "photo editor" in Japanese is not a direct translation of "photo editor."
- **Rewrite descriptions per locale.** Adapt the hook-features-proof-CTA structure to local conventions and selling points.
- **Some markets index English keywords.** Japan, South Korea, and several other markets index both the local language and English keyword fields. Use this to capture additional search terms.
- **Localize screenshot captions.** Captions in the user's language convert better than untranslated English.

For in-app string localization (String Catalogs, FormatStyle, right-to-left layout), see the `ios-localization` skill.

## Common Mistakes

1. **Duplicating title words in the keyword field.** Apple indexes the title and subtitle automatically -- repeating those words in the keyword field wastes characters.
2. **Writing feature-descriptive screenshot captions instead of benefit-oriented ones.** "Calendar View" converts worse than "Never miss a deadline" -- lead with the user outcome.
3. **Translating keywords instead of researching per-market terms.** Direct translation misses local search behavior and high-volume terms specific to each market.
4. **Prompting for reviews after a negative experience.** Calling `requestReview()` after an error, a failed transaction, or during onboarding generates low ratings.
5. **Ignoring the first three screenshot slots.** Most users never scroll -- placing an onboarding or splash screen first wastes the highest-impact real estate.
6. **Never rotating promotional text.** Promotional text is the only field changeable without a new build -- leaving it static misses conversion opportunities.
7. **Running A/B tests with insufficient duration.** Product page optimization tests need at least 7 days and meaningful traffic to reach statistical significance.
8. **Adding spaces after commas in the keyword field.** Spaces count against the 100-character limit -- use `keyword1,keyword2` not `keyword1, keyword2`.
9. **Using identical screenshots for every Custom Product Page.** Custom Product Pages exist to tailor messaging per audience segment -- reusing identical assets defeats the purpose.
10. **Not responding to negative App Store reviews.** Unanswered negative reviews signal abandonment to prospective users and miss an opportunity to demonstrate responsiveness.

## Review Checklist

- [ ] Title uses high-value keyword alongside brand name; no words repeated in subtitle
- [ ] Subtitle communicates primary value proposition within 30 characters
- [ ] Keyword field uses all 100 characters; no spaces after commas; no duplicates of title/subtitle words; singular forms only
- [ ] Description follows hook-features-proof-CTA structure; first 3 lines compelling before the fold
- [ ] Promotional text is current and relevant to the latest release or event
- [ ] First 3 screenshots show highest-value screens with benefit-oriented captions
- [ ] App preview video (if present) leads with the core feature in the first 5 seconds
- [ ] `requestReview()` is placed after a positive user moment, not on first launch or after errors
- [ ] Custom Product Pages created for distinct acquisition channels with tailored screenshots
- [ ] In-app events configured for upcoming launches, seasons, or feature releases
- [ ] Metadata localized with per-market keyword research for all supported locales
- [ ] Compliance cross-check: all metadata passes the `app-store-review` skill checklist before submission

## References

- Keyword research methodology: [references/keyword-research-methodology.md](references/keyword-research-methodology.md)
- Custom Product Pages, A/B testing, and in-app events: [references/product-page-variants.md](references/product-page-variants.md)
