# Creator Workflow

## Creator authority

`short-drama.json#/creator_authority` stores accepted creator constraints, visual direction and production
profile choices. A skill may draft choices, but only the creator or an explicitly authorized delegate can accept
them. If nobody has decided, keep the artifact pending; do not infer acceptance from silence or from a request to
preview the whole pipeline.

Use project-relative paths and stable record IDs when one artifact points to another. Human-facing records do not
need lifecycle digests. Deterministic source indexes may still carry byte spans because their job
is exact source extraction, not workflow state.

## Entry points

| Creator asks for | Owner | Minimum input |
|---|---|---|
| Develop an idea or episode map | `short-drama-develop` | brief or conversation |
| Analyze a long source | `short-drama-novel-analyze` | preserved source file |
| Write or revise an episode | `short-drama-write` | idea, episode card, outline or script |
| Extract assets | `short-drama-assets` | current script |
| Create image prompt specs | `short-drama-image-prompts` | current asset facts |
| Design shots/keyframes | `short-drama-storyboard` | current script and asset facts |
| Create video prompt specs | `short-drama-video-prompts` | current shots/keyframes |
| Produce images, video or TTS | `short-drama-produce` | current bounded job plus explicit confirmation after preview |
| Review | `short-drama-review` | bounded artifact set |
| Initialize, continue, show or deliver | `short-drama` | project path or target path |

Direct entry is valid. Do not fabricate upstream files merely to make a nominal pipeline complete.

## Branches

```text
direction / story development (when needed)
              |
           screenplay
              |
            assets
          /        \
 image prompts   storyboard -> video prompts
          \        /
       confirmed production
                |
             review -> delivery
```

Look Development is optional. Image prompts and storyboard are sibling branches after asset facts exist.

## Preview, confirmation and revision

A request for an end-to-end preview authorizes drafting, not acceptance. Its runtime contract is **one bounded work unit per turn**:

1. choose one owner stage; for a high-fanout stage, choose one explicit contiguous batch;
2. read only that unit's direct inputs, draft or revise it, and run its local structural checks;
3. persist a candidate without inventing creator acceptance;
4. report the included scope, remaining scope and next useful action, then **return control to the creator**.

The turn ends at step 4. A creator message such as “continue” authorizes the next bounded unit. The next owner
stage, review and production each begin on their own explicit request; review also runs when an explicitly
requested delivery needs a verdict. Undecided work stays in `needs_confirmation`, and delivery waits until the
creator accepts the relevant outputs.

For a revision:

1. identify the artifact and owner;
2. read only its direct current inputs;
3. show the semantic change and what should remain unchanged;
4. let the owner publish the revision;
5. request creator acceptance when canonical meaning changed;
6. report whether a separate bounded review is still needed; do not start it automatically.

Changing an upstream file does not recursively rewrite project state. A consumer that directly recorded that file
shows `update_needed`; republish the consumer when the creator actually wants it refreshed.

Rendered prompt Markdown is a view of its structured spec. If someone edits the rendered view, either regenerate
it, adopt the change into the spec, or reconcile both explicitly.

## Delivery boundary

Deliver only explicitly selected, current, approved text and JSON in the text package. Produced media remains in
its project production directory and may be exported by a separate creator-approved media handoff. Exclude private
sources, credentials, absolute paths and machine state. `verify` checks checksums; it does not judge creative quality.
