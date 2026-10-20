# xerj-decide — training + export harness (issue #1064)

This crate trains and exports the **open `xerj-decide` model**: the tier-2
local decide head that `xerj --decide-mode local --decide-model-dir …`
loads. The artifact is a plain directory — `config.json`, `tokenizer.json`,
`model.safetensors`, plus `VERSION.json` and `MANIFEST.sha256` — read by the
**existing loader** in `engine/crates/xerj-ai/src/decide.rs`. This harness does
not modify the loader; trainer and server run the same
`candle_transformers` `ModernBertForSequenceClassification::forward` against
the same tensor names, so the architecture cannot drift between the two.

The eval card for the shipped weights is
[`docs/DECIDE_MODEL.md`](../../docs/DECIDE_MODEL.md).

## Reproduce

```sh
cd benchmarks/decide-model
cargo build --release

# 0. data (downloads the three source files, verifies sha256)
./scripts/fetch_data.sh data

# 1. the tokenizer is a FROZEN input of the recipe, not a derived artifact:
#    the tokenizers crate's fit is not stable across processes (its trainer
#    iterates a randomly-seeded HashMap; measured 8740/8741/8742 on this
#    corpus, and forcing the crate's sequential path does not remove it), so
#    one fit is committed at pinned/tokenizer.json and every run copies it.
mkdir -p work && cp pinned/tokenizer.json work/tokenizer.json

# 2. train. Seeds are flags; defaults are the v1 recipe. ~15 min/epoch on a
#    32-core dev box, checkpoints per epoch under work/.
cargo run --release -- train --data-dir data --workdir work --epochs 5 --name v1

# 3. held-out numbers (full Banking77 test + full SMS held-out rows)
cargo run --release -- eval  --data-dir data --workdir work

# 4. the publishable directory, verified by reloading it through the same
#    mmaped-safetensors path the server uses
cargo run --release -- export --data-dir data --workdir work --out artifact/xerj-decide-v1
```

With the pinned tokenizer in place, everything downstream is deterministic
end to end: the RNG is splitmix64 (pinned stream test in `src/rng.rs`), the
epoch data order comes from `stream_seed(seed, epoch)`, and weight init is
written from the same stream in sorted-tensor-name order
(`src/model.rs::init_deterministic`) because candle's CPU RNG cannot be
seeded. No code path in the artifact reads a clock or an environment
variable. (`cargo run --release -- tokenizer` fits a fresh tokenizer when
you want one for a different corpus — just do not expect a fresh fit to be
byte-identical to the pinned one.)

### Leave-one-out runs (the honest zero-shot numbers)

`--exclude` removes a dataset from training *and* from the dev holdout, then
`eval` scores that dataset's held-out rows with a head that never saw it:

```sh
mkdir -p work-no-banking && cp pinned/tokenizer.json work-no-banking/
cargo run --release -- train --data-dir data --workdir work-no-banking --exclude banking77 --epochs 5 --name loo-banking
cargo run --release -- eval  --data-dir data --workdir work-no-banking --exclude banking77   # scores the full banking77 test
```

### Serving latency

With the exported artifact on disk:

```sh
xerj --insecure --port 9410 --data-dir ./tmpdata \
    --decide-mode local --decide-model-dir ./artifact/xerj-decide-v1
python3 scripts/eval_latency.py --es http://localhost:9410 --native http://localhost:9411 \
    --labels-csv data/b77_train.csv --out work/latency.json
```

Use a **private port and a throwaway data dir** — never the shared
reference-coding server.

## Layout

| path | what |
|---|---|
| `src/rng.rs` | splitmix64 stream; the only randomness anywhere in the harness |
| `src/data.rs` | readers, pinned sha256s, seed-7 SMS split, licence record |
| `src/corpus.rs` | the hypothesis templates (byte-identical to the loader's) and the 3-way NLI pair construction |
| `src/model.rs` | the head: ModernBERT-class classifier built on a `VarMap`, deterministic init, the serving-mirroring `score` |
| `src/train.rs` | AdamW + warmup-cosine, epoch-seeded shuffles, per-epoch checkpoints |
| `src/evaluate.rs` | accuracy / ECE / coverage-at-0.8 / P-R-F1, scored through `Head::score` exactly as the server scores |
| `src/export.rs` | writes the three loader files + `VERSION.json` + `MANIFEST.sha256`, then reloads the artifact and requires score agreement |
| `pinned/tokenizer.json` | the frozen wordpiece tokenizer every run trains from (see Reproduce for why it is an input, not an output) |
| `scripts/fetch_data.sh` | data download + digest check |
| `scripts/eval_latency.py` | `/_decide` and `/v1/systemone` p50/p99 against a booted node |
| `scripts/publish_bundle.sh` | assembles the Hugging Face upload bundle |

`data/`, `work/`, and `artifact/` are gitignored. The weights blob is ~30 MB
(over the 5 MB commit ceiling for this repository), so the repository carries
the harness, the manifest and the publish bundle — not the safetensors.

## Licences

The **weights are Apache-2.0 from xerj-org**. They were trained on two public
CC-BY-4.0 datasets (Banking77 from PolyAI-LDN; the UCI SMS Spam Collection),
recorded in the manifest's `training_data` with the attribution that licence
asks for. Those terms govern the datasets and are provenance for the weights —
they are not a grant xerj-org makes. See `src/data.rs` for the full licence
text and citations.
