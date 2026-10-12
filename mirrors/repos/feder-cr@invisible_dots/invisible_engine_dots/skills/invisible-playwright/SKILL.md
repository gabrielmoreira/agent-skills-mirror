---
name: invisible-playwright
description: Use the Dot's browser identities for any task on a website or search on the web: which identity to use, opening and closing one, and when a plain download is simpler than a browser.
---

# The browser identities

Your browser is invisible_playwright: a real Firefox that a site sees as a person at a computer. How to drive a page
(finding a page, the order to try things in, what a page can tell) is in the browser server's instructions, which your
system prompt carries. This file is about the identities. Use the browser when a task needs a website; for a plain
download or an API, `exec` with `curl` is simpler.

## Identities

A browser identity is one person on the web: its own profile, cookies, logins and fingerprint, kept on disk between
uses.

- `browser_identity_list` shows the identities, which are open, and how many may be open at once.
- `browser_identity_create` makes one, closed. Give it a name only: it then leaves through this computer's own network,
  which is right unless the person asked for this one identity to use a proxy of theirs.
- `browser_identity_launch` opens it on your desktop. The first launch of a new identity can take minutes.
- `browser_identity_close` closes it; its profile, cookies and logins stay.
- Every page tool takes the `identity_id` of an open identity, and acts on that identity's one page.
- Reuse the identity that is already logged in to a site instead of making a new one, and keep one identity per
  person or account you act as: two accounts in one identity are one person to anyone looking.
- A second identity is for what must not touch the first. The usual case: signing up somewhere and needing a mailbox
  for the verification. Open a throwaway-mail site in another identity, take the address, type it into the form in the
  first one, and go back to the other for the link.

Close an identity with `browser_identity_close` once the task no longer needs it, before you answer: an open browser
holds memory on your computer.

## Your own skills

When you work out how to do something on a site that you will do again (where its login is, which steps a form needs,
what blocks you), write it down as a skill of your own: /home/dot/skills/<name>/SKILL.md, the same shape as this file.
