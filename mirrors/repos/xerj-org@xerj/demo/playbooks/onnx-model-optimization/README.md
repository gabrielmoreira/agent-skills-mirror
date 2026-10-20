# Transform the exact pinned MiniLM export into a fused FP32 graph

This offline recipe transforms one exact, previously recorded
`sentence-transformers/all-MiniLM-L6-v2`-compatible ONNX export into one exact
transformer-fused FP32 graph. It does **not** download, commit, install, select,
or recreate the source model. The approximately 90 MB source and output remain
external runtime assets.

This is a checksum-locked transformation recipe, not a from-upstream
reproduction recipe. You must already possess the exact source model and
tokenizer bytes listed below. The repository does not publish those assets or
an immutable exporter revision, and a fresh generic `optimum-cli export` is not
expected to reproduce them.

The recipe is intentionally narrow and fail-closed:

- CPython 3.13.5 and every optimizer package are exactly version-pinned; every
  selected wheel is SHA-256 pinned;
- source model and tokenizer must match measured lengths and SHA-256 hashes;
- the result must match the measured bytes, hash, interface, opsets,
  initializer types, and complete operator inventory;
- a lock is acquired with `O_EXCL`;
- candidate and manifest are staged and synced inside one private sibling
  directory, then the complete directory is atomically published without
  replacement;
- any mismatch exits non-zero without publishing an artifact.

The final output directory does not become visible until both files are
complete. A process or machine failure may leave a hidden sibling staging
directory or lock, but cannot publish a partial final directory. First confirm
that the PID in `.<output-directory>.optimize.lock` is no longer alive; then
remove the hidden staging directory and stale lock before rerunning. Never
delete a live lock.

## Locked environment

The lock targets ordinary CPython 3.13.5 on GNU/Linux glibc x86-64, the only
generation environment used for the exact byte result. It is not a general
cross-platform Python lock.

```bash
python3.13 -m venv /path/to/xerj-onnx-recipe-venv
/path/to/xerj-onnx-recipe-venv/bin/python -m pip install \
  --only-binary=:all: \
  --require-hashes \
  -r demo/playbooks/onnx-model-optimization/requirements-linux-x86_64-cp313.lock
```

## Transform the pinned source

```bash
/path/to/xerj-onnx-recipe-venv/bin/python \
  demo/playbooks/onnx-model-optimization/optimize_minilm_fp32.py \
  --source /models/minilm-source/model.onnx \
  --tokenizer /models/minilm-source/tokenizer.json \
  --output-dir /models/minilm-fused-v1
```

The published directory contains `model.bert-fused-fp32.onnx` and
`model.bert-fused-fp32.manifest.json`.

Required inputs:

| Asset | Bytes | SHA-256 |
|---|---:|---|
| source model | 90,405,214 | `6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452` |
| tokenizer | 466,247 | `be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037` |

Required result:

| Asset | Bytes | SHA-256 |
|---|---:|---|
| fused model | 90,276,689 | `d45c738311abe1488b6d9e2862e1db08267fc31d6f301d8f26163e2fb4956b9c` |

The manifest embeds the complete checked-in artifact contract and records the
observed source and candidate graph inventories plus the exact toolchain.
Before publication, the recipe enforces the observed source and tokenizer
bytes and hashes, candidate bytes, hash and complete graph inventory, package
versions, interpreter, and the optimizer arguments that it actually executes.

Other contract fields are recorded metadata, not observations made by this
script: artifact name/version, source license and provenance, the XERJ
embedding contract, and the compatibility support boundary. In particular,
the original experiment did not preserve an immutable upstream export
revision. Exact source bytes are pinned, but a stronger upstream provenance
claim would be dishonest.

[`artifact-contract.json`](artifact-contract.json) is the checked-in expected
contract. The generated manifest adds the complete inspected source and
candidate inventories and must agree with it.

## Use with XERJ

Build and start XERJ as described in
[`docs/EXPERIMENTAL_ONNX.md`](../../../docs/EXPERIMENTAL_ONNX.md), using the
generated model:

```bash
target/release/xerj \
  --insecure \
  --data-dir /var/lib/xerj-fused \
  --embed-mode onnx-experimental \
  --onnx-model /models/minilm-fused-v1/model.bert-fused-fp32.onnx \
  --onnx-tokenizer /models/minilm-source/tokenizer.json

target/release/xerj autoindex /path/to/corpus \
  --url http://localhost:9200 \
  --prefix finance-minilm-fused-v1 \
  --fresh
```

The fused graph is a **new embedding identity**. Its output is numerically
distinct from the source graph for XERJ because the model hashes differ. Never
resume an index created with the source model under the fused model. Retain the
old asset for the old index, or use `autoindex --fresh` with a new prefix. Do
not bypass `embedding_identity.json`.

## Compatibility boundary

This is offline transformer fusion (`opt_level=0`), not a hardware-specific
ONNX Runtime optimized-session cache. The graph nevertheless contains
`com.microsoft` contrib operators. The proven product path is ONNX Runtime
transformer optimizer 1.22.1 for generation, then XERJ's `ort`/`ort-sys`
2.0.0-rc.12 API-24 CPU path on GNU/Linux glibc x86-64. The generation-tool
version is not a claim that XERJ consumes the graph through runtime 1.22.1.

Do not infer support for another runtime/API line, CPU architecture, execution
provider, musl build, or non-ORT consumer. Even where the graph loads,
different kernels or CPUs can change floating-point output. Run the
asset/runtime and retrieval gates before expanding the support matrix.

XERJ already requests ONNX Runtime Level3 graph optimization when it creates a
session, including for an unfused source graph. This repository contains no
published measurement showing that the offline-fused asset improves session
initialization time, steady-state throughput, or retrieval quality beyond that
runtime optimization. Those are separate measurements: a cold-start result
cannot establish a steady-state benefit. The recipe currently provides a
byte-pinned fused artifact and inspection trail, not a public performance
claim. Adopting it also creates a new model identity and therefore requires a
fresh index, as described above.

## Evidence boundary

This recipe was extracted from an internal optimizer screen whose evidence is
not published in this repository. Therefore this playbook makes no public
speed or retrieval-quality claim. Any future claim needs checked-in sanitized
evidence and the repository's applicable quality and performance gates.

Run focused tests without invoking the 90 MB optimizer:

```bash
PYTHONPATH=/path/to/xerj-onnx-recipe-venv/lib/python3.13/site-packages \
  python3.13 -m unittest \
  demo/playbooks/onnx-model-optimization/test_optimize_minilm_fp32.py
```
