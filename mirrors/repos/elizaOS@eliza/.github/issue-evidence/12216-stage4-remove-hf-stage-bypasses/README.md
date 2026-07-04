# Stage 4 Remove HF Stage Bypasses Evidence

Issue: #12321

PR scope:

- Remove `--allow-missing` from the per-tier HF model repo publisher so blocked bundle plans always exit non-zero.
- Remove `--skip-hash-verify` so publish planning always hashes and verifies staged artifacts.
- Remove the same bypass options from the Node staging wrapper and update the shell helper text.

Verification:

```bash
grep -R "allow-missing\\|skip-hash-verify\\|allowMissing\\|skipHashVerify" -n packages/training/scripts/publish packages/training/scripts/test_hf_publish.py | head -100
# no output

python3 -m pytest packages/training/scripts/publish/test_publish_eliza1_model_repo.py -q -k 'dry_run_blocks_missing_with_report or checksum_mismatch or harness_eval_missing'
# .. [100%] 2 passed

python3 -m pytest packages/training/scripts/publish/test_publish_eliza1_model_repo.py -q
# ................. [100%] 17 passed

python3 -m py_compile packages/training/scripts/publish/publish_eliza1_model_repo.py packages/training/scripts/publish/test_publish_eliza1_model_repo.py
# passed

node --check packages/training/scripts/publish/eliza1-hf-stage.mjs
# passed
```
