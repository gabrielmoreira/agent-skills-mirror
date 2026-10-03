# Retiring a Skill

Read this when a request asks to retire, withdraw, or remove a skill from the collection. It is the only home for the subject: what the retiring commit does, and what the release makes of it.

## Removing a skill that was never released

Cleanup, nothing more. Delete everything the skill owns — `skills/<skill-name>/`, `trials/fixtures/<skill-name>/`, and `trials/pending/<skill-name>/` where it still has a queue. There is no catalog row to drop, no changelog, and no user who could have installed it, so nothing is announced and no reason is owed. The release does not detect it — it was never in a catalog to disappear from. Everything below is about a skill that was published.

## Retiring a released skill

One commit, one skill, deleting everything that skill still owns:

- `skills/<skill-name>/`
- `trials/fixtures/<skill-name>/`
- `trials/pending/<skill-name>/`, where the skill still has a queue. A pending question asks what a skill should do, and the retirement is the answer — leaving the queue behind offers a later session work on a skill that no longer exists.

The commit body states why it was retired and what replaces it. That body is the announcement its users read, word for word. If the reason is a security defect, say so plainly — the release note is how someone learns to uninstall it.

**Where the request gives no reason, ask for one plainly.** Never infer it from the diff or write a placeholder. The release refuses to announce a retirement it cannot explain, so an invented reason is worse than a question.

The retiring commit leaves the root README alone, like every other commit that changes bundle content. Its catalog row is dropped by the release that announces the retirement — the same release that adds a row for a skill published for the first time.

Until then the row stands, and so do its download link and any sibling link pointing at the skill. `check-docs.py` recognizes a skill the last snapshot published whose directory is now gone, and holds those open instead of reporting them broken. It names every such skill at the end of each run, and names any whose deleting commit has an empty body, so release preparation sees what it still owes before the generator refuses to announce it.

## What the release does with it

Detection compares the previous snapshot tag with `HEAD`: a skill the root catalog listed at that tag, whose directory is now gone, is retired in this snapshot. The catalog at a tag is that snapshot's own record of what it published — changelogs were introduced later and cannot answer this for early snapshots. The skill's title and last released version come from that same row, so a snapshot whose manifest can no longer be read is named correctly anyway. There is no list to maintain and no row to date.

The reason is the body of the commit that deleted the skill, and nothing else. Where that body is empty the release fails rather than announcing a withdrawal it cannot explain — fix the commit, do not work around it. Release preparation is also where the catalog row is dropped, alongside giving the retirement its reason.

The note carries the title, the last released version, the reason, and a statement that the skill receives no further updates or fixes. It carries no download link: an existing user already has the bundle, and no one should install an unsupported skill. Retirements render first in the release notes, ahead of new skills and improvements, because they are the only entry that asks an existing user to act.

The announcement happens exactly once, without anyone tracking that it did: the next snapshot compares against this one, whose catalog no longer lists the skill. The bundle stops being carried forward from this snapshot on; never hand-build or attach a retired skill's bundle.
