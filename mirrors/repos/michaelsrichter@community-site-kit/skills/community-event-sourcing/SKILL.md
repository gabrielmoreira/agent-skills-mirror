---
name: community-event-sourcing
description: >-
  Find, extract and add other organizers' events, organizer directories, and teacher/band/DJ links to a
  community events site. Use when asked to add community events, import a regional dance calendar (PDF
  newsletters), import events from a Facebook group or a teacher's own calendar (eventscalendar.co,
  Google Calendar, ICS, Wix), backfill an event archive, or link teachers' and bands' websites and social
  pages. Keeps the host organization first and every listing attributed to its source.
---
> `<kit>` = the folder where the community-site-kit plugin is installed (usually `~/.copilot/installed-plugins/community-site-kit/community-site-kit`; check with `copilot plugin list --json`) or a clone of github.com/michaelsrichter/community-site-kit. Run Node scripts from the site repo folder so they can use its `sharp`, `playwright` and `yaml` packages.


# Community event sourcing

The host organization's events always come first. Community events are a service to visitors, so each one
must say who runs it, how to reach them, where the listing came from, and "Check with the organizer before
you go."

## Content model (already in the starter)

- `host: home | community` on every event and series. Home = the organization; community = anyone else.
- `organizer` → an entry in `src/content/organizers/` (name, website, email, phone, Facebook, Instagram,
  town, venue, dance styles, tagline, classes, source name/URL, `editorialReview`).
- `sourceName` ("The Dance Calendar, October 2026"), `sourceUrl`, `infoUrl`, `cadence` ("1st and 3rd Fridays").
- Weekly community dances = a **series** bounded to the source's month (`recurrence.startDate/endDate`),
  so they expire unless a newer source confirms them. One-offs = events.
- Venues are shared: reuse an existing venue entry; new venues get geocoded (`venue-map-geocoding`).

## Sources and how to read them

See [references/source-types.md](references/source-types.md) for details. Summary:

| Source | How |
| --- | --- |
| Regional printed calendar (monthly PDF newsletter) | Download all issues (current + archive), parse with `scripts/parse-pdf-calendar.py`, then curate by hand |
| Facebook group / page events | Owner signs in to the Playwright browser; read the Events tab; take only event facts (title, date, time, place, host org, ticket link). **No personal names** of members |
| Teacher's own calendar widget (eventscalendar.co, Elfsight, Wix, Squarespace, Google Calendar) | Open the embed with Playwright, list network requests, find the public JSON or ICS feed; prefer ICS when offered |
| Organizer websites | Read schedule pages; confirm days, times, prices; store contact info as published |
| Google Maps (venue facts) | Parking, accessibility attributes, rating, hours, phone, website; store a "Photos & reviews on Google Maps" link (`https://www.google.com/maps?cid=<CID>`); **never copy photos** |

## Workflow

1. **Collect** raw listings into a scratch folder (`audit/<source>/…json`), each with source and page/URL.
2. **Scope**: keep the region (and nearby city events relevant to the dance style); drop far-away towns.
   Write the scope rule in the decision log.
3. **Curate**: merge duplicates across sources; split "dances" vs "classes" (weekly classes go on the
   Lessons/community pages, not as events); fix soft hyphens and column bleed from PDFs; never guess a
   missing time or price — leave it out and mark `editorialReview`.
4. **Generate content files** with a one-off Node script (YAML front matter, explicit `published: true`,
   `host: community`, organizer, venue, styles, source). Re-run safely (idempotent by slug).
5. **Backfill the home archive** from past issues: add missing teacher, band, lesson style and price to
   completed home events, with `sourceName` per issue. Keep existing statuses (cancelled stays cancelled).
6. **People links**: for every teacher, band and DJ, search the web for their official site and social
   pages (`webiq-web` or `web_search`, then open them to verify the name and region match). Add `website`,
   `facebookUrl`, `instagramUrl`, `youtubeUrl` to their profile; every mention renders links with
   `data-track="outbound_click"`. If a teacher publishes their own calendar, import it as community
   events with `organizer` = their organizer entry.
7. **Validate**: `npx astro check`, unit tests (schemas, explicit `published`), build, link check; look at
   the events page, community page and a community event page on a phone.
8. **Document**: counts per source in `docs/content-audit.md`; editor steps for adding community events
   in `docs/editor-guide.md`; scope and exclusions in `docs/decision-log.md`.

## Do not

- Copy photos from Facebook or Google.
- Import members' personal names or private group posts.
- Present community events as the organization's own (badge + legend + disclaimer on the event page).
- Keep weekly community series open-ended without a confirming source.
