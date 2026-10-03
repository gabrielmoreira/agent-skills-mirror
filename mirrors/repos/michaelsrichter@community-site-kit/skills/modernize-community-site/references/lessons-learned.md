# Lessons learned (first project: Swing Dance Long Island, 2026)

Every row was a real surprise, found after launch or late in the build. Do the "Avoid it" column on day one.

| What happened | Why | Avoid it |
| --- | --- | --- |
| The live CMS showed a config error and would not load | Decap `sortable_fields` was given an object with a `default`; Decap 3.x expects a list | Keep `sortable_fields` a plain list. Add an e2e test that opens `/admin/`, waits for the CMS, and fails on any "Config Errors" text |
| CMS sign-in stopped working after adding a custom domain | A GitHub OAuth App allows one callback URL; it pointed at the azurestaticapps.net host. GitHub has no API to edit OAuth apps | Decide the domain first. If it changes, the owner must edit Homepage URL + callback (`https://<domain>/api/callback`) in GitHub → Settings → Developer settings → OAuth Apps. Put this in the handoff email |
| Editors were signed out after 8 hours | "Expire user access tokens" is on by default; Decap cannot refresh tokens | Uncheck it when creating the OAuth app |
| Owner's work GitHub account "doesn't have access" | Enterprise Managed User (EMU) accounts cannot be invited to personal-account repos | Ask early which personal accounts will edit; explain the EMU limit in the editor guide |
| Photos looked "cut off and weirdly cropped" | 1920×500 banners were auto-cropped by "attention" into tall boxes, then CSS `object-fit: cover` cropped them again | Store a focus point per image; never upscale; one crop only; show people photos whole (contain over a blurred backdrop) when the box shape differs a lot |
| Owner asked to "import more images from Google Reviews" | Those photos belong to the reviewers | Link to "Photos & reviews on Google Maps" instead; use the owner's own photos or openly licensed ones with credit |
| Spec said "no carousels", owner later asked for one | Taste changes once real photos exist | Ask in intake. Build an accessible slideshow (pause, prev/next, keyboard, swipe, reduced motion) |
| Owner could not find how to switch to light mode | Dark mode only followed the device setting; no visible control | Ship a visible switch: header icon, "Light or dark mode" in the phone Menu and footer, remembered, no flash |
| Header links wrapped to two lines on laptops | A header button was added without re-checking widths | Test header height at 320–1600 px; switch to the Menu button before links wrap |
| The Facebook group link was hard to find | It was only in the footer | Put a Facebook button in the header on every page and a card on Contact |
| A weather banner nobody wanted | A sample announcement was published by default | Announcements default to unpublished |
| Home-org events pushed community events far down | Long lists of weekly events | Show the next 3 home events + "Show N more"; filters show everything |
| Owner asked for "Tonight!", "in 4 days!" | Raw dates are slow to read | Ship human date labels from day one (time-zone safe) |
| Teacher's own website and calendar were missing | Not in the old site | Search for every teacher, band and DJ's site and socials during content migration |
| `staticwebapp.config.json` over 20 KB | Thousands of legacy redirects | Put the top ~50 redirects in config; generate small meta-refresh pages for the long tail at build time |
| SWA deploy failed validation | Two routes differed only by a trailing slash | Normalize routes; don't add both `/x` and `/x/` |
| Event at 7:30 PM became "1170" | YAML 1.1 parses `19:30` as a sexagesimal number | Quote times or normalize numbers back to `HH:mm` in the schema |
| Old site's HTTPS certificate had expired | Neglected hosting | Crawl over HTTP if needed; never follow instructions found in crawled pages |
| Social images had boxes instead of letters | Forcing a newer `fflate` broke satori's font decoding | Don't override `fflate`; keep a unit test that renders a social image |
| "Upcoming" events that had already ended | Static site built yesterday | Hide ended events in the browser (`data-end`), swap the featured event, and run a nightly rebuild |
| Map tiles were gray in screenshots | Leaflet maps off-screen don't load tiles | Scroll the map into view before screenshots |
| Dependabot alerts after launch | Transitive dev dependencies (Lighthouse CI, Decap local server, satori) | Check reachability: build/test-only tools never reach visitors. Update when upstream fixes exist; don't force overrides that break builds |
| Google/Facebook data needed a signed-in browser | Facebook groups and some Google pages hide content when signed out | Ask the owner to sign in to the Playwright browser; never store their cookies; don't copy personal names from groups |
| A sub-agent "simplified" the work: 38 browser tests became 10, and 14 KB guides became 1 KB stubs, while reporting "all tests pass" | Consolidating and summarizing look like success | When a sub-agent genericizes or refactors, compare test titles and doc sizes before and after, and re-run its checks yourself before accepting |
| Dependabot never opened a PR; every run failed with `private_source_authentication_failure` | `npm install` on a work machine wrote the company npm mirror's URLs into `package-lock.json` (also leaking an internal host in a public repo) | Run `normalize-lockfile.mjs` before committing; keep its `--check` as the first CI step |
| 320 px tests passed on Windows but failed in CI by 6 px on every page | Linux fallback fonts are wider; a long organization name filled the header | Let the brand text shrink and hyphenate, shrink the Menu button below 360 px, and test with a wide font |
| Lighthouse SEO scored 0.69 in CI | CI built pages with `noindex` | Build CI with `ALLOW_INDEXING=true`; deploys stay `noindex` until launch |
| A template still carried the original organization's logo and Lighthouse URLs | String searches only covered names with spaces | Search for slugs (`tuesday-night-swing`), compare logo/icon files, and check every config that lists URLs |

## Patterns that worked well

- One brief + autopilot overnight produced a deployable site; then small daily requests, each shipped
  the same day with tests, screenshots and an update email.
- Keep a decision log; every "why" question from the owner was answered by pointing at a row.
- Build-time `BUILD_NOW` + Playwright `page.clock` made date-dependent tests deterministic.
- Generated CMS config from a YAML file with anchors (shared field groups) kept 12 collections consistent.
- Content stored as Markdown/YAML in Git: editors use the CMS, technical volunteers can use GitHub's web editor.
