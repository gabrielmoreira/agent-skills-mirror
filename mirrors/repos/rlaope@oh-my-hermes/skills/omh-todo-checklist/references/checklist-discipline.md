# Plan Checklist Discipline

The shaping rules and the two stop reasons the workflow body points at. Open this while declaring or repairing a list; the body carries the rules that hold whether or not it is open.

## 1. When a checklist is not worth declaring

It costs a tool call, a panel, and a write on every subsequent change. It buys one thing: a reader who can see where a run is without asking. So it pays when the work spans turns and somebody is watching, and it does not pay otherwise.

Do not declare one for work that is a single step, work already finished, or a question answerable in this turn. A checklist that is declared and never advanced is worse than none: the panel then asserts a plan nobody is walking, and a reader has to discover that by asking.

## 2. One checklist, in one tool

Hermes has a checklist tool of its own, `todo_list`. When `todo_list` is in your tool list or tool_search finds it, it holds the steps: write the list there and move its states there. OMH mirrors each of those writes into this plan todo, so the HUD and the plan's continuation and stall checks read it with no second copy. Writing the same list to `omh_todo` as well doubles every update and is never needed. Without `todo_list`, `omh_todo` holds the steps and everything below applies to it directly.

Three kinds of plan keep their steps in `omh_todo` even when `todo_list` is there, because what they depend on exists only on `omh_todo`: a planning run, whose `plan_stage` the edit gate reads; an accepted plan, whose `plan_stage=accepted` and `check:` items `omh_team` binds its lanes to; and a `code-story` template, whose phases a native list cannot carry. A plan awaiting acceptance and a template hold while they are open, and an accepted plan until it goes stale, finished or not; while one holds, a `todo_list` write is not mirrored over it. To leave one for unrelated work, end it first with `omh_todo action=clear`. Recording the person's redirect as `deferred_reason` instead keeps the plan, its stage and its gate, and pauses it: the plan line stops asking for its next item and the turn-end drive stops until the item list changes.

With `todo_list` holding the steps, call `omh_todo` only for what it alone records:

- an item's `blocked_reason` (`action=advance`, which on a plan `todo_list` holds keeps the state `todo_list` last set), kept across later `todo_list` writes while the item stays where it was or is paused from in_progress back to pending; resuming, completing or reopening it, or cancelling it while it is open, ends the reason;
- the plan's `deferred_reason`, which lapses at the next change to the list;
- the checkpoint/record/recall dossier (`references/closing-a-story.md`);
- advancing a done item to done again after its check passes, which is what binds that command to it.

The native states read as the record's: `in_progress` is `active`; `completed` is `done`, still a declaration and judged against recorded commands exactly as a `done` written with `omh_todo`; `cancelled` is `done` carrying a `blocked_reason`, the record's spelling of skipped.

## 3. Phases are numbered in delivery order

A phase groups items that finish together. Number them in the order they are delivered, so the label says where in the run the reader is:

    I. Bootstrap
    II. Wave One Delivery
    III. Review
    IV. Evidence and Cleanup

Items sharing a `phase` render as one section, and the HUD shows the current phase's checklist rather than the whole list. Phases that are not in delivery order make that view misleading rather than merely untidy.

Phase names and item text are written in English even when the conversation runs in another language. The HUD checklist is an operator surface under the repository's English-by-default output contract.

## 4. One item per observable outcome

An item is finishable by something a reader could check. "Implement the parser" is an outcome. "Think about the parser" is not, and it can never be honestly marked done.

The test: name what would make this item done. If the answer is a command that runs, a file that exists, a review that returned, or a state a person can look at, it is an item. If the answer is "when it feels finished", split it or drop it.

Subtasks use `depth` 1-3 and render indented beneath the preceding shallower item. They continue their parent's section, so they may omit `phase`. Use them when one outcome genuinely decomposes; a flat list of six is easier to read than a nested list of three.

## 5. The two reasons a plan stops, which are not interchangeable

This is the distinction that otherwise exists only inside the tool's JSON schema.

**`blocked_reason` — an item cannot proceed.** Per item. Name what it is waiting on: a review, an approval, a missing credential, another item. Any value here stops the plan advancing past that item. Remove the field once the thing it names arrives; it does not clear itself.

It is not for an item that is merely unstarted, slow, or mid-work, and not for one whose text happens to discuss blocking.

**`deferred_reason` — a person steered the session elsewhere.** Per write, not per item. Send it only when the user redirected this session away from the plan ("do Y first", "forget that for now"), naming what they asked for instead. While it holds, the plan stops asking for the next item, so the session serves the person without the checklist arguing.

It clears itself. It is stored with a digest of the item list it was sent with, and a reader honours it only while that digest matches. So resuming costs no clearing step: omit the field on the next write, which is the default. Any item change that does not re-send it ends the deferral too. Send it again alongside a changed item list only if the person is still steering.

**When both could apply, `blocked_reason` wins.** An item that genuinely cannot proceed carries it whatever the person is doing, because the two describe different facts: one is about the work, the other about the conversation.

## 6. One item, or the whole list

`action=advance` changes one item's state. It takes the item number (1 for the first), the start of that item's current text as a guard, and the new state; `blocked_reason` rides with it, and omitting that field clears one. A guard that no longer describes the text at that position is refused rather than applied, so a reference computed against a list that has since been re-set cannot change the wrong item. It is the same write as `action=set` by a narrower route: same validator, same stamp, same record.

`action=set` writes the whole list. Every write sends every item back, including unchanged ones and including the ones you only want to re-state. An item left out of a write is deleted, silently and without error. Declare and re-scope with it; tick with `action=advance`.

Read before re-declaring: `action=show` returns the current projection. Declaring over an existing list without reading it first is how a checklist someone else in this session was walking gets replaced.

## 7. States

`pending`, `active`, `done`. Exactly one item is active while work is in progress. A finished list has every item `done` and none active.

A state is a declaration. `done` records that the writer says the outcome happened; it is not an observed result, and a reader wanting proof needs the evidence cited separately.
