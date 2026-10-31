# Content Route — Full Reference

## Presenting available search sources

Before any tool call, dispatch `ask_followup_question` offering only the sources whose tools you actually have (via introspection), plus "Other". Each is its own option — never numbered lines inside the question text:

```text
question: "How would you like to search for content?"
options:
  - "Search using keywords — Search Salesforce CMS by keywords and taxonomies"
  - "Search using Data 360 hybrid search — Semantic (vector + keyword) search across Salesforce CMS and connected DAMs"
  - "Other — Provide your own URL, asset library path, or system to check"
```

Wait for the user's selection. Do not call any tool before this point. Then follow the matching branch:
- **Search using keywords** → `search_content_cms_channels` (build keywords + taxonomies, confirm, execute per scope — see below).
- **Search using Data 360 hybrid search** → `search_digital_content` (verbatim query + bare ISO `searchLanguage` when the schema lists it — see "Search using Data 360 hybrid search" below).
- **Other** → ask for a direct URL, asset library path, or specific system to check. No confirmation step, since no tool is called.

## Confirming the query before searching

Required two-message pattern, same turn:

**Message 1 (chat-visible plain text — NOT inside `ask_followup_question`):** print the parameters as a labeled list, one field per line:

```text
I'll search for content with these parameters:

  Content Type: <label> (<fqn>[, <label2> (<fqn2>), ...])
  Keywords: <keyword1 OR keyword2 OR ...>
  Taxonomies: <term1, term2, ...>
  Language: <en_US>
  Channels: Public[, plus <uiBundle> channel]
```

**Message 2 (immediately after, same turn):** dispatch `ask_followup_question` with a short question and options — `Yes - search now` / `Edit search` / `Cancel`.

**Never put the labeled list inside `ask_followup_question`'s `question` text.** That UI strips line breaks and formatting, which is exactly what collapses the parameters back into a single paragraph.

## Executing the search call(s)

Per the scope determined in Step 1. `contentAccessScope` and `channelIds` are **mutually exclusive fields — never include both in the same call**:
- **No `channelId` in scope (public channels only)** — one call to `search_content_cms_channels` with `contentAccessScope: "Public"` and no `channelIds` field at all.
- **A `channelId` is in scope** — two calls: one with `contentAccessScope: "Public"` and no `channelIds` (public channels), and one with `channelIds` set to the discovered `channelId` and no `contentAccessScope` field at all. Each result item already carries its own list of channel deliveries in `managedContentChannelDeliveryDetails` — this array can hold many entries for a single item (a public-unauthenticated channel, a Community channel, several uiBundle channels, etc. — see the real API response below), independent of how many calls were made. **If the same item (by `managedContentKey`) appears in both responses, merge their `managedContentChannelDeliveryDetails` arrays** rather than picking one response and discarding the other — de-duplicate only exact repeats of the same `managedContentChannelDetails.id`. Presentation (Step 3 point 4) still shows the item once; selection (Step 3 point 5) is where the channel choice actually gets made — see "Disambiguating channel at selection" below.

From each response, parse `outputValues.searchResults[]`, extracting `title`, `contentType`, `managedContentId`, `managedContentKey`, `language`, and the **full `managedContentChannelDeliveryDetails` array** — never just index `[0]`. Each entry pairs a `contentUrl` with `managedContentChannelDetails.{id, name, type}` (the channel it's delivered to). `type` is one of `PUBLIC_UNAUTHENTICATED`, `COMMUNITY`, or `WEB_APP` (a uiBundle-scoped channel — this is what the channel-scoped call in Step 1 discovers). A single item's array can be empty (not yet delivered to any channel — omit the Unauthenticated URL line entirely for that item), have one entry (use it directly, no question needed), or have several (ask which channel — see "Disambiguating channel at selection" below).

**The Unauthenticated URL is public-channel-only.** Only a `PUBLIC_UNAUTHENTICATED` or `COMMUNITY` entry's `contentUrl` is ever shown to the user as the Unauthenticated URL. A `WEB_APP` entry's `contentUrl` is **never** surfaced — omit the URL line entirely when the chosen (or only) entry's type is `WEB_APP`, even though the field is present in the response. This applies after channel disambiguation (below), not before — a `WEB_APP` entry is still offered as a selectable channel option; it just never produces a displayed URL once chosen.

**Real API response — `WEB_APP` (uiBundle) channel, from the channel-scoped call:**

```json
{
  "title": "Apple Inc.",
  "contentType": "c__StockMarket",
  "managedContentId": "20YVW000001miuD",
  "managedContentKey": "MCICPC4X5KE5ATHMTN4EYK5DOCYM",
  "managedContentChannelDeliveryDetails": [
    {
      "contentUrl": "https://.../channels/0apVW000000Z25NYAS/contents/20YVW000001miuD?language=en_US",
      "managedContentChannelDetails": { "id": "0apVW000000Z25N", "name": "testinternalapp", "type": "WEB_APP" }
    }
  ]
}
```

Even though `contentUrl` is present, this item's only entry is `WEB_APP` — the Unauthenticated URL line is omitted for it. Only `managedContentId`, `managedContentKey`, `language`, and channel (`testinternalapp`) are shown.

**Real API response** (one item, six delivery entries, from a single call — no second channel-scoped call was even involved):

```json
{
  "title": "Housing Prices In Japan",
  "contentType": "sfdc_cms__news",
  "managedContentKey": "MCVL5CJAB4NBBBRPTMY2N3DALBB4",
  "managedContentChannelDeliveryDetails": [
    { "contentUrl": "https://.../0apVW000000TsHxYAK/...", "managedContentChannelDetails": { "id": "0apVW000000TsHx", "name": "Test CMS Channel", "type": "PUBLIC_UNAUTHENTICATED" } },
    { "contentUrl": "https://.../0apVW000000VUt3YAG/...", "managedContentChannelDetails": { "id": "0apVW000000VUt3", "name": "testLWR", "type": "COMMUNITY" } },
    { "contentUrl": "https://.../0apVW000000ZYoPYAW/...", "managedContentChannelDetails": { "id": "0apVW000000ZYoP", "name": "Test Channel 2", "type": "PUBLIC_UNAUTHENTICATED" } },
    { "contentUrl": "https://.../0apVW000000ZYq1YAG/...", "managedContentChannelDetails": { "id": "0apVW000000ZYq1", "name": "Test Channel 3", "type": "PUBLIC_UNAUTHENTICATED" } },
    { "contentUrl": "https://.../0apVW000000ZYrdYAG/...", "managedContentChannelDetails": { "id": "0apVW000000ZYrd", "name": "Test Channel 4", "type": "PUBLIC_UNAUTHENTICATED" } },
    { "contentUrl": "https://.../0apVW000000ZYtFYAW/...", "managedContentChannelDetails": { "id": "0apVW000000ZYtF", "name": "Test Channel 5", "type": "PUBLIC_UNAUTHENTICATED" } }
  ]
}
```

The multi-channel case is not "one entry from the public call, one from the channel-scoped call" — it's whatever the array actually contains, however many entries that is.

## Search using Data 360 hybrid search (`search_digital_content`)

Chosen when the user picked "Search using Data 360 hybrid search" at the source step. Data 360 hybrid search (vector + keyword) runs across Salesforce CMS and any connected third-party CMS/DAM.

1. Pass `searchQuery` **verbatim** — same language, same script as the user wrote it. No translation, no keyword extraction, no ` OR `-joining, no `taxonomyExpression`, no `contentTypeFqn`/`contentAccessScope`/`channelIds`, no pagination. Translating first only makes step 2 harder, since you'd be detecting the language of your own translation instead of the user's actual words.
2. **Determine language** — a short ISO code read directly off the user's literal wording, before any translation happens in your reasoning. Bare 2-letter codes (`en`, `fr`, `de`, `es`, `ja`, ...) cover most languages and are the validated, simpler form; a few regional splits need a country suffix instead (`pt_BR`, `zh_CN`, `zh_TW`, ...). Default to `en` only when the message is genuinely ambiguous (e.g. a bare product name) — never because translating felt natural. Use the bare 2-letter form whenever one exists — the backend accepts only the platform's own language codes, so `fr` works but `fr_FR` is rejected as invalid (`en` and `en_US` both work because `en_US` is itself a platform code).
3. **Data 360 hybrid search ignores channel scope entirely** — there is no public vs. channel-scoped split. Make a **single call** regardless of whether a `channelId` is in scope from Step 1: `search_digital_content(searchQuery="<verbatim query>", searchLanguage="<language code>")`. **Only send `searchLanguage` if the tool's input schema actually lists it** — orgs without language-variant search enabled don't declare the input at all. When it's absent, call with `searchQuery` alone, skip the language line in the confirmation message, and skip steps 4–5 (the backend searches primary-language content only).
4. **Offer one retry with `searchLanguage` omitted entirely — ask the user first, never retry silently — but only when the first call either:**
   - returns **zero results**, **or**
   - fails with an **input-validation error about the language value itself** — an unrecognized language code errors the whole call (for example, `INVALID_API_INPUT` / "Specify a valid language code, such as en_US, fr, or de.") rather than returning an empty list.

   **Do NOT offer this retry on a server or transport error (5xx, timeout, connection failure).** Those must fail per `SKILL.md`'s Error Handling table — omitting the language cannot fix them and would mask the real failure. The retry exists only for the two language-specific cases above.

   Offer it before concluding nothing exists and before suggesting broader keywords: tell the user what happened in plain chat text (e.g. "No results found in French."), then `ask_followup_question` with options `Yes - search without language filter` / `No - stop here`. The retry is a second backend call the user didn't confirm, so they decide whether it runs. Skip the question only if the user already said, in this conversation, to fall back to any language when nothing matches theirs — then retry directly. This is the same policy as the Media Route's hybrid search (`media-route.md`). Omitting the field makes the backend fall back to each item's own primary/default language variant instead of the requested one — so an item that only has, say, a French variant still surfaces on the retry even when the user asked in English. Only fall through to "no results" / broadening suggestions if the user declines, or the retry also comes back empty.
5. **Read each result item's `language` field to know which language variant you actually got** (a locale string such as `en_US` or `fr`). If it differs from the language the user asked for — typically after the retry — say so explicitly when presenting that item, e.g. "No French version exists for this item — here's the original in English." Never present a fallback-language result as if it were the requested-language match; the user needs to know a substitution happened.

   If `language` is **absent** on the results of a call that sent `searchLanguage`, the backend couldn't apply the language filter (for example, the org's search index predates language-variant support) and silently returned primary-language content instead — even on the first call, with no error and no empty list. Don't claim the results are in the requested language; tell the user the search couldn't be restricted to that language.

This is a **strict** filter, not soft ranking like the keyword route: the backend only returns items carrying that exact language variant, and it does **not** fall back to English (or any other language) per item on its own — that's why step 4's retry exists as an explicit, user-approved second call, not something the backend does silently.

Example — French input "trouve-moi un article sur les pinceaux depuis le CMS" → `search_digital_content(searchQuery="trouve-moi un article sur les pinceaux depuis le CMS", searchLanguage="fr")`.

Example of the retry — English input "give me a blog post about a snowboard from the CMS" → first call `search_digital_content(searchQuery="give me a blog post about a snowboard from the CMS", searchLanguage="en")` returns zero results (the only snowboard article in the org has a French variant, not English) → tell the user "No results found in English." and ask whether to search without the language filter → user picks `Yes - search without language filter` → retry `search_digital_content(searchQuery="give me a blog post about a snowboard from the CMS")` with `searchLanguage` omitted → the item surfaces with `language: "fr"` → tell the user: "No English version exists for this item — here's the original in French."

Still confirm first via the two-message pattern — Message 1 surfaces the detected language so the user can catch a mis-detection before the search runs (language detection is the most error-prone step of this route):

```text
I'll search Data 360 hybrid search with:

  Query: trouve-moi un article sur les pinceaux depuis le CMS
  Language: fr   (auto-detected — tell me if this is wrong)
```

Show `Query` exactly as the user wrote it (verbatim) and `Language` as the bare code you'll send. This route has no `Content Type` / `Keywords` / `Taxonomies` / `Channels` lines — it ignores channel scope and does its own semantic matching. Then `ask_followup_question` with `Yes - search now` / `Edit search` / `Cancel`, exactly as for keyword search.

### Parsing the `search_digital_content` response

The response shape differs from `search_content_cms_channels`. Map each result to the same content-route fields the rest of this reference uses, so "Disambiguating channel at selection", display, and the render hand-off all work unchanged:

| `search_digital_content` field | Content-route equivalent |
|---|---|
| `contentName` | `title` |
| `contentId` | `managedContentId` |
| `contentKey` | `managedContentKey` |
| `contentTypeFqn` | `contentType` |
| `contentUrls[]` → each `{ channelName, channelId, url }` | `managedContentChannelDeliveryDetails[]` → each `{ contentUrl: url, managedContentChannelDetails: { id: channelId, name: channelName } }` |
| `language` | `language` — present when language-variant search applied; use it per step 5 above |
| `searchScore` | _(extra — hybrid-only relevance score; optional to surface)_ |

**Omissions to account for:** if `language` is absent, omit the Language line for that item (and, if the call sent `searchLanguage`, tell the user the search couldn't be restricted to the requested language — see step 5).

**Classifying channel type.** The hybrid response carries **no channel `type`** on its delivery entries, and because hybrid search ignores channel scope it can return an item delivered to a uiBundle channel. Fill in `managedContentChannelDetails.type` yourself so the public-channel-only URL rule in "Executing the search call(s)" above still holds:
- An entry whose `channelId` matches any uiBundle `channelId` found in Step 1 (any `uiBundles/*/public/content-metadata.json` channel, or the named uiBundle's resolved channel) → `WEB_APP`. Its `url` is **never** surfaced as the Unauthenticated URL, and the render hand-off passes `contentKey` instead of a URL for it. Compare on the first 15 characters — Salesforce IDs appear in both 15- and 18-character forms.
- Every other entry → treat as a public channel (`PUBLIC_UNAUTHENTICATED`), so its `url` is the Unauthenticated URL.

A `WEB_APP`-classified entry is still a selectable channel option at disambiguation, exactly as in the keyword case — it just never produces a displayed URL.

**Filter to the Step 2 content types.** The hybrid call takes no `contentTypeFqn`, so results can include types outside what Step 2 discovered. Keep only results whose `contentTypeFqn` is one of Step 2's FQN(s), so both sources answer the same question. If that filter removes every result from a non-empty response, don't report "no results" — tell the user which other content types came back and ask whether to show them.

After mapping, the `managedContentChannelDeliveryDetails` array behaves identically to the keyword case (zero / one / many entries), so everything downstream — channel disambiguation, display, and the render hand-off — is reused as-is.

## Disambiguating channel at selection

Reached at Step 3 point 5, only for a selected item whose (merged, per "Executing the search call(s)" above) `managedContentChannelDeliveryDetails` array has more than one entry. Build one option per entry, using that entry's `managedContentChannelDetails.name`, in the order the array returns them — not a fixed two-option choice. **Call `ask_followup_question` with these as its actual `question` and `options` parameters — never concatenate the channel list into the question string itself**, the same rule every other question in this skill follows:

```text
question: "Which channel would you like to use for 'Sustainability Report 2024'?"
options: ["Public", "landing-page"]
```

Wait for the reply before displaying that item's details, and use the record from the **chosen** entry — never assume entry `[0]` is the right one. An item selected alongside it whose array has zero or one entry does **not** get a question — zero entries goes straight to display with the Unauthenticated URL line omitted; one entry goes straight to display using that entry. Once every multi-entry item in the selection has been resolved (or immediately, if none were), display all selected items' details (Step 7 below).

**Real-world scale** — the "Housing Prices In Japan" response above would produce:

```text
question: "Which channel would you like to use for 'Housing Prices In Japan'?"
options: ["Test CMS Channel", "testLWR", "Test Channel 2", "Test Channel 3", "Test Channel 4", "Test Channel 5"]
```

Ask from the full array every time, however many entries it has — don't special-case it down to "Public vs. the one uiBundle channel." All six names go in the `options` array; the `question` string stays that one short sentence.

**A `WEB_APP` entry is still a valid, selectable option here** — it's excluded only from the Unauthenticated URL line at display time (see "Executing the search call(s)" above), not from the channel choice itself.

## Offering the render hand-off

Only when the channelId in scope came from uiBundle discovery (skip entirely for public-only scope, or a user-supplied `channelId` with no associated uiBundle). Same required two-message pattern as the search confirmation above:

**Message 1 (plain text):**

```text
I can render the following in the <uiBundle> app:

  1. <title> (<content type label>)
  2. <title> (<content type label>)
```

**Message 2 (immediately after):** `ask_followup_question` with options `Yes` / `No`. Never restate the item list or count inside the question text — the question stays generic (`"Render this content in the <uiBundle> app?"`).

- **Yes** — dispatch via `mcp__skill_bridge__load_skill("experience-cms-content-render")` — never the built-in Skill tool (separate registry, returns `Unknown skill`). Pass each selected item's `title`, content type FQN, its chosen entry's `managedContentChannelDetails.id` (channel ID) **only when that item's (merged) `managedContentChannelDeliveryDetails` array has an entry** — use the chosen entry if the array had more than one, or the sole entry if it had exactly one. **An item with zero entries has no entry to read `.id` from — omit the channel ID field for it entirely, never a placeholder or `null`**; `experience-cms-content-render`'s own documented channel-resolution flow asks the user for the channel (or HALTs) when none is supplied, so this is safe to leave out. Also pass either its Unauthenticated URL or, if absent, its `managedContentKey` renamed to `contentKey` — `experience-cms-content-render`'s own `SKILL.md` names the field `contentKey`, not `managedContentKey`. If the load call fails, tell the user the hand-off failed and stop — don't render yourself.
- **No** — stop; the search is complete.

## Building the search query

Keyword/taxonomy extraction rule: see `SKILL.md` Step 3 point 2 (the Media Route uses the same split — see `media-route.md` for media-specific examples). Additional worked examples for content:
- "press release about our product launch" → keywords: launch, announcement, release, product launch; taxonomies: Launch, Announcement, News
- "FAQs about password resets" → keywords: password, reset, login, account; taxonomies: _(empty — no descriptive/categorical terms)_

1. **Determine locale** — format `en_US`, `es_MX`, `fr_FR` (default: `en_US`)
2. **Build the JSON payload** — `searchKeyword` joins keywords with ` OR `; `taxonomyExpression` is a stringified `{"OR": ["term1", "term2"]}`, or `"{}"` if none.

## Complete End-to-End Example

**User Request:**
> "I need to find blog posts about sustainable business practices and environmental responsibility for our company website."

---

**Step 1: Determine Search Intent**

Intent parsed:
- Content type: Blog posts
- Keywords: sustainable, business, practices, environmental, responsibility
- Clear intent → proceed to Step 2

---

**Step 2: Discover Content Types**

Call `search_metadata` — this tool has no `filters` array; `metadataType` is the only accepted narrowing parameter:
```json
{
  "query": "blog post article",
  "metadataType": "ContentTypeBundle",
  "limit": 100
}
```

This returns candidate matches only — no `jsonAttributes`, so routing and delivery-API filtering aren't possible yet. Each candidate already includes a full composite identifier, e.g. `00DVW00000CfBQP2A3::0T1VW000008sow60AA::ContentTypeBundle` (name `sfdc_cms__blog`) among others — use it as returned.

Call `query_metadata` with each candidate's identifier from above, as-is, batched into one `metadataIdentifiers` array:
```json
{
  "metadataIdentifiers": [
    "00DVW00000CfBQP2A3::0T1VW000008sow60AA::ContentTypeBundle"
  ]
}
```

For each entry, read `typeDetails[].properties` — `mixins`, `typeClasses`, and `apiName` live there. Filter in two steps, **before** deciding content-vs-media routing:

1. Discard any candidate whose `properties.mixins` lacks `sfdc_cms:deliveryApiEnabled`.
2. Of the remainder, discard any candidate whose `properties.typeClasses` does not contain `sfdc_cms__structured`. **This is a "supported for search" gate, not a content/media split** — `sfdc_cms__structured` is present on both structured-content types (`sfdc_cms__blog`) and media types (`sfdc_cms__image`), so a surviving candidate could still turn out to be either. **`sfdc_cms__content` alone is not sufficient** here — it's a shared parent class for both structured content and media types (e.g. `sfdc_cms__email` has `sfdc_cms__content` in its `typeClasses` but not `sfdc_cms__structured`, and must be discarded, not routed to content search).

Only after this filtering do you inspect the survivors' `typeClasses` again to route: `sfdc_cms__media` present → Media Route (see `media-route.md`); otherwise → Content Route (this file). Rank the content-route survivors.

Result: Found `sfdc_cms__blog` content type (single match here after filtering; if multiple relevant types had matched, e.g. `sfdc_cms__blog` and `c__Article`, they would be passed together as `"sfdc_cms__blog,c__Article"`)

---

**Step 3: Build Search Query**

Extract:
- Keywords: `sustainable OR sustainability OR environmental OR responsibility OR green OR eco OR carbon`
- Taxonomies: `{"OR": ["Business", "Corporate", "Environment", "Responsibility"]}`
- Language: `en_US`

Construct payload (public-channels scope only here — no `channelId` was discovered, so `contentAccessScope` is set and `channelIds` is omitted entirely; the two fields are mutually exclusive):
```json
{
  "inputs": [{
    "searchKeyword": "sustainable OR sustainability OR environmental OR responsibility OR green OR eco OR carbon",
    "taxonomyExpression": "{\"OR\": [\"Business\", \"Corporate\", \"Environment\", \"Responsibility\"]}",
    "searchLanguage": "en_US",
    "contentAccessScope": "Public",
    "contentTypeFqn": "sfdc_cms__blog",
    "pageOffset": 0,
    "searchLimit": 5
  }]
}
```

---

**Step 4: Confirm Query**

Present to user:
```text
I'll search for content with these parameters:

  Content Type: Blog (sfdc_cms__blog)
  Keywords: sustainable OR sustainability OR environmental OR responsibility OR green OR eco OR carbon
  Taxonomies: Business, Corporate, Environment, Responsibility
  Language: en_US
  Channels: Public

Proceed with this search?
```

User: "Yes - search now"

---

**Step 5: Execute Search**

Call `search_content_cms_channels` with the payload

---

**Step 6: Present Results**

Results are grouped by content type, with channel shown as a per-item field. This example ran with only one content type FQN (`sfdc_cms__blog`) and public-channels-only scope, so there's only one group and the content-type heading is omitted — but the per-item `Channel:` field is still shown:

```text
I found 5 content items:

1. Our Journey to Carbon Neutrality
   Content Type: Blog (sfdc_cms__blog) — Channel: Public

2. Building a Sustainable Supply Chain
   Content Type: Blog (sfdc_cms__blog) — Channel: Public

3. Renewable Energy: Powering Our Future
   Content Type: Blog (sfdc_cms__blog) — Channel: Public

4. Green Office Initiatives That Work
   Content Type: Blog (sfdc_cms__blog) — Channel: Public

5. Sustainability Report 2024
   Content Type: Blog (sfdc_cms__blog) — Channel: Public

---
6. Load More (showing 5 of 8)
7. Done

Select one or more items (e.g., "1, 3" or "all"), Load More, or Done:
```

If a `landing-page` uiBundle channel had also been in scope and returned hits, the channel would still just be a per-item field — it would NOT create a new group, since content type is the only grouping key. But if a second content type (e.g. `c__Article`) had also matched, results would be grouped and numbered continuously by content type instead, e.g.:

```text
I found 3 content items:

Blog (sfdc_cms__blog):
1. Our Journey to Carbon Neutrality — Channel: Public
2. Internal Sustainability Metrics Q3 — Channel: landing-page

Article (c__Article):
3. Building a Sustainable Supply Chain — Channel: Public
```

User: "1, 2, 5"

---

**Step 7: Display Content Details**

```text
Selected content:

1. Our Journey to Carbon Neutrality
   Content Type: Blog (sfdc_cms__blog)
   Channel: Public
   Content ID: 20YXX000000010
   Content Key: MCBT7N9K5WX2QPFR4VHD8JLZ6MGY
   Language: en_US
   Unauthenticated URL: https://example.my.salesforce-sites.com/blog/carbon-neutrality-journey

2. Building a Sustainable Supply Chain
   Content Type: Blog (sfdc_cms__blog)
   Channel: Public
   Content ID: 20YXX000000011
   Content Key: MCQJ3P8TK6DWL9XN5VHR2FZ4GBY7
   Language: en_US
   Unauthenticated URL: https://example.my.salesforce-sites.com/blog/sustainable-supply-chain

5. Sustainability Report 2024
   Content Type: Blog (sfdc_cms__blog)
   Channel: Public
   Content ID: 20YXX000000014
   Content Key: MCHZ8P3T7FN5XDWK2QJVR6GMLBY9
   Language: en_US
```

Item 5's `managedContentChannelDeliveryDetails` array is empty (not yet delivered to any channel), so its URL line is omitted rather than shown blank. Items 1 and 2 have one entry each, so their URLs are shown in full. (This example's scope was public-channels-only with no `channelId` discovered — see SKILL.md Step 1 — so no item here has more than one delivery entry; for a worked multi-entry disambiguation, see "Disambiguating channel at selection" above.)

---

**Step 8: Offer to Render (only if a uiBundle channel was in scope)**

This example ran with public-channels-only scope (SKILL.md Step 1 found zero uiBundle `channelId`s), so this step is skipped entirely — the results from Step 7 are the final output. If SKILL.md Step 1 had found, say, a `landing-page` uiBundle with a `channelId`, the agent would instead use the same two-message pattern as Step 4's search confirmation — the item list as its own plain-text message, never folded into `ask_followup_question`'s question text:

**Message 1 (plain chat text):**

```text
I can render the following in the landing-page app:

  1. Our Journey to Carbon Neutrality (Blog)
  2. Building a Sustainable Supply Chain (Blog)
```

**Message 2 (immediately after):** `ask_followup_question` with the question `"Render this content in the landing-page app?"` and options `Yes` / `No`. Note the question stays generic — it does NOT restate "these two items" or the count; that's exactly the kind of detail Message 1's list already carries, and stuffing it into the question text is the failure mode this pattern avoids (same reasoning as Step 4's search-confirmation message, which strips line breaks/formatting from anything placed inside `ask_followup_question`).

On `Yes`, dispatch delegation via `mcp__skill_bridge__load_skill("experience-cms-content-render")` — never the built-in Skill tool, which doesn't know about MCP-bridge skills and returns `Unknown skill`. Pass each selected item's `title`, content type FQN (e.g. `sfdc_cms__blog`), and its chosen entry's channel ID (`managedContentChannelDetails.id`, e.g. `0apVW000000TsHx`) **when it has one** — items 1 and 2 above each have exactly one entry, so their channel ID is included; item 5 has zero entries (empty `managedContentChannelDeliveryDetails`), so its channel ID is omitted entirely rather than read off a nonexistent entry. Also pass either its Unauthenticated URL (item 1/2 above) or, when absent, its `managedContentKey` renamed to `contentKey` (item 5 above) — the receiving skill's `SKILL.md` names this field `contentKey`. If the load call fails, tell the user the hand-off failed and stop — do not attempt the render yourself.
