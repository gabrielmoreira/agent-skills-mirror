# Copilot instructions for this workspace

This workspace manages the user's **Chrome bookmarks** on the local machine.

- For anything bookmark-related, use the `chrome-bookmarks` skill
  (`.github/skills/chrome-bookmarks/SKILL.md`) and its script via `python bmk.py ...`.
- Never edit the browser's `Bookmarks` file by hand or with ad-hoc code; always go
  through the script (it handles checksums, backups and atomic writes).
- Bulk/destructive commands preview first; only add `--yes` after the user
  explicitly approves. Never add `--force`.
- Scratch files (exports, plans, reports) go in `.bmk/`, which is git-ignored.
- The script is stdlib-only Python 3.9+; run tests with
  `python -m unittest discover -s tests -v` after changing it.
