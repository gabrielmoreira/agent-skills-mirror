# Memory Guide

Agent Zero can remember useful facts, solutions, preferences, and imported
knowledge so future chats do not always start from zero.

That power needs curation. Long-term AI memory is not a solved problem, even for
large AI labs and companies. A memory system can help the agent become more
useful, but it can also preserve stale assumptions, wrong conclusions, old test
data, or instructions that no longer fit. A sustainable memory system needs some
human gardening.

When Agent Zero does something unexpected, keeps repeating a bad habit, or seems
strangely confident about the wrong thing, Memory is one of the first places to
look.

## Open Memory

Open **Memory** from the dashboard or sidebar.

![Memory dashboard](../res/usage/memory-dashboard.png)

The dashboard shows remembered entries and imported knowledge chunks. Each row
has metadata, a content preview, copy and delete actions, and a detail view.

## Search And Filter

Use the controls at the top to narrow what you are looking at.

![Memory dashboard controls](../res/usage/webui/memory-dashboard-controls.png)

The most useful controls are:

- **Memory Directory:** choose the memory store you want to inspect.
- **Area:** filter between `main`, `fragments`, `solutions`, and `skills`.
- **Search:** find memories related to a phrase, behavior, project, tool, error, or preference.
- **Threshold:** adjust how strict the similarity match should be.
- **Limit:** control how many results are returned.
- **Clear:** reset the filters.

Start with ordinary words. If Agent Zero keeps using the wrong command, search
for the command. If it keeps assuming the wrong project rule, search for the
rule, client name, repo name, or phrase it keeps repeating.

## Inspect And Edit

Click a memory row to open its details.

![Memory editing](../res/usage/memory-editing.png)

In the detail view you can:

- read the full content;
- check whether it came from conversation memory or imported knowledge;
- copy the memory with metadata;
- copy only the content;
- edit the text;
- delete the entry.

Edit a memory when it is almost right but needs correction. Delete it when it is
wrong, obsolete, duplicated, too vague, or harmful to future reasoning.

## What To Keep

Good memories are durable and useful:

- stable user preferences;
- project-specific conventions;
- commands that were verified and still apply;
- decisions that should persist across chats;
- known solutions to recurring problems;
- important constraints that are not obvious from files alone.

Good memory reads like a note you would happily give a future teammate.

## What To Remove

Remove or rewrite memories that are likely to poison future processing:

- stale setup instructions;
- old paths, ports, service names, or commands;
- temporary experiments;
- failed guesses saved as facts;
- outdated project decisions;
- broad personality instructions that make the agent overcorrect;
- private data that should not have been remembered;
- memories copied from a confused or interrupted chat.

The danger is not that one bad memory always wins. The danger is that it becomes
one more piece of "evidence" nudging the agent in the wrong direction again and
again.

## When Behavior Looks Wrong

Check Memory early when Agent Zero:

- keeps following an old instruction after you corrected it;
- keeps using a tool, path, or workflow you no longer want;
- mixes two projects together;
- remembers a false preference;
- repeats a wrong explanation;
- ignores current project instructions in favor of old context;
- acts as if a test result or setup step happened when it did not.

A good debugging loop is:

1. Search Memory for the repeated behavior or phrase.
2. Open likely entries and read the full content.
3. Edit entries that are useful but inaccurate.
4. Delete entries that are simply wrong.
5. Run the task again with a clear correction in the chat.

## Use Project Memory For Project Context

Keep project-specific memories in the project where they belong. Client rules,
repository conventions, local commands, and workflow preferences should not leak
into unrelated work.

If Agent Zero is mixing contexts, check whether the memory belongs in global
memory or project memory. Moving from "global forever" to "this project only" is
one of the simplest ways to keep the system sane.

## Be Careful With Bulk Cleanup

The dashboard can select multiple rows and copy, export, or delete them.

Before deleting many memories:

- export or back up important entries;
- search narrowly instead of deleting by broad category;
- delete obvious junk first;
- keep useful solutions even if they are old;
- avoid wiping imported knowledge unless you know how to rebuild it.

Memory curation is not about making the database empty. It is about keeping the
right signal and removing the noise that makes the agent less trustworthy.

## Related

- [Usage Guide](usage.md): where Memory fits in the everyday Agent Zero workflow.
- [Projects Guide](projects.md): how project memory keeps client, repo, and task context separated.
- [Troubleshooting](troubleshooting.md): quick checks when Agent Zero behaves unexpectedly.
- [Backup And Restore](usage.md#backup-and-restore): what to do before large memory cleanup.
