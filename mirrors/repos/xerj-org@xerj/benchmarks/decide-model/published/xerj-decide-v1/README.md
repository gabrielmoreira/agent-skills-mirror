# xerj-decide-v1 — published artifact record (weights not committed)

The trained tier-2 decide head for `xerj --decide-mode local`. The weights
blob (`model.safetensors`, 29,683,844 bytes / 7,419,907 F32 parameters) is
over this repository's 5 MB commit ceiling for artifacts, so this directory
commits everything small and digest-pinned instead; `MANIFEST.sha256` is the
`sha256sum -c`-shaped integrity record for the whole artifact.

## Where the weights land

The intended home is the `xerj-org/xerj-decide-v1` model repository on a
public model hub (Apache-2.0). **Publication is pending operator
credentials; no URL exists yet and none is claimed here.** Until then the
artifact is rebuilt locally, bit for bit, by the recipe in
[`benchmarks/decide-model/README.md`](../../README.md) — the harness is
deterministic given the pinned tokenizer, and `export` re-verifies its own
output by reloading it through the loader's mmaped-safetensors path.

## Files here

| file | role |
|---|---|
| `MANIFEST.sha256` | sha256 of every artifact file (weights included) + training provenance and licences |
| `VERSION.json` | name / version / architecture / parameter count |
| `config.json` | the loader-parseable ModernBERT classifier config |
| `tokenizer.json` | the frozen 8,742-token wordpiece tokenizer (identical to `pinned/tokenizer.json`) |

To assemble a servable directory once the weights are available:

```sh
cp config.json tokenizer.json .
# fetch model.safetensors (from the published repo, or rebuild via the harness)
sha256sum -c MANIFEST.sha256
xerj --decide-mode local --decide-model-dir .
```

The full upload bundle (weights, Apache-2.0 licence, model card) is built by
`benchmarks/decide-model/scripts/publish_bundle.sh`, which also prints the
exact upload commands. Measured accuracy, calibration and latency live in
[`docs/DECIDE_MODEL.md`](../../../docs/DECIDE_MODEL.md).
