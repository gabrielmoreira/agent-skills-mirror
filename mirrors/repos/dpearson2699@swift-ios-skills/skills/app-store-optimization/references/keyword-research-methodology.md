# Keyword Research Methodology

Step-by-step process for identifying, scoring, and maintaining the keyword field for App Store search optimization.

## Contents

- [How Apple Indexes Metadata](#how-apple-indexes-metadata)
- [Research Process](#research-process)
- [Keyword Scoring Framework](#keyword-scoring-framework)
- [Slot Allocation Strategy](#slot-allocation-strategy)
- [Seasonal Keyword Rotation](#seasonal-keyword-rotation)
- [Before and After Examples](#before-and-after-examples)

## How Apple Indexes Metadata

Apple indexes different metadata fields with different weights and behaviors:

| Field | Indexed for search? | Controllable per version? | Notes |
|-------|---------------------|--------------------------|-------|
| App name | Yes -- high weight | Yes (with new binary) | 30 characters. Strongest ranking signal. |
| Subtitle | Yes -- high weight | Yes (with new binary) | 30 characters. Second strongest signal. |
| Keyword field | Yes -- medium weight | Yes (with new binary) | 100 characters. Primary keyword surface. |
| In-app purchase display names | Yes -- lower weight | Yes (with IAP update) | Each IAP name is indexed. |
| In-app event name | Yes -- during event window | Yes (per event) | Only indexed while the event is active. |
| Description | No | Yes (with new binary) | Not indexed for search. Affects conversion only. |
| Promotional text | No | Yes (anytime, no binary) | Not indexed. Conversion only. |
| Developer name | Yes -- low weight | Account-level | Rarely useful for keyword strategy. |
| Category | Yes -- automatic | Yes (with new binary) | Apple adds the category term automatically. Do not repeat it in keywords. |

### Indexing behavior details

- Apple matches both singular and plural forms from a singular keyword. Always use singular.
- Apple does not match partial words -- "photo" does not match "photography". Include both if both are search terms.
- Title and subtitle words are indexed with the highest weight. Repeating them in the keyword field has no additional benefit and wastes characters.
- Apple combines words across the title, subtitle, and keyword field when matching multi-word queries. "Budget" in the title and "tracker" in the keyword field will match "budget tracker" as a search query.

## Research Process

### Step 1: Competitor audit

Identify the top 5-10 apps ranking for the primary category terms. For each competitor, note:

- Title and subtitle keywords
- Visible keyword patterns (terms that appear frequently across top-ranking apps)
- Gaps -- relevant terms that competitors are not targeting

Use App Store search autocomplete to discover what users actually type. Start typing a category term and note the suggested completions.

### Step 2: Category analysis

List every term a user might associate with the app's functionality:

- Primary function terms (what the app does)
- Use case terms (why a user would want it)
- Audience terms (who the user is)
- Adjacent terms (related activities or workflows)

Filter this list against competitor findings. Terms that appear in many competitor titles are high-volume but high-competition. Terms that appear in autocomplete but not in competitor metadata represent opportunities.

### Step 3: Search Ads discovery

Run Apple Search Ads discovery campaigns with broad-match keywords matching the primary function. After 2-4 weeks of data:

- Export the search term report to see actual queries that triggered impressions.
- Sort by tap-through rate (TTR) to identify high-intent terms.
- Sort by conversion rate to identify terms where users who find the app actually download it.
- Add high-performing discovered terms to the keyword field.

### Step 4: Iteration cycle

With each app update:

1. Review App Analytics for keyword impressions, tap-through rates, and conversion rates.
2. Identify underperforming keywords (low impressions or low TTR) and replace them.
3. Test new terms discovered through Search Ads or category changes.
4. Check if competitor metadata has shifted -- new competitors or renamed apps can change the keyword landscape.

## Keyword Scoring Framework

Score each candidate keyword on three dimensions:

| Dimension | Score range | How to assess |
|-----------|-------------|---------------|
| **Relevance** | 1-5 | Does the keyword describe what the app actually does? 5 = core function, 1 = tangentially related |
| **Volume** | 1-5 | Is this term frequently searched? Use Search Ads impression data as a proxy. 5 = high impressions, 1 = minimal |
| **Difficulty** | 1-5 | How many established apps target this term? 5 = low competition (good), 1 = dominated by major apps |

**Decision rule:** Include a keyword only if Relevance >= 3. Among qualifying keywords, prioritize by (Relevance x 2) + Volume + Difficulty. This weights relevance heavily while still favoring discoverable, winnable terms.

**Disqualify keywords that:**
- Do not describe the app's actual functionality (Relevance < 3)
- Are competitor brand names (violates App Store guidelines)
- Duplicate a word already in the title or subtitle
- Are the app's primary category name (Apple adds it automatically)

## Slot Allocation Strategy

The 100-character keyword field requires careful allocation. Here are allocation patterns for different app types:

### Example: Fitness tracking app

Title: `FitTrack -- Workout Log` (23 chars used)
Subtitle: `Exercise & Activity Stats` (25 chars used)

Keyword field strategy -- do not repeat: fittrack, workout, log, exercise, activity, stats

```
gym,training,health,run,step,calorie,weight,strength,cardio,hiit,yoga,plank,squat,routine,progress
```

(96 characters -- 4 remaining, all unique against title/subtitle)

### Example: Photo editing app

Title: `PixelPop -- Photo Editor` (24 chars used)
Subtitle: `Filters & Retouch Tools` (23 chars used)

Keyword field -- do not repeat: pixelpop, photo, editor, filter, retouch, tool

```
selfie,portrait,collage,crop,blur,preset,enhance,adjust,brightness,contrast,saturation,beauty,skin
```

(99 characters -- all unique against title/subtitle)

### Allocation principles

- Each comma costs 1 character. Fewer, longer keywords are not inherently better than more, shorter ones -- Apple matches individual words, not phrases.
- If two keywords are always searched together (e.g., "meal prep"), include both words separately ("meal,prep") since Apple combines across fields anyway.
- Reserve 5-10 characters for experimental keywords that rotate each release based on performance data.

## Seasonal Keyword Rotation

Some keywords have seasonal search volume spikes. Plan rotation around predictable events:

| Season/Event | Example keywords to add | When to deploy |
|-------------|------------------------|----------------|
| New Year | resolution,goal,habit,new year | December release |
| Back to school | student,school,study,planner | July/August release |
| Holiday shopping | gift,holiday,deal,wish list | October/November release |
| Summer fitness | outdoor,running,summer,beach | April/May release |
| Tax season | tax,receipt,expense,deduction | January/February release |

Rotate 2-3 keyword slots per seasonal cycle. Keep the core 70-80 characters stable and use the remaining 20-30 characters for seasonal experimentation.

## Before and After Examples

### Problem: Wasted characters

**Before:**
```
fitness tracker, workout app, best exercise, health and wellness, gym
```
Issues: spaces after commas (-5 chars wasted), "fitness" and "tracker" may duplicate title, "best" and "app" have no search value, "and" is a stop word.

**After:**
```
gym,health,run,step,calorie,weight,strength,cardio,hiit,yoga,plank,squat,routine,progress,streak
```
Fixes: no spaces, no duplicates of title/subtitle, no filler words, all terms are genuine search queries.

### Problem: Duplicate keywords

**Before** (title is "RunMate -- Running Tracker"):
```
running,tracker,run,jog,marathon,5k,pace,distance,route,gps,heart,rate,training,fitness,health
```
Issues: "running", "tracker", and "run" duplicate the title -- 17 characters wasted.

**After:**
```
jog,marathon,5k,pace,distance,route,gps,heart,rate,training,fitness,health,stride,tempo,interval
```
Fixes: removed title duplicates, added 3 new high-value terms with the recovered space.
