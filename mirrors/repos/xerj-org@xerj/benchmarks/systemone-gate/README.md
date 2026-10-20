# The /v1/systemone acceptance gate — jev-reranker, unmodified, on a XERJ node

Run 2026-09-21, locally built `xerj-server` at the vote-text fix (#1000/#1001),
`--port 9490` (native REST on 9491), throwaway data dir, `[decisions]
index = "sms"` (`gate-decisions.toml`: k=10, text/label fields,
`positive_label = "spam"`). Client: `pip install jev-reranker` (0.1.2, MIT) —
no patches, no subclassing, its own listwise instruction template, its own
splitting, its own strict response validation. The only configuration:

```sh
TYPESAFE_ENDPOINT=http://localhost:9491/v1/systemone
TYPESAFE_API_KEY=<the node's admin key>
```

`TYPESAFE_BASE_URL` is silently ignored by the client — the endpoint variable
must carry the full path. (Verified in the wheel: `reranker.py:238`.)

## What ran

`gate_load_sms.py` indexes the 4,000-message SMS train split
(`benchmarks/decisions-as-retrieval`'s split: shuffle seed 7, first 4,000) and
fixes 10 held-out gate documents (5 spam, 5 ham, 40–140 chars) in
`gate-docs.json`. `gate_run.py` ranks them through BOTH client entry points:

1. the constructor default (listwise, compact instruction — references
   `` `documents.doc_N` `` and `` `query` `` in backticks);
2. `relevance_rerank()` — the documented relevance preset, which since client
   0.1.2 ships its rubric OBJECT in state and references it in backticks. The
   node acknowledges the rubric without embedding its prose in the vote
   (#1000's defect class); the two phases score identically, which is the
   proof.
3. the constructor default again, under a deliberately spammy query.

The query is `triage inbox unsolicited correspondence` — every term verified
absent from the corpus. Since client 0.1.2 the question itself references
`` `query` `` in backticks, so the query is named payload and joins the vote
BY CLIENT DESIGN (the question asked is "does this document answer this
query"). For a classification history that is noise, which is why the gate
query is neutral — and phase 3 proves the separation survives a spammy query
("winner claim free prize congratulations") that the pre-#1000 node would
have collapsed on (the first gate attempt then: spam 1.000 vs ham 0.785).

## Result (`gate-transcript.txt`)

The client's own validation IS the wire gate: answers keyed exactly by the
sent question ids, every answer `{type: "noul", noul}` numeric in 0..1,
`model` a non-empty string (it resolved `xerj-history-vote-1` — the node's
truthful echo, never a Jev name), `usage` non-negative integers. The semantic
gate, threshold 0.3: neutral query gap **0.8542** (spam mean 0.9447 vs ham
0.0905, identical across both entry points), spammy query gap **0.6087**. No
request left the node: the vote is an ordinary search of the `sms` index;
the module adds no outbound client.

## The response the client does not show

`/_decide` exposes the same vote with its evidence — neighbours, labels,
engine scores, weights, and an abstain verdict below `decisions.min_confidence`:

```sh
curl -s localhost:9490/_decide -H 'content-type: application/json' \
  -H "authorization: ApiKey $(cat <data_dir>/admin.key)" \
  -d '{"index":"sms","question":"URGENT! Your Mobile number has been awarded"}'
# {"index":"sms","k":10,"label":"spam","confidence":1.0,"abstain":false,
#  "neighbours":[{"_id":"1805","label":"spam",...,"weight":1.0}, ...]}
```

Zero-support questions are a 422 naming the question ids, never a fabricated
0.5; `score` questions (no vote analogue) are a 422 naming the alternative;
a backtick reference that resolves to nothing is a 422 naming the path. All
pinned by `engine/crates/xerj-api/tests/systemone_http.rs`.
