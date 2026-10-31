# Verification quickstart

1. Run source/normalization and installer tests with temporary private runtime homes.
2. Install pinned pyATS into a fresh spec160 runtime, never the owner runtime.
3. With synthetic environment credentials, run the one-process session on each source
   fixture, first preview then explicit activation/list. No probes or device commands.
4. Exercise duplicate names, partial/stale records, missing SSH facts, unknown OS,
   missing credentials, unsafe source/file/REST inputs, active replacement/deletion,
   concurrency and restart. Confirm old active state remains on failures.
5. Exercise VS Code and terminal static/dynamic source choices, cancel/resume and
   static preservation; inspect persisted plan and private env only via sanitized
   assertions. Do not include credential values in evidence.
6. Build extension, run relevant regression suites and catalog/coherence checks.
7. Record actual results and unavailable live/platform rows in verification.md.
