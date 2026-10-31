"""btlib — step-level replay of Agentforce STDM traces (stdlib only).

One replay unit = one production LLM_STEP: the exact request that step sent (messages in
production order, the step's own tool definitions) and the answer it got (the golden).

    redact    scrub bearer tokens / JWTs from anything written or printed
    stdm      read STDM_RESULT payloads out of `sf apex run --json` output
    messages  rebuild a step's request messages in production layout
    units     one bt.unit/1 record per LLM_STEP
    sfap      SFAP /chat/generations client (urllib, token read per call, retries)
    judge     binary LLM judge for text replies and free-text arguments
    scoring   decision / names / args / text scores, failure buckets, schema checks
    results   run-dir artifacts: results.jsonl, summary.json, the legacy CSV
    agentsrc  read an .agent file: node instruction blocks, tools, rendering rules
    patch     edit ops on the captured requests (--patch), with per-op coverage
    agentpatch the same edit ops in the .agent file: the version that ships is the one scored
    versions  which retrieved agent version each unit renders from (--agent-versions)
    splits    session-level test / val labels (--val-fraction) and --exclude-sessions
    cache     answers already received, keyed by the payload as sent (--cache-dir)
    tokens    mint a new SFAP token when the run's expires (--token-org)
    compare   paired comparison of two runs of the same units, with a noise band (bt_compare.py)
    fetch     STDM sessions through read-only anonymous Apex, nothing deployed (bt_fetch.py)
"""

SCHEMA_UNIT = "bt.unit/1"
SCHEMA_RESULT = "bt.result/1"
SCHEMA_SUMMARY = "bt.summary/1"
SCHEMA_PATCH = "bt.patch/1"
SCHEMA_COVERAGE = "bt.patch_coverage/1"
SCHEMA_VERSIONS = "bt.versions/1"
SCHEMA_CACHE = "bt.cache/1"
SCHEMA_COMPARE = "bt.compare/1"
SCHEMA_FETCH = "bt.fetch/1"
SCHEMA_KIT = "bt.fetch_kit/1"
