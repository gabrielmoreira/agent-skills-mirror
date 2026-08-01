# Public Reply Mode (GitHub issue / PR)

Loaded from `write` when the deliverable is a maintainer reply on a public issue or PR thread.

Activate when: "回复 issue", "reply to PR", "comment on #N", "回 issue", or the user asks for the text of a GitHub issue / PR comment.

Hard rules for the reply body:

1. **Open with `@<reporter>` + one thanks line.** Match the reporter's language (Chinese → "感谢反馈" / English → "thanks for the detailed report"). No exclamation mark. No emoji. No "🙏".
2. **Then state the cause in one sentence, the impact in one sentence.** No multi-paragraph background, no internal symbol names, no walk-through of the fix.
3. **Then state the ship state**, exactly one of: already shipped in v<X.Y.Z>, fixed on `main` and going out in the next release, planned for v<X.Y.Z>, not planned (with one-line reason and an alternative path). Every sentence must be true at the moment of posting: no "already shipped" without release evidence in the current turn, no "landed on main" while the change sits uncommitted, no implied verification (built a branch, ran an artifact) that did not happen.
4. **Two paragraphs maximum**, separated by one blank line. No bullet lists, no section headers, no code blocks except a one-line command when actually needed.
5. **A batch of replies is N replies, not one skeleton filled N times.** When closing or answering several threads in one pass, read the drafts side by side before posting: same opening clause, same paragraph order, and same closing move across three or more of them reads as template voice no matter how correct each one is. Only the facts are shared. The opening sentence in particular should come from that thread's own report.

The reply is the final user-facing text, not an agent log. Do not write "刚才我判断错了", "前面回复有误", "I re-read it and changed the comment", or any meta narration about your own process. If editing an existing maintainer comment, replace it with the clean final wording as if it were the only comment the user will read.

Before posting, re-read the live issue / PR with `gh issue view <num>` or `gh pr view <num>`. Do not reply from memory; titles, states, and author languages change between sessions.

For paid / subscribed users, acknowledge the purchase relationship and the inconvenience in one phrase, then state the boundary. Do not over-explain. When the current product cannot support their setup, suggest the safest practical path (upgrade macOS, wait for the next release, provide logs, refund route) without arguing.

For private support channels (DM, in-app reply, support email), drop the report register entirely: short colloquial sentences in the maintainer's own voice, lead with what the user gets rather than how it works, and fewer full stops than documentation would carry.

Closing rule: when closing as `completed`, the comment must independently explain what was fixed and the expected release. When closing as `not planned`, the comment must independently explain the current boundary and an alternative path. Do not rely on prior thread context as the explanation.
