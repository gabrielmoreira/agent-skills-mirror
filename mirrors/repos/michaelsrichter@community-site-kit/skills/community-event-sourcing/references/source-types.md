# Community source types: practical notes

## Monthly PDF calendars (regional dance newsletters)

- Find the archive page ("Past issues", "Back issues"). Download every issue for the period you need with a
  polite loop (one request at a time). Name files `YYYY-MM.pdf`.
- Parse with `../scripts/parse-pdf-calendar.py` (PyMuPDF). It reads text blocks column by column, detects
  day headers (`TUESDAY OCT 6`), sections (`DANCES`, `CLASSES`, `SPECIAL EVENTS`, `WORKSHOPS`) and town
  headers, joins soft-hyphenated words, and strips "Ad pg N" references. Output rows:
  `{issue, date, section, town, text, page}`.
- Expect noise: directory pages at the end of an issue can look like listings (filter them by a known
  address prefix), and two-column layouts sometimes bleed. Always curate by hand before generating content.
- Search the rows for the host organization's name to backfill the archive (teachers, bands, prices).
- Credit the newsletter as `sourceName` with the issue month, and link the issue PDF as `sourceUrl`.

## Facebook groups and pages

- Most group content needs a signed-in browser. Ask the owner to sign in to the Playwright browser; do not
  copy cookies or profiles; close the browser afterwards.
- Read only what is needed: the group's public description, member count, URL (for the header button) and
  upcoming events (title, start/end, place, organizing group, ticket/info link).
- Do not copy members' names, photos or posts. Do not post anything.

## Embedded calendar widgets

- eventscalendar.co: the embed `https://embed.eventscalendar.co/html/calendar/<project>` loads a public JSON
  feed like `https://api.eventscalendar.co/api/v0.1/projects/<project>/data/public/events?user=<user>&app=calendar`.
  Find the exact URL in the browser's network requests (`browser_network_requests`).
- Google Calendar embeds: the calendar ID is in the iframe `src`; the public ICS is
  `https://calendar.google.com/calendar/ical/<id>/public/basic.ics`.
- Many widgets offer "Subscribe" or "Add to calendar" (ICS). Prefer ICS: it has stable UIDs and time zones.
- Convert to community events with the teacher's organizer entry; keep their wording short; link `infoUrl`.

## Organizer and teacher websites

- Record contact info exactly as published (phone, email, site). Mark anything inferred for review.
- Typical structure to capture: weekly socials (day, time, price, DJ), classes (levels, start dates,
  "no partner required", first class free), special events (holiday parties, workshops).

## Google Maps facts for venues

- Use the place page (search "<venue> <town>"). Capture: rating + review count with the month, parking
  (free lot, street), wheelchair-accessible entrance/parking, hours, phone, website, Facebook, plus code.
- Store `googleMapsUrl` (prefer `https://www.google.com/maps?cid=<CID>`) for "Photos & reviews on Google
  Maps"; never download review photos.
- Summarize review themes in neutral words ("large free parking lot", "wood dance floor") with `factsSource`.

## Band and teacher links

- Search: "<name> swing band <region>", "<name> dance teacher <town>". Confirm on the page that it is the
  same person/band (region, style, photos). Prefer official sites, then Facebook, Instagram, YouTube,
  Linktree. Avoid ticket resellers and fan pages.
