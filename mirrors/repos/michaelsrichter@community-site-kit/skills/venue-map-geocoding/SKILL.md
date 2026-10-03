---
name: venue-map-geocoding
description: >-
  Add latitude/longitude to venues automatically and show events on an interactive map. Use when asked
  for a map view of events or venues, to geocode addresses, to store coordinates in the CMS, to add
  "dances near me", or to fix wrong map pins. Uses free, key-less services (U.S. Census geocoder, then
  OpenStreetMap Nominatim) and Leaflet with OpenStreetMap tiles.
---
> `<kit>` = the folder where the community-site-kit plugin is installed (usually `~/.copilot/installed-plugins/community-site-kit/community-site-kit`; check with `copilot plugin list --json`) or a clone of github.com/michaelsrichter/community-site-kit. Run Node scripts from the site repo folder so they can use its `sharp`, `playwright` and `yaml` packages.


# Venue geocoding and the events map

## Geocoding

- Script: `scripts/geocode-venues.mjs` in this skill (standalone; the starter also ships it as
  `npm run geocode`). It reads venue Markdown/YAML front matter, and for each venue without coordinates:
  1. U.S. Census Bureau geocoder (`onelineaddress`, benchmark `Public_AR_Current`) — free, no key, public domain.
  2. OpenStreetMap Nominatim fallback — **max 1 request per second**, a real User-Agent with contact info,
     `countrycodes` filter. Attribution: "© OpenStreetMap contributors, ODbL".
  3. Nominatim again with "<venue name>, <address>".
  Strips suite/unit/floor text, rejects matches farther than `--max-km` from `--center`, and writes
  `latitude`, `longitude`, `coordinatesSource` (rounded to 6 decimals, line endings preserved).

  ```powershell
  node <kit>/skills/venue-map-geocoding/scripts/geocode-venues.mjs --dir src/content/venues --center 40.8677,-73.3537 --max-km 250 [--force] [--dry] [--country us]
  ```

  Needs the `yaml` package resolvable from the current folder (the starter has it).
- Outside the U.S., skip Census (`--no-census`) and keep Nominatim.
- CMS: expose `latitude`, `longitude`, `coordinatesSource` with hints ("Filled automatically; change only
  if the pin is wrong. Right-click the spot in Google Maps to copy coordinates.").
- GitHub Action (starter: `.github/workflows/geocode-venues.yml`): on PRs/pushes touching
  `src/content/venues/**`, run the script and commit the result back to the branch.
- When an address fails, fix the address (wrong road names are common, e.g. "Broad Hollow" vs
  "Broadhollow") before entering coordinates by hand.

## The map page (`/events/map/`)

- Leaflet 1.9 + OpenStreetMap standard tiles (`https://tile.openstreetmap.org/{z}/{x}/{y}.png`), with
  attribution. No API key, no cookies. Dark mode: CSS filter on the tile pane via a token
  (`--map-tiles: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%)`).
- Group events by place (`src/lib/map-places.ts`): one pin per venue; home-org venue pin is a star in the
  brand color, community pins round. Popups list the next 3 dates, link to the venue page and directions.
- Filters (host, when) sync to the URL; `#place-<id>` deep links focus a pin.
- "Show dances near me": `navigator.geolocation` only on click; sorts the list by distance in the browser;
  nothing is sent anywhere. Add `Permissions-Policy: geolocation=(self)` and a privacy-page note.
- A plain list of places (with the same info) renders without JavaScript and is the accessible alternative.
- CSP: `img-src` must allow `https://tile.openstreetmap.org`.
- Link the map from the view switcher, homepage, footer, venue pages ("See it on the dance map") and `llms.txt`.

## Tests

- Unit: `oneLineAddress`, `distanceKm`, parsers for Census/Nominatim responses, `groupByPlace`.
- E2E: number of markers equals number of places; home pin count; "Show on map" opens a popup; host
  filter changes marker count and URL. Scroll the map into view before screenshots (off-screen Leaflet
  maps render gray).
