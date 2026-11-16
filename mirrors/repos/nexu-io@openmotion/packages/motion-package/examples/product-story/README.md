# Product Story

A portable recipe for a short promise → evidence → action story. Start with [MOTION.md](MOTION.md), which references the independent [DESIGN.md](DESIGN.md). An optional [SKILL.md](SKILL.md) gives an Agent the usage procedure. The [manifest](motion-package.json) declares every shipped file and its hash.

**Status: recipe.** The package includes an original emphasis element, material requirements, an input schema, two fictional presets and a deterministic shot-plan helper. It does not include an animated project, a rendered video or human visual acceptance.

From this directory, using Node.js (checked with 26.11.1):

```sh
node scripts/plan.mjs presets/product.json
node scripts/plan.mjs presets/lesson.json
```

Both commands print a JSON plan without writing files or downloading anything. The product preset introduces a fictional planning tool. The lesson preset keeps the same scene rhythm while substituting a different topic. Neither supplies the real evidence image or makes a claim about a real product or learning outcome. Constraints live in [inputs.schema.json](inputs.schema.json); the helper checks required fields, unknown fields and text lengths, with whitespace-only text also rejected.

Example Agent request:

> Use this package's MOTION.md and linked DESIGN.md for a short introduction to my product. Preserve the reveal, evidence and settled ending. Use my approved headline and screenshot, identify missing materials, and deliver an editable project in my chosen engine. Follow the review criteria before claiming completion.

To make an industry package, copy the complete folder, change the manifest name/version and matching root Skill name, replace the identity and material requirements, and document motion overrides. Preserve required notices. Keep the directory name equal to the root Skill name for Skill-host installation. Update the explicit inventory and hashes with the Motion Package authoring toolkit before sharing. Installation into a Skill host is a separate operation; this folder is not automatically discovered by Studio.

All original documents, sample text, scripts and the SVG use the bundled [Apache-2.0 license](LICENSE). Real brand materials retain their owner's permissions. [Material requirements](materials/requirements.md) explain the generic-font and missing-evidence limits.

## Acknowledgements

The independent design document follows the upstream [DESIGN.md alpha format](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md); the optional task entry follows [Agent Skills](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx). The sample contains original fictional content, with no upstream logos, videos or design samples copied.
