# Security

## Reporting

Report vulnerabilities via this repository's GitHub Security Advisories. If advisories are turned off, open a GitHub Issue. Do not send a personal email.

## Bundled scripts

Review scripts under a skill before running them. Skills must not contain `.env` files or live API keys.

## Browser / CDP

`chrome-browser-automation` and `grokimagine` drive a real Chrome over CDP. They are not CAPTCHA or anti-bot tools. Stop if you find bypass instructions.

## Sanitize (contributors)

Placeholders only. Rules live in [CONTRIBUTING.md](CONTRIBUTING.md).

## Maintainer greps (published tree)

Scan **published files** for these classes. Never put a real profile name into docs.

- Mailbox domains (personal inboxes such as `gmail.com`, `outlook.com`)
- `C:\Users\` plus a real username (`C:\Users\<user>` / `C:\Users\<you>` placeholders are OK)
- Vault / cloud-drive roots
- Live token prefixes (`sk-`, `ghp_`, `xai-`, and similar). An English word that happens to contain `sk-` is not a key.

Published files are sanitized; this repo’s git history is not rewritten and is not claimed PII-clean.
