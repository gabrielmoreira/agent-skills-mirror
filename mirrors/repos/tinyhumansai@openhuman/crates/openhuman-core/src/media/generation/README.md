# generation

Image and video generation agent tools, backed by OpenRouter through the
OpenHuman backend's `/agent-integrations/openrouter` proxy. The work is
split across three layers, each with a different owner:

- **TinyInference** (`tinyinference-image` / `tinyinference-video`, reached
  through `tinyagents_harness`) owns the wire contract, the reference and
  output-shape standards, the submit-poll-download job loop for video, and
  the rule that a billed call always returns media or an error, never an
  empty success.
- **TinyAgents** (`tinyagents_harness::media`) owns the tools themselves:
  argument parsing, artifact persistence into the workspace, and result
  wording.
- **This module** owns the host policy: endpoint, credential, egress,
  privacy, and budget gates (`provider.rs`), plus the tool names,
  descriptions, and local-reference policy (`tools.rs`).

## Key files

| File | Role |
| --- | --- |
| `provider.rs` | `managed_generators`: builds `MediaGenerators { image, video }` against the managed backend, or returns `None` when no backend transport is installed. Wraps each generator in a `Guard` that enforces local-only privacy mode and the egress disclosure before a request leaves the device, and the managed-credit budget gate before a billed submit. |
| `tools.rs` | `build_media_tools`: registers `media_generate_image`, `media_generate_video`, and `media_list_models` as `Tool` implementations over the generators from `provider.rs`. Also defines `reference_policy`, which restricts local reference files (for image edits or video first/last frames) to the action directory or workspace directory. |
| `artifact_tool.rs` | `MediaArtifactTool`: wraps a generation tool so every file it saves is also tracked as an OpenHuman artifact, following the same `create_artifact` / `finalize_artifact` pattern the document and presentation tools use. Runs the inner tool unchanged, then files each reported output and stamps an `artifact_id` (or `artifact_error`) onto its entry. |
| `mod.rs` | Re-exports: `MediaArtifactTool`, `managed_generators`, `MediaGenerators`, `OPENROUTER_PROXY_PATH`, `build_media_tools`, `media_tools_from`, `MediaListModelsTool`, and the three tool-name constants. |

## Key types

- `MediaGenerators { image: Arc<dyn ImageGenerator>, video: Arc<dyn VideoGenerator> }`,
  the pair of generators for one process.
- `MediaArtifactTool<T: Tool>`, the artifact-tracking wrapper described above.
- `MediaListModelsTool`, a read-only tool that lists the image and video
  models the current generators can run, with an optional substring filter.

## How it fits

`build_media_tools` is called from wherever the tool registry assembles the
agent's tool list; it returns an empty list rather than erroring when no
backend transport is installed, so a library host with no TinyHumans
connection simply has no media tools rather than a broken one. Generated
files land under `<action_dir>/generated-media/`, and `MediaArtifactTool`
moves each one into the workspace's `artifacts/<id>/` layout so it shows up
as a card in the chat UI. Billing and margin stay backend-side: this module
never charges directly, it only refuses to submit when
`crate::integrations::client::budget_gate` reports the account's managed
credits are exhausted.

## Where to look next

See [`../README.md`](../README.md) for the media domain overview and how
this relates to [`../image`](../image/README.md).
