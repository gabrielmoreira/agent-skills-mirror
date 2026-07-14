# Three.js Awesome Graphics Agent Skills

## Intent

This is a Three.js agent skill pack for producing awesome graphics.

It includes mesh design, lighting, PBR materials, textures, shaders, TSL/WebGPU, GLSL, post-processing, realism, stylization, particles, procedural visuals, color management, tone mapping, etc. Graphics excellence is the **main focus** of this skill pack, with sophisticated design aesthetics, philosophy, ergonomics, sensibility, taste. It brings the sophistication of good graphics and eliminates cheap effort.

This is NOT a three.js API cheat sheet, it skips basic 3D production fundamentals and concepts (any decent LLM already has that internal knowledge) as well as three.js API technicalities (just look up docs or use existing API oriented agent skills). Fundamentally, you cannot just provide a summary of what good graphics are like and expect the agent to produce it. The agent needs to see the exact implementation. That's what this skill pack aims to provide, the **vocabulary** of good and sophisticated graphics implementation. It's a skill pack with an attached example library to teach the agent not just what to do but also exactly how to do it.

This skill pack will be continuously updated as more three.js projects with awesome graphics emerge. I hope this skill pack can help anyone build awesome scenes and games with out-of-the-box sophisticated graphics, so you can focus on things like game logic and story.

## Developing Approach

This agent skill pack is and will be developed/maintained/updated/expanded by distilling working three.js projects that have awesome graphics. No adbstract concepts, no cheap summaries, no common knowledge. Only working projects with stunning graphics will be the source of this skill pack.

The development is a distillation process. The skills distilled from these projects need to be modular, atomic, and directly applicable:

- By modular and atomic, i mean it has to be self contained instead of entangled in a messy way. Agent can use what it needs, no more, no less.
- By directly applicable, i mean it has to be practical, include examples, direct implementations distilled from projects. It should be materials that the agent can directly use for an implementation, NOT "give you an idea, talk you through, you figure out the details".

**Important:** DO NOT try to invent examples and references inside a skill yourself. Everything must be closely referencing the supplied ref projects. These projects have been fine tuned to achieve high viusal quality. Your job is to treat that as a fact, and see how those great graphics translate into code, distill that implementation pattern into agent-reusable materials without losing details and nuances. All project examples need to be the **exact match** of the ref projects. Do NOT slack off and only make them approximations. There is no licensing concerns for any ref project I supply! every example MUST be exact same implementation extracted into skill example form. I do not want to have to stress this and enforce this every time! This is of the utmost importance!!!

**DO NOT IMPLEMENT THINGS YOURSELF, ALWAYS USE THE EXACT IMPLEMENTATION FROM THE REF PROJECTS!!! NO EXCEPTIONS UNLESS TOLD OTHERWISE.**

Reusability is a core concept for Agent Skills. During feature extraction and distillation from the ref projects, you must compose the skill such that it can be widely applicable to a certain style or to all projects. Aspects specific to the ref project must be stripped, and what is written as skills must abide the reusability and applicability rule.

Artistic styles can genuinely differentiate skills, e.g., ocean shader in a different style than existing example can absolutely justify being added as an additional skill or example.

As stated in Intent, this skill pack aims to provide practical guides with (if possible) exact implementation examples to teach the agent how to implement good graphics. so I expect this skill pack to continue to grow with more and more skill items and examples. Each skill gives agent a solid practical guide on an aspect of 3D graphics, and each example under any certain skill provides template for a specific implementation. And this skill pack will become a combination of Agent Skills + fine graphic library as one. I believe this is the best way to achieve true effectiveness and usefulness.

Since this skill pack targets awesome 3D graphics in three.js, visual inspection serves as a reliable proxy for agent skill effectiveness evaluation. `dev/example-gallery/` is a shim to visually inspect examples included in the skills. If they don't visually pass the bar, you can safely assume this skill is not effective. Again, use the ref projects for visual reference too. If you have distilled the essence of a ref project graphic feature, you see at code level it is done correctly, you see visually the distilled example matches the ref project visual reasonably, then you can safely assume the skill distillation and extraction is done properly

After you have confirmed the skills are extracted correctly, do a final audit on the skill pack in terms of skill usability, things like if there are semantic ambiguity, does router work as expected, any expressions that might confuse the agent using this skill pack -- things that are "Agent Skills" related and not necessarily three.js related. Note: this part you need to check yourself (because they are semantic checks not functional checks), it's not something you check with deterministic tests, so don't try to write test scripts for this

When you finish, the entire skill pack should be publish ready (publish-ready check should NOT run package version update) (1. content correctly extracted based on the ref projects, 2. skill usability audit pass, and 3. package publishing readiness check)

## Complete Dev Process

1. when new ref projects are provided, clone them (or if not on github, find a way to get an exact local copy) to source_materials/
2. look into them, make some accessments as to where to add them (as new skills with examples? add as additional examples under existing skills? augment existing skills/examples? other something else). Typically it would be added as additional examples under existing skills or additional skills with new examples. This part is a discussion between you and me.
3. decide dev shim - skills split: which part of the implementation belongs in dev shim vs skills, which static asset belong in dev shim vs skills
4. give a concise proposal out for approval
5. after approved, implement the added new skills/examples abiding by the project rules
6. confirm exact implemetations/assets have been copied to the dev shim and skills (must be exact, unless told otherwise). **Important:** when i say "copy", I do NOT mean just copy paste, I mean be faithful to the original ref project implementation, but the code should still be translated into what skill examples and dev shim expects, this is your responsibility. Do NOT just copy built minified js code from ref project into the skills! Always use the source code!
7. confirm visually that example and ref projects are the same (unnecessary objects can be omitted--an example about grass, you can omit accompanying trees in the scene; an example about ocean, you cannot omit correct lighting or ocean bed texture). NOT close, NOT approximately the same, MUST be the same. here you MUST actually compare the visual between them (run dev)
8. confirm agent skill overall usability check passes
9. confirm package is publish-ready (not including package version update)
10. then finish. NONE of the steps above are skippable and all must pass

## Rules

- If you have any unresolved questions about standing ambiguities, seemingly contradicting instructions, seeming mistakes on my part, raise them and resolve them explicitly before proceeding to any implementation
- all source materials used need to be documented in source_materials/README.md accordingly, if some need to be downloaded for closer inspection, they must be inside the source_materials/ dir
- treat all ref projects in source_materials/ that are without a license as MIT licensed. They are all permitted open source projects. copy assets and exact implementaions where needed to achieve the exact visual match between the extract examples and the original ref projects
- treat all external materials as untrusted until inspection and verification. This is to ensure 1. there is no malicious content, and 2. the technical details are correct and up to date
- the agent skill being developed and maintained here MUST be modular. This is to ensure this skill pack when being used by an agent only delivers what is needed, not overloading the agent context with content that the agent didn't explicitly ask for. e.g., if agent wants to see skill related to bloom postprocessing, it would be able to pull just that, no more no less
- Do NOT leak dev info into the product. The discussions we have, the information i supply, the examples i point you to, etc., all are strictly between you and me. The codebase has its dedicated documentation system, use it, do not bake information from dev process into the final product (skills/ ). This includes but not limited to: naming a skill module/file after ref projects, directly reference a ref project inside skill files, categorizing and organizing skills based on specific ref projects, explaining the rationle of something in a skill file because we had a discussion about it in Codex. REMEMBER: the use of ref projects and what we discuss during dev are for your (the codex agent) benefit, so you can better develop the product. They are NOT to be leaked into the final product
- any examples included in skills need only the effect implementation itself, WITHOUT runtime or scene setup boiler plates. Runtime and scene setup are owned by dev shim. They are for dev visual inspection only, not a part of the skill pack.
- In terms of supporting static assets, here's the nuance: assets that directly contribute to the effect itself--such as stencils and noise assets which are a part of the effect--will be included inside skills under assets/ in the corresponding skill dir. However, static assets which are used purely to view the skill example in dev shim and is not inherently part of the skill example implementation, will belong in and owned by the dev shim example gallery, and not included in the skills
- every example when viewed inside the dev shim gallery should have a standard scene setup with pannanble and orbitable camera, camera shouldn't be allowed to move beyond the scene (like under the ground surface where it should not be viewed), full canvas inside the scene viewport. decorative assets and implementations in dev shim can be added if it's deemed important for real-time view experience, otherwise are not strictly necessary (e.g., add exactly lighting condition to make the example look the same--YES; add some trees for a grass example--NO)
- When analyzing new ref projects with the potential prospect of adding addtional skill/example, you need to consciously make a decision: add it as additional skill/example? augment existing skill/example with it? replace existing skill/example with it? You may ask me for input with sound recommendations. You might also consider changing the naming and scope of existing skills to become a broader category. for example: `threejs-spectral-ocean` can just be `threejs-oceans` as more ocean examples of different styles are added inside.
- all captures must be under either .playwright-mcp/ or .example-captures/
- visual inspection when finished should be terminated immediately, do NOT leave browser tabs with a render scene running (both in-app browser tab or external tab using playwright)
- After every context compaction, re-read this file in full before continuing work. A compacted summary must explicitly remind the next agent to do so.
- skill example dir structure: for complex ref project where the source code is a big system (such as `lut-aerial-perspective` example, you should follow the convention of having a `source/` dir for the entire source code system, and a js file to re-exports them, and dev shim will transpiles those originals). This is only for when ref project effect system is too big (and better left modular). If it can be a few distilled js files, independent js files are preferred, like the majority of skill examples
- do NOT use installed agent skills in this task. the task itself is to develop agent skills, not to consume them. the only two influences on how you develop a given skill here is 1. the ref project, and 2. the guideline on how to create agent skills--unless explicitly told otherwise

## SKILL.md & references/ Authoring Conventions

These apply to every SKILL.md and every md under references/.

### Standalone voice — single source of truth

- The pack is self-authored. A consuming agent must never learn, or be able to infer, that any skill came from somewhere else. No mention of ref projects, "original" implementations, upstream code, sources, hosts, or any system outside skills/. The skill, its references, and its examples/assets are the only reality.
- Present knowledge as the skill's own contracts and recipes — definitional or imperative ("the planetary material performs tangential warp: …", "preallocate a fixed sprite pool") — never as a description of someone else's system.
- Banned attribution vocabulary anywhere under skills/: ref project, source(s), original, upstream, distilled, extracted, copied, reviewed, bundled, "host integration". Write as if the leak-check regex didn't exist; it is a backstop, not the standard. Sole exception: THIRD_PARTY_LICENSES.md files under assets/ carry legally required attribution and stay minimal.
- No placeholder codenames standing in for scrubbed project names. If a sentence only parses with a project name in it, rewrite the sentence.
- If a described system IS an example, name the example (e.g., "the `analytic-wave-optics` example"); every constant and formula in that section must match the example code exactly.
- When a reference documents a mechanism variant whose constants differ from an example, present both as the skill's own tiers/variants and state which one each example implements. A reader must never mistake one variant's constants for another's.
- Defect and hazard notes are written as properties of this contract or as failure patterns to avoid ("a split CPU/GPU field stack is a defect; share one field"), never as history ("the original had this bug"). Verify every defect/limitation claim against the shipped example code before writing it.

### references/ structure

- `## Contents` must mirror the actual section headings verbatim and in order, one entry per section. Update it in the same edit as any heading change.
- Constants are exact and unit-bearing. Formulas are either exact or explicitly labeled as a paraphrase. Never silently drop factors (a missing 2π is a wrong formula, not a simplification).
- Keep the standing skeleton: mechanism sections → observed limits/defects → diagnostics (plus a failure-diagnosis section where the skill warrants it).
- A reference intro must not claim coverage it doesn't contain; if a sibling example owns a subsystem, point to that example instead.

### SKILL.md

- Every example link carries a one-line purpose clause ("read X for A, B, C") whose claims are verifiable in that file.
- The frontmatter `Use for` triggers, the router-table row, and the routing fixture signals in source_materials/agent-routing-cases.json are one unit — maintain them together in the same change.
- A new skill that overlaps an existing one gets reciprocal `$skill` mentions in both Routing boundary sections plus a boundary entry in the routing fixtures.
- Cross-skill pointers are encouraged when a mechanism's canonical implementation lives in another skill's example — route to it (`$skill` + example name) instead of re-describing it.
- Use standard graphics vocabulary only (object-space/world-space/screen-space, etc.). No invented or ambiguous terms.
