# Requirement baseline for a community events website

Use this as the checklist for every project. Each line is written so you can test it. Lines marked
**(late)** were asked for *after* launch on the first project. Build them from day one.

## 1. Visitor questions answered on the homepage (above the fold on a phone)

- [ ] Next confirmed **home-organization** event: name, weekday + date, lesson time, open dancing time,
      venue + town, admission summary (member/non-member/student), "Beginners welcome", "No partner needed".
- [ ] Buttons: View event details, Get directions, Add to calendar, Share. Each is at least 44 px tall.
- [ ] A human date label: "Tonight!", "Tomorrow night", "This Tuesday · in 4 days!", "Next Tuesday · in 9 days",
      "In 3 weeks". It is computed in the organization's time zone and refreshed in the browser. **(late)**
- [ ] If the featured event has ended since the last build, the next one swaps in (client-side). If none,
      a friendly empty state appears. An old event is never shown as upcoming.
- [ ] Below: next home events (3 visible + "Show N more …"), then "More dancing around <region>" with
      community events. **(late)**
- [ ] What to expect, dance styles explained, beginner info, lesson info, membership value, venue summary,
      volunteer/contact call to action.
- [ ] Homepage photo area is an accessible auto-rotating slideshow of real photos of people dancing
      (pause/play, previous/next, swipe, keyboard, stops when a person picks a slide, respects reduced
      motion, pauses off-screen). Owner-supplied photos come first. **(late)**

## 2. Events

- [ ] One content entry per event; recurring series expand into occurrences with stable URLs
      (`/events/YYYY-MM-DD-slug/`) and per-date overrides (cancel, band night, special price, venue change).
- [ ] Statuses: draft, scheduled, cancelled, postponed, soldOut, completed. Cancelled stays visible and is
      clearly marked (text + icon, not color only).
- [ ] Times stored as local date-time + IANA time zone; no day shifts on phones; DST tested.
- [ ] **Host:** each event is `home` (the organization) or `community` (another organizer). Badges + legend
      explain the difference. Home events are always listed first; community events after. **(late)**
- [ ] Community events show organizer, contact (phone/email/website/Facebook), source ("From The Dance
      Calendar, October 2026") and "Check with the organizer before you go". **(late)**
- [ ] Dance-style tags on cards (max 3 + "+N more"). Style taxonomy is stored once. **(late)**
- [ ] Views: List (default, works without JavaScript), Month calendar (agenda on phones), Map, Past events
      (by year). One shared view switcher. **(late: map)**
- [ ] Filters: when (today, this week, this month, all, live bands), host, type, style, venue, lesson,
      level, text search. Filters sync to the URL. When any filter is on, show every match (no collapse).
- [ ] Long home-event lists show the **next 3** and a "Show N more <short name> dances" button
      (aria-expanded, focus moves to the first revealed item, "Show fewer" returns). Hidden items are in the
      HTML (no layout shift); everything shows without JavaScript. **(late)**
- [ ] Event page: summary at a glance, price table, lesson/dancing times, venue with parking and access
      notes, teacher/band/DJ with photo and links, "Next <short name> dance" callout on other pages,
      "More upcoming dances" (3 home + 3 community).
- [ ] Event actions: Google Calendar, Outlook (personal + work/school), standards-compliant `.ics`,
      calendar subscription feeds (home and community), native Web Share with accessible fallback
      (copy link, copy plain-text details, Facebook, email, SMS), directions (Google + Apple Maps), print
      view, downloadable social images (landscape + square). Copy shows a toast in a live region.
- [ ] RSS feed, `llms.txt`, Event JSON-LD with only real facts (eventStatus, organizer, offers, image ≥ 720 px).

## 3. People, places and organizers

- [ ] Venues stored once; address, parking, accessibility, phone, website, Facebook, "Photos & reviews on
      Google Maps" link (do not copy the photos). Facts note their source. **(late)**
- [ ] Venues have latitude/longitude filled automatically (Census geocoder, then OpenStreetMap Nominatim),
      stored in the CMS with the source; a GitHub Action fills new venues. **(late)**
- [ ] Teachers, bands and DJs have profile pages. **Every mention links to their website or social pages**
      (website, Facebook, Instagram, YouTube), with outbound-click tracking. **(late)**
- [ ] Teachers who keep their own public calendar have those events imported (with source). **(late)**
- [ ] Community page: organizers grouped by style, contacts, classes, links to the regional calendar
      and the Facebook group, disclaimer. **(late)**

## 4. Photos and media

- [ ] Only photos the organization owns or has permission for, or openly licensed photos with credit.
      Never copy Google Maps or Facebook user photos. Ask the owner for a folder of their own photos.
- [ ] Every image has alt text, intrinsic size, `srcset`/`sizes`, AVIF/WebP, lazy loading below the fold.
- [ ] Never upscale. Never crop wide banners into tall boxes. Each image can store a focus point
      (`"50% 30%"`) used for crops; CSS does not crop again. People's heads are never cut off. **(late)**
- [ ] Videos: short (≤ 20 s), silent, ≤ 1 MB, H.264, with poster, play only when visible. **(late)**
- [ ] `docs/image-inventory.md` lists source, permission status and where each image is used.

## 5. Navigation, layout and look

- [ ] Nav: Home, Events, New to <dance>?, Lessons, Venues, About, Membership, Gallery, Contact.
- [ ] Header: logo + name, nav (Menu button on phones and narrow laptops), **light/dark button**,
      **Facebook group button**. Header stays one line at every width from 320 px to 1600 px. **(late)**
- [ ] Phone Menu and every page's footer contain "Light or dark mode: Light / Dark / Auto". Auto follows
      the device; the choice is remembered without a flash. **(late)**
- [ ] No horizontal scrolling at 320 px; touch targets ≥ 44 px; works at 200% zoom.
- [ ] No announcement banner by default (the CMS can turn one on). **(late: owner removed "Bad weather?")**
- [ ] Original, warm design; respects reduced motion; no parallax; no text inside essential images.

## 6. Words

- [ ] Plain language an average U.S. high-school student understands: short sentences, common words,
      no jargon, every chart/table/definition explained. **(owner preference)**
- [ ] Well-known labels: "Frequently Asked Questions", "Add to calendar", "Get directions". **(late)**
- [ ] FAQ answers the real questions: partner, beginners, lesson, styles, what to wear, cost, parking,
      accessibility, membership, volunteering.

## 7. Content management (Decap CMS)

- [ ] `/admin/` with GitHub sign-in through a small OAuth Function; editorial workflow (drafts, review, PR
      previews). Every field in the content schema is editable; editors never touch raw JSON.
- [ ] Collections: events, series, venues, instructors, performers (bands/DJs), organizers, dance styles,
      pages, announcements, gallery albums (with "show on homepage slideshow"), FAQ, settings.
- [ ] Alt text is required; focus point fields for images; sort events newest first.
- [ ] An automated test loads `/admin/` and fails on any CMS config error. **(late: a bad config crashed it live)**
- [ ] Editor guide in plain language, including sign-in troubleshooting.

## 8. Legacy migration

- [ ] Crawl every public page of the old site (politely); inventory pages, events, venues, prices,
      contacts, images, links, titles/descriptions, duplicates, stale and conflicting facts.
- [ ] **Every** old URL redirects to the best new page (301 in config for the important ones; generated
      redirect pages for the long tail). **(late)**
- [ ] `docs/legacy-site-migration.md`: what each old page was, its problems, and where its content went,
      with old/new screenshots. Plus `content-audit.md` and `redirect-plan.md`. **(late)**
- [ ] Migrated, consolidated, redirected, needs review, omitted, not found — all listed.

## 9. Analytics and privacy

- [ ] GA4 and Microsoft Clarity load only after consent (or per the owner's opt-out choice); Global Privacy
      Control respected; "Privacy choices" link in the footer. **(late)**
- [ ] First-party telemetry Function sends OpenTelemetry custom events and metrics to Azure Monitor
      (page views, event views, interactions by action/method/location, Web Vitals, consent changes,
      rejected payloads). Same-origin only, size-limited, rate-limited, allow-listed names and props. **(late)**
- [ ] Named custom events for every action: select_event, add_to_calendar, share, get_directions,
      outbound_click, filter_events, show_more, theme_change, etc. Documented in `docs/analytics.md`.
- [ ] Privacy page in plain language (what is measured, cookies, map tiles, "near me", theme choice).

## 10. Security, SEO and performance

- [ ] CSP with hashed inline scripts (no `unsafe-inline` scripts, no inline `style=""`), HSTS, nosniff,
      Referrer-Policy, Permissions-Policy (geolocation=self only if the map uses "near me").
- [ ] Unique titles/descriptions, canonical URLs, sitemap, robots (no indexing before launch), Open Graph,
      JSON-LD (Organization, WebSite, Event, Place, Person, BreadcrumbList, FAQPage), 404 page.
- [ ] Lighthouse ≥ 90 performance, ≥ 95 accessibility/best practices/SEO; no serious axe issues.

## 11. Delivery

- [ ] Repo on the owner's chosen account, public unless they say otherwise. **(late)**
- [ ] Azure Static Web Apps Free + managed Functions; Bicep + an idempotent deploy script; deployment token
      piped into a GitHub secret; app settings for OAuth, Application Insights and allowed hosts.
- [ ] CI: type check, unit, API, build, link check, e2e (with axe), CodeQL, Dependabot; PR previews;
      nightly rebuild so "upcoming" stays true.
- [ ] Custom domain: add it in Azure, give the owner the **exact** DNS records (CNAME + TXT), confirm
      validation and HTTPS, update `SITE_URL`, `ALLOWED_HOSTS` and the OAuth app callback. **(late)**
- [ ] After each deploy: live smoke test, then email/Teams the owner the URL, changes, test results and any
      manual steps. **(late)**
- [ ] Docs: README, architecture (Mermaid), content model, editor guide, deployment, DNS cutover, rollback,
      accessibility test plan, image inventory, redirect plan, analytics, decision log.
