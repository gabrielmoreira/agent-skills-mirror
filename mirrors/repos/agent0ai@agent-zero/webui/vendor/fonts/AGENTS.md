# WebUI Font Vendor DOX

## Purpose

- Own the locally served Rubik and Roboto Mono WebUI font bundle.
- Keep core typography available without internet access.

## Ownership

- `fonts.css` owns the local `@font-face` declarations and supported variable weight ranges.
- `*.ttf` files are clean upstream font artifacts.
- `*-OFL.txt` files own the corresponding upstream licenses.
- `README.md` records upstream provenance and artifact mappings.

## Local Contracts

- Font sources in `fonts.css` must remain same-origin relative URLs.
- Preserve normal and italic Rubik weights 300–900 and Roboto Mono weights 100–700.
- Keep each font artifact paired with its upstream license and pinned provenance.

## Work Guidance

- Replace fonts from a pinned official upstream revision rather than modifying binaries.
- Update `fonts.css`, licenses, and provenance together when changing the bundle.

## Verification

- Run `pytest tests/test_webui_offline_assets.py`.
- Smoke-test the main and login pages without external network access.

## Child DOX Index

No child DOX files.
