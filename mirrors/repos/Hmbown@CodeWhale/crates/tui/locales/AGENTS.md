# crates/tui/locales — agent guidance

Eight UI packs. `en.json` is the reference; ja, zh-Hans, es-419, pt-BR, vi,
and ko are **complete packs** held to exact raw key parity with English;
zh-Hant is **intentionally partial** (#4057, Setup core only).

## Adding or changing a string

1. Add the `MessageId` variant, the `ALL_MESSAGE_IDS` entry, and the
   `en.json` key — all three, or
   `message_id_list_english_pack_stay_in_exact_sync` fails.
2. Translate into every complete pack, or
   `shipped_complete_packs_have_raw_key_parity_with_english` fails. Do not
   "fix" that test by copying English into a pack — the whole point is that
   the silent English fallback is invisible at runtime, so the gate is the
   only thing standing between users and untranslated UI.
3. If you change an **existing English value**, retranslate it everywhere
   (including zh-Hant if it carries the key). Value drift is invisible to
   the key gates; say what you changed in the commit body.

## Translation conventions

- `{named}` placeholders stay literal; call sites substitute with
  `.replace()`.
- Product terms stay English per pack convention: Fleet, Plan / Act /
  Operate, Ask / Auto-Review / Full Access (see `HomeAgentModeYoloTip` in
  any pack for the pattern). Plain words ("read only", phase words)
  translate naturally and must stay short — footers and row controls
  render them in tight budgets.
- Key names (`Enter`, `Alt+?`), commands (`/fleet setup`), and glyphs are
  never in translations; they are composed in code.
- Preserve intentional leading/trailing spaces (pane titles, `Rule  `,
  the slash-menu hint).

## Adding a locale

Mirror what PR #4347 (Korean) did: pack JSON with full parity, `Locale`
variant + tag/display/parse arms in `localization.rs`, onboarding picker
entry (`language.rs` — a test forces every shipped locale to be offered),
setup-wizard match arms, and locale display arms in the config/change
commands. The `/config` hint and invalid-locale error derive from
`Locale::shipped()` automatically.

## READMEs

Translated READMEs (repo root) are separate from these packs but follow
the same discipline: `scripts/check-readme-translations.py` (in CI) fails
when English changes without the six translations being refreshed and
restamped.
