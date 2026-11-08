# Starlight Motion Designer MCP

## Product Thesis

Build a Motion Designer MCP that turns brand strategy, design tokens, screenshots, and product intent into implementable motion systems.

This should not be a generic animation toy. It should be an agentic production layer that helps teams ship tasteful motion in real apps, docs, demos, launch pages, and videos.

## Best Brand Owner

| Brand | Role |
| --- | --- |
| Starlight Intelligence Systems | Owns the protocol, MCP server, QA harness, governance, and enterprise credibility. |
| Arcanea | Owns premium creative examples, motion language, templates, lore/interface atmosphere, and studio-grade demos. |
| FrankX.ai | Owns public education, content, launch funnels, affiliate stacks, and creator-friendly packaging. |

Recommendation: ship the core as **Starlight Motion Designer MCP**, package the beautiful examples under **Arcanea Motion Systems**, and sell/teach it through **FrankX.ai**.

## Core Capabilities

1. **Motion brief generator**
   - Inputs: brand tokens, page purpose, audience, interaction type.
   - Output: motion principles, duration/easing tokens, choreography, reduced-motion behavior.

2. **Implementation planner**
   - Chooses Motion, GSAP, Rive, Lottie, Remotion, CSS, or Three.js.
   - Returns dependency plan and file-level implementation instructions.

3. **Code patch assistant**
   - Applies framework-specific implementation patches.
   - Supports Next.js, React, plain HTML/CSS/JS, and Remotion.

4. **Capture and review**
   - Runs browser capture.
   - Generates screenshots/video/GIF.
   - Scores against the motion rubric.

5. **Asset pipeline**
   - Generates style frames via image generation.
   - Imports Figma/Canva context when available.
   - Emits Lottie/Rive/Remotion recommendations.

6. **Motion system registry**
   - Stores reusable patterns: reveal, transition, hover, loader, scroll narrative, hero choreography, data visualization, onboarding.

## MCP Tools To Expose

| Tool | Purpose |
| --- | --- |
| `create_motion_brief` | Turn product/brand intent into a motion spec. |
| `select_motion_stack` | Recommend Motion/GSAP/Rive/Lottie/Remotion/Three based on constraints. |
| `generate_motion_tokens` | Emit durations, easings, stagger rules, reduced-motion defaults. |
| `plan_animation_patch` | Produce file-level implementation plan. |
| `capture_motion_preview` | Use browser capture to record animation. |
| `score_motion_quality` | Apply rubric and output fixes. |
| `export_gif_recipe` | Produce ffmpeg/Remotion export commands. |
| `register_motion_pattern` | Save reusable pattern metadata. |

## MVP Scope

Build the MCP as a local TypeScript server with:

- Motion brief generation.
- Stack selection.
- Motion token output.
- Rubric scoring.
- Export command generation.
- Optional Playwright capture wrapper.

Do not start with full visual editing. Start with motion intelligence, QA, and implementation planning.

## Maintenance

Expected maintenance: medium.

- Monthly dependency checks for Motion, GSAP, Remotion, Playwright, and MCP SDK.
- Quarterly refresh of library rankings.
- Security review for any tool that reads files, invokes shell commands, or connects to design platforms.
- Example gallery updates after each major brand/site launch.

## Legal / IP Risk

Main risks:

- Using proprietary example animations without permission.
- Bundling paid templates or restricted assets.
- Using GSAP or other libraries in a way that violates builder/platform terms.
- MCP prompt injection or excessive file access.
- Generated images resembling protected brands or characters.

Mitigation:

- Use CC0/MIT/owned examples in the repo.
- Keep third-party code as dependency references, not copied source.
- Add source/license metadata for every asset.
- Scope MCP tools narrowly and review command execution.

## Why Build It

This is strategically strong because motion is where AI-generated UI still looks flat. A motion-focused agent layer creates:

- Better web launches.
- Better social/demo content.
- Better product onboarding.
- A differentiated agent skill marketplace asset.
- A reusable enterprise-friendly design intelligence product.

