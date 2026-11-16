---
name: product-story
description: Adapt the Product Story recipe to a supplied product or lesson brief using its visual identity, three-scene rhythm and input limits. Use when the user selects this package or asks to adapt its recipe.
license: Apache-2.0
---

# Product Story

Read [MOTION.md](MOTION.md) and [DESIGN.md](DESIGN.md) for the chosen creative system. Read [material requirements](materials/requirements.md) and [input constraints](inputs.schema.json) when adapting content. Preserve user-specified changes and locked content; the supplied presets are fictional examples.

For a concrete starting plan, run from this package directory:

```sh
node scripts/plan.mjs presets/product.json
```

The optional helper uses Node.js built-ins and was checked with Node.js 26.11.1. It reads the preset and local sequence, validates input fields, and prints JSON to stdout. It performs no writes, downloads or rendering. Use `presets/lesson.json` to inspect a different subject with the same timing. Make task-specific presets in the user's working project, keeping the shared package intact unless the user requests a package edit.

If the user requests a video, implement the plan in their chosen editable engine with supplied materials. This package does not include an animated project. Apply the Motion document's design bindings, holds and review criteria, and use the host's normal preview/export workflow for the requested deliverable. Record actual verification; a plan or a successful script does not establish rendered or human visual acceptance.
