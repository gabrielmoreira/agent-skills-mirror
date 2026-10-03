# Windows + PowerShell notes for these projects

- Source files are often CRLF. Multi-line `.Replace()` in PowerShell silently fails on CRLF; use the edit
  tool, a small Node script, or normalize with `` `r`n ``.
- Astro dynamic routes contain brackets (`src/pages/events/[slug]/index.astro`). Use `-LiteralPath`, or
  `[IO.File]::ReadAllText/WriteAllText` with **absolute** paths (.NET ignores PowerShell's current directory).
- `sharp` keeps file handles open on Windows. Read the file into a Buffer first, then write the output.
- Playwright's `webServer` fails if port 4321 is busy. Stop any `astro preview` you started before running
  `npx playwright test`. Use another port (e.g. 4400) for ad-hoc previews.
- `&&` only chains native commands in PowerShell; use `;` before PowerShell statements.
- Never `Stop-Process -Name`; stop the exact PID you started.
- Pushing to a personal GitHub account from a machine signed in to a work account: use a one-shot header,
  e.g. `git -c credential.helper= -c "http.https://github.com/.extraheader=AUTHORIZATION: basic <base64 of x-access-token:TOKEN>" push origin main`
  and `GH_HOST=github.com GH_TOKEN=<token> gh …`. Never echo the token.
- Commit identity for a personal repo: use the account's `<id>+<login>@users.noreply.github.com` address.
- ffmpeg is not installed by default: `npm i --no-save ffmpeg-static` in a scratch folder and call its path.
- Python for PDF parsing: `pip install pymupdf`.
- Work machines often point npm at a company mirror (`npm config get registry`). Installs work, but the
  lockfile records the mirror's URLs. Before committing to a public repo, run
  `node <kit>/skills/site-quality-gates/scripts/normalize-lockfile.mjs`. Direct HTTPS to
  `registry.npmjs.org` may be blocked on such networks; let GitHub Actions verify installs.
- Lighthouse CI on Windows can fail with `EPERM … lighthouse.<n>` while deleting Chrome's temp profile.
  That is a clean-up error, not a score; rely on the Linux CI run.
- `npm run build` (Astro + sharp) very occasionally crashes on Windows with
  `Assertion failed: !(handle->flags & UV_HANDLE_CLOSING)` from libuv. It is a Node/Windows issue, not
  your code: rerun the build. If it repeats, close other Node processes and retry.
