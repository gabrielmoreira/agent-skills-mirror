---
name: event-listing-ux
description: >-
  Patterns for listing and presenting events on a community or dance organization website: home
  organization first, featured next event, human date labels ("Tonight!", "Tomorrow night", "in 4 days!"),
  show only the next 3 with "Show more", list/calendar/map/past views, filters, add to calendar, share,
  directions, copy details, expiry of ended events on a static site. Use when building or changing event
  lists, the homepage hero, event pages, calendar feeds, or when the owner says events are hard to find.
---

# Event listing UX

All of these exist in the starter (`michaelsrichter/community-site-starter`). File names below refer to it.
If you are working on another codebase, copy the behavior, not necessarily the code.

## 1. Home organization first, everywhere

- `homeFirst()` in `src/lib/event-core.ts` sorts home events before community events, then by start time.
- `getEventGroups()` (`src/lib/content.ts`) returns `upcomingHome`, `upcomingCommunity`, `upcomingOrdered`
  and `next` (the next confirmed **home** event — never a community one, even if sooner).
- Homepage hero and the events page both feature `next`. Event pages for anything else show a
  "Next <short> dance" callout.
- Month calendar: home events first within a day, distinct style, a legend.
- Badges (`HostBadge.astro`): star + "<Short> event" vs people icon + "Community event". Always with a legend.

## 2. Human date labels

- Pure function `relativeLabel(startMs, endMs, nowMs, { excited, allDay })` in `src/lib/relative.ts`,
  computed in the organization's time zone (`America/New_York` by default):
  "Happening now!", "Tonight!", "Today!", "Tomorrow night", "Tomorrow", "This Tuesday · in 4 days!",
  "Next Tuesday · in 9 days", "In 3 weeks". `excited` adds "!" for home events.
- `RelativeWhen.astro` renders a hidden placeholder with `data-when-start/end`; `src/scripts/relative.ts`
  fills it in the browser (so labels are right on the day the page is viewed, not the build day).
- Unit-test: same-day evening, after midnight, DST weeks, all-day events, ended events.

## 3. Show the next 3, then "Show N more"

- Server renders every item; items after the third get `data-collapsed` (`EventCard collapsed` prop).
- CSS: `.js [data-collapsed] { display: none !important }` and hide month headings with no visible
  items: `.js [data-collapse] [data-month-group]:not(:has([data-event]:not([hidden]):not([data-collapsed]))) { display: none }`.
  The `js` class is added by an inline head script, so there is no layout shift and no-JS visitors see all.
- `ShowMore.astro` renders `<button aria-controls aria-expanded data-collapse-toggle>` with
  "Show 7 more <Short> dances" / "Show fewer <Short> dances". `src/scripts/collapse.ts` recounts after
  ended events are hidden, moves focus to the first revealed card, and tracks `show_more`.
- Filters set `data-collapse-filtered` on the container and dispatch `site:lists-changed` so every
  match shows while filtering (the collapse script listens for that event and recounts).
- Apply to: homepage, events list (index counts across month groups), event page "More upcoming"
  (3 home + 3 community), venue, series, performer, lessons; map popups show 3 dates per place.

## 4. Views and filters

- One `EventViews.astro` switcher: List · Month calendar · Map · Past events.
- List is the default and works without JavaScript; month calendar becomes an agenda list on phones.
- Filters (`src/scripts/events-filter.ts`): when (today, 7 days, month, all, live bands), host, type,
  style, venue, lesson, level, search; synced to the query string; result count in a live region;
  "Clear filters"; empty state.
- Map: see the `venue-map-geocoding` skill.

## 5. Event actions (every event page, and the featured card)

- Add to calendar menu: Google, Outlook.com, Outlook work/school, `.ics` download
  (`/events/<slug>/calendar.ics`), subscription feeds for home and community events.
- Share: native `navigator.share` when available; fallback dialog with copy link, copy details (name,
  weekday date, time, venue, town, URL), Facebook, email, SMS; downloadable social images (1200×630 and
  1080×1080, generated at build with satori). Toast in an `aria-live` region; never `alert()`.
- Directions: Google Maps and Apple Maps links built from the venue address.
- Print view: hide chrome, show essentials.

## 6. Static site, live truth

- Each event card carries `data-end` (epoch ms). `src/scripts/expire.ts` hides ended events, empty month
  groups and sections, swaps the featured candidate, and shows the empty state if needed.
- CI runs a nightly rebuild so the HTML catches up.
- Use `BUILD_NOW` (build) and Playwright `page.clock` (tests) to make date logic deterministic.

## 7. Cards

Each card shows: ticket-style date, host badge, human label, title, lesson + dancing times, venue + town,
price range, teacher/band (with outbound links), up to 3 style tags + "+N more", and for home events
"Beginners welcome · No partner needed". Community cards are compact and show organizer + cadence.

## Tests to keep

Hero is the home event even when a community event is sooner; lists start with 3 + toggle works both
ways; filters disable collapse; ended event hidden after the clock passes its end; cancelled event
visible and marked; no-JS list shows everything; human labels correct around midnight and DST.
