# xerj-blogposts — the house-writing corpus

Every post XERJ has published, as records, so an agent writing the next one
can retrieve how the last ones were argued instead of guessing at the voice.

## What is in it

One record per published post at `landing/blog/*.html` (excluding the index):
`id`, `title`, `description`, `published`, `url`, and the readable prose of
the post body, plus derived `cve_ids` / `release_ids` fields for posts that
cite them. 8 records at the 2026-10-08 rebuild (the exploit-hub post,
PR #1240), pinned to `a9ad4fc0117db67bb0086a66eaa8dad8398afdb1` of this
repository; 7 at the first build, pinned to
`fce97e180e558df407af8d453bd52d5a7968b091`.

## Rebuild

```sh
python3 tools/packs/xerj-blogposts/gen_posts.py      # regenerate posts/*.json
python3 tools/packs/xerj-blogposts/gen_posts.py --check   # CI: fail on drift
cd engine && cargo run --release -p xerj-server -- corpus build xerj-blogposts \
  --recipe ../tools/packs/xerj-blogposts/recipe.toml
```

The `--check` mode is the staleness gate: the corpus is derived from the
site, and the two must not diverge. A new post lands with its record in the
same PR.

## Why it exists

The corpus program has a rule against indexing this repository (rule 3 of the
`xerj-code` skill: a reference corpus returns other people's work as
precedent; ours would return our own mistakes). This corpus is the scoped
exception the rule allows: it indexes only the published prose, never engine
code, and it exists because the posts ARE a work product an agent needs to
retrieve — the house voice, the arguments, the numbers, the habit of
publishing losses.

Licence: our own Apache-2.0 prose. No third-party content.
