# channel/wechat

The WeChat channel: how to reach YOUR user's thread in WeChat and
speak there. `open` navigates to the thread by in-app search
(skipped when the thread already shows, or when WeChat resumes on it
after the dock tap), `send` runs `open` as its first step and then
pastes and sends a message into the thread, and `boot/` is the walk
every wake plays first: reach the thread, read the request, hand the
matching playbook the baton.

## Device

Recorded on WeChat with an English system (guards accept both the
English and 中文 labels). The thread page's one anchor is the contact
name in the centered title box, never the top band: an iOS notification
banner prints the same name left-aligned at the same height.

## Traps

- WeChat search can put a "Searched ID" account first; `send` refuses
  to type unless the thread title matches, so a wrong hit aborts.
- WeChat resumes on the last search when a thread was opened from one,
  with the term still in the field, so a second search in the same wake
  (the boot's `open`, then a `send`) would paste the contact name twice
  and hit a stranger's "Searched ID" card. `open` taps the field's
  clear (x) before pasting; on an empty field the tap only keeps focus.
- `<<CONTACT>>` must be exactly what the app shows as the thread title.
