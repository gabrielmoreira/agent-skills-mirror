# Image review

- Codex branch mode: **added, single-frame PNG, JPEG and WebP** files supported.
- Install Pillow in helper's Python environment (`python -m pip install Pillow`).
  Use vision-capable Codex model + CLI supporting `codex exec --image`.
- No new bypass flag required. Full decoding rejects corrupt/animated files.
- Images: ≤16,777,216 pixels; no dimension >16,384 pixels.
  Decoder bomb warnings fail closed before pixel loading.
- Added image paths: encoded bytes ≤20 MiB each, ≤100 MiB total; check Git object
  sizes before capture. Exceeding any limit fails entire review.

- Capture exact bytes from pinned HEAD; stage only those images in isolated
  workspace; attach through Codex native image input.
- Every pass: path, media type, byte count, SHA-256 manifest + image attachments
  + text diff. Image findings: original path, line 1.
- Text-only review: no Pillow required.

- Binary deletions, including images: deletion metadata in every mode; no image
  attachments or Pillow.
- Other binaries, modified images, local/commit image additions/modifications,
  image review with other engines: unsupported; fail closed.
- Missing Pillow or provider image limits: fail review; never silently drop assets.
- Sensitive-path, source-mutation, authentication, sandbox controls stay enabled.

- Partial clones: materialize required Git objects **before** review.
- Isolated Git reader intentionally disables lazy network fetching; never weaken boundary.
