# Motion Package specification

**Version: 0.2 — draft.** A Motion Package is a portable folder that gives an Agent the visual identity, motion language, materials and method needed to adapt a creative system to another brief. This specification adds a distribution contract to the [v0.1 Motion.md authoring proposal](motion-md.md); it does not replace native project formats.

The key words MUST, SHOULD and MAY describe package conformance. A conforming package does not imply that its creative claims, upstream format declarations or rendered effects have been independently verified.

## 1. Layers and compatibility

| Artifact | Owns | Consumer |
| --- | --- | --- |
| `DESIGN.md` | Visual identity, design tokens and their rationale. | Design and coding Agents can read this file independently. |
| `MOTION.md` | Design reference, brand facts, narrative, motion, timing, sound, invariants and review criteria. | A motion-capable Agent reads the selected creative context. |
| `SKILL.md` (optional) | Task selection and the procedure for using the package. | A compatible Skill host, after normal discovery/activation. |
| `motion-package.json` | Identity, versions, entry paths, dependencies and an explicit hashed file inventory. | Packaging/checking tools and discovery clients. |
| Source, elements, materials, presets and scripts | Implementation and task-specific inputs. | The declared runtime or an Agent choosing the relevant resources. |
| Previews and evidence | What was actually produced and reviewed. | Creators and reviewers. |

`MOTION.md` assembles the full creative context through references. It does not copy DESIGN.md's token tree into a competing palette. The Brand Kit section still owns product facts, approved claims, voice and asset permissions; its visual identity comes from the Design section's reference. An existing `BRANDKIT.md` can remain linked material.

Compatibility means **document composition**: the referenced DESIGN.md retains its own format, token semantics, unknown sections and tooling. It does not mean Motion Package tools implement the upstream parser, CSS export, contrast checks or token merging. Likewise, an optional Skill retains the independent Agent Skills format. Package metadata is not inserted into either upstream document's frontmatter.

The local [authoring toolkit](../packages/motion-package/README.md) implements manifest/inventory checking, hash refresh and portable-folder assembly. There is no Studio importer, automatic Skill installation, marketplace, dependency installer, Markdown-to-animation compiler or cross-engine rendering guarantee.

## 2. Minimum package and file names

```text
product-story/
├── motion-package.json
├── MOTION.md
├── DESIGN.md
├── LICENSE
├── SKILL.md                     optional task procedure
├── inputs.schema.json           optional replacement contract
├── elements/                    reusable implementation fragments
├── materials/                   supplied material and acquisition requirements
├── presets/                     example briefs or content variants
├── scripts/                     opt-in helpers with documented dependencies
├── references/                  focused guidance or pinned parent documents
├── previews/                    actual results, when available
└── evidence/                    scoped verification, when available
```

Only the manifest, motion document, design document and license file are mandatory. Use folders that carry actual content; empty placeholders are unnecessary. A package MAY contain knowledge alone. It MUST NOT describe a recipe as a tested editable project or invent a preview to imply rendering acceptance.

New packages SHOULD use `MOTION.md` and `DESIGN.md`. The manifest is authoritative for exact, case-sensitive paths: `motion.md`, `design.md` and existing `MOTION_DESIGN.md` are valid when explicitly declared. Consumers MUST NOT silently choose between similarly named files. Legacy single documents remain readable as v0.1 context without a manifest. They become v0.2 packages only after the required files and declarations are added; no bulk renaming is required.

## 3. The Design reference

The motion document MUST have a Design section that links its declared design entry using an ordinary relative Markdown link:

```markdown
## Design

Design source: [DESIGN.md](DESIGN.md).
Use its colors, typography, spacing and component roles as the visual authority.
Keep its token references intact, for example {colors.primary}.
Video adaptation: use typography.h1 for the opening phrase; preserve its family
and weight, and describe any frame-size scaling here.
```

No special `@include` preprocessor is required. An Agent follows the link when the selected task needs that context, as it would follow a reference in a repository instruction document. This is not a claim that AGENTS.md defines a universal import syntax.

Rules:

1. Manifest paths resolve from the package root; Markdown links resolve from the containing document. Both MUST reach the same design file. For `references/MOTION.md`, a root design link is `../DESIGN.md`.
2. A portable package MUST contain the design document and every local resource required to use the declared entry. Remote URLs are provenance or optional reference links, not implicit downloads. Vendor permitted content for an offline handoff; otherwise declare the missing material as a user input and the package's limitation.
3. `design.format: "design-md"` declares the upstream format, and requires `design.specVersion` (currently `alpha` upstream). The document can retain frontmatter, interleaved YAML blocks or both. Upstream token references and duplicate-key rules remain upstream responsibilities.
4. `design.format: "markdown"` accepts a prose design guide, including older community documents. Do not label it upstream-schema-conformant without validating it. Readers still preserve and use its prose.
5. The design document owns visual values. MOTION.md owns temporal behavior and explicitly named video adaptations. A token-name reference is not permission to reinterpret or silently redefine the token. Record conflicting requirements and resolve them for the affected task before production.
6. Application chrome remains governed by its own design system. A creative package affects the authored work, not the editor's themes or controls.

A package has one effective design entry. To compose several brand sources, write one design document that names the selected roles and links the permitted sources; there is no implicit last-file-wins merge. Circular reference chains are authoring errors. An Agent tracks visited paths, stops a cycle, and reports the unresolved dependency rather than guessing.

## 4. Motion document contract

The creative body remains Markdown, not a serialized timeline. It MUST identify the package/version and cover these responsibilities; headings other than Design may fit the author's domain:

| Responsibility | Required decisions |
| --- | --- |
| Purpose and provenance | Audience, intended result, authorship/reference and observed versus proposed behavior. |
| Design | Direct design link, token roles and named video adaptations. |
| Brand and material | Approved facts, voice, required footage/images/fonts/audio, rights and missing-input behavior. |
| Story | Hook, reveal order, evidence and ending; scene purpose, not only timestamps. |
| Motion and sound | Units, shot boundaries, reading holds, easing, camera, transitions, audio anchors and silence policy. |
| Invariants and inputs | What survives a remix, what can change, limits, overflow and duration/aspect-ratio adaptation. |
| Review | Actual playback, visual/audio checks, source/output identities and remaining gaps. |

Frame-based timing MUST declare frame rate; seconds MUST be labeled. Preserve source/output clock mapping for edited footage. Brand identity, timing and source code are separate authorities: an implementation that diverges from the written rules requires reconciliation, not an automatic claim that the prose was executed.

## 5. Manifest

The machine-readable contract is [schema.json](../packages/motion-package/schema.json), using JSON Schema 2020-12. `specVersion` versions this package contract; `version` versions the author's content. They are independent of DESIGN.md's version, dependency versions and the OpenMotion application version.

| Field | Requirement and meaning |
| --- | --- |
| `specVersion` | Required literal `"0.2"`. Unknown versions are rejected by the reference checker. |
| `name` | Required lowercase kebab-case identifier, at most 64 characters. |
| `version` | Required exact `MAJOR.MINOR.PATCH`, optionally with a prerelease suffix. No ranges, tags or build metadata in this profile. |
| `description` | Required nonempty summary, at most 1024 characters. |
| `license`, `licenseFile` | Required main license identifier/expression and bundled full terms. Asset-specific terms override the default. |
| `motion` | Required path to the creative document, with file role `motion`. |
| `design` | Required `{path, format, specVersion?}`; its path has file role `design`. |
| `skill` | Optional path ending in exact `SKILL.md`, with file role `skill`. |
| `inputs` | Optional replacement-schema path, with file role `inputs`; its schema dialect and validation command must be documented. |
| `extends` | Optional ordered paths to bundled parent motion documents, each with role `reference`. Explicit context, not executable inheritance. |
| `dependencies` | Optional exact-version requirements; see below. |
| `files` | Required inventory of every distributed file except this manifest. Each entry has `path`, `role`, `sha256`, optional `license` and provenance `source`. |
| `tags` | Optional discovery labels such as `education`, `retail`, `product-demo` or `title-reveal`. No registry implied. |
| `extensions` | Optional metadata with namespaced keys such as `org.example`. Unknown namespaces are preserved, not executed. |
| `$schema` | Optional editor hint. The checker never fetches it. |

See the [complete sample manifest](../packages/motion-package/examples/product-story/motion-package.json). The inventory roles distinguish source, assets, materials, scripts, presets, reference, preview, evidence and license files. A third-party file MUST carry its applicable license and bundled terms/notice; a provenance URL does not grant redistribution rights. Attribution and hashes MUST survive packing.

Paths are relative POSIX file paths without traversal, empty segments, URL/query/fragment syntax, whitespace, Windows reserved names or platform-invalid characters. File and directory names MUST be unique after Unicode NFC normalization and lowercase comparison. Symlinks and non-regular files are excluded. A path MUST NOT identify the manifest itself. The explicit inventory is the portable payload: unlisted workspace files, credentials, outputs and caches are not copied. Hashes identify file bytes, not authenticity or an author's permission to use them.

Each dependency declares `name`, `kind` (`tool`, `library` or `motion-package`), exact `version`, HTTPS `source`, and optional `path` to a bundled inventory entry. A `motion-package` dependency requires a local entry; its version identifies the reviewed parent. Source links SHOULD pin an immutable commit or version. Tool requirements describe the tested environment; they do not install or execute anything. Library requirements can point to a bundled entry or describe a separately installed runtime, with that limitation stated in MOTION.md. Required transitive materials and notices MUST also appear in the inventory; there is no transitive package resolver in this version.

The reference checker checks declared entries, roles, path portability, file types, hashes and dependency shape. It does not parse arbitrary Markdown links, lint DESIGN.md, validate SKILL.md frontmatter or input-schema semantics, inspect dependency internals, detect prose reference cycles, enforce licenses, scan secrets, sandbox scripts or judge creative quality. Authors and specialized tools perform those checks separately. `lock` refreshes declared hashes; it is not an acceptance operation.

## 6. Extending a package

Two supported authoring patterns keep reuse practical:

- **Fork:** copy a portable package, choose a new name/version, retain provenance and applicable licenses, replace its design/input material, and record what changed. This is sufficient for most industry packs.
- **Compose:** vendor a reviewed parent's required files under `references/` or `vendor/`, preserving relative links and terms. Record its exact version in `dependencies` and list its motion document in `extends`. Include the whole required local reference closure in `files`.

For composition, read parents in `extends` order, then the child MOTION.md. The child MUST list the inherited decisions and explicit overrides; conflicting parents require an explicit choice. The child's declared design entry is the effective identity. A parent's geometry or art that depends on its former tokens must be adapted deliberately. An extension MUST NOT silently relax locked content, asset permissions or evidence requirements. Agents follow only references needed for the task and report missing or circular references. Package files remain task context and never override the user's instructions or the host's permission rules.

For example, an education fork can preserve the reveal → evidence → recap rhythm while replacing product screenshots with a diagram, a worked example and a retrieval question. A retail fork can preserve the same rhythm with product material, a demonstrated feature and approved offer terms. Those are authoring patterns, not claims of completed industry videos. Custom domain metadata belongs under `extensions`; required new behavior needs a future spec version rather than an opaque extension field.

## 7. Optional Agent Skill

Use the existing Agent Skills contract: a skill directory contains `SKILL.md` with valid `name` and `description` frontmatter. A root Skill's name matches the package directory; a nested Skill's name matches its immediate directory. When distributing a nested Skill separately, bring its referenced materials into that standalone Skill's directory and revalidate the links.

Keep the entry short: when to use this package, which motion/design documents to read, expected inputs, scripts available, and how to review the result. Load supporting files on demand. Script commands MUST state dependencies and writes; reading or checking a package MUST NOT run its code. A host's installation/discovery procedure is separate from packaging. Without SKILL.md, an Agent can still use the manifest and creative documents directly.

## 8. Author, verify and share

1. Create the documents and real resources; declare the inventory and dependency versions.
2. Check DESIGN.md with the appropriate upstream tool when claiming its schema; validate a Skill with the Agent Skills reference tool when included. Verify local Markdown links and source attribution.
3. Refresh hashes with `lock`, run `check`, then `pack` into a new directory. Run checks on that relocated copy and any supplied helper there. Keep the package name as the directory name if using a root Skill.
4. For an executable package, adapt it to a second brief, render with the declared runtime, play the result with sound and record exact source/input/output identities. Human visual acceptance remains separate.
5. Share the folder as a repository, immutable Git release or ordinary ZIP, with a clear usage entry, license and status. Packaging does not publish it. A `.motion` extension, npm package or marketplace listing has separate contracts and authorization.

A useful public listing includes name/version, audience and industry, design entry, motion invariants, required inputs, runtime requirements, actual preview if available, provenance/license, known limits, and an example Agent prompt. Never present an upstream reference or static asset as a generated result. A recipe can be shared honestly before it has a video preview.

## 9. Migration and current implementation boundary

Existing `MOTION_DESIGN.md`, gallery `motion.md`, the Remix Skill profiles and their scripts remain unchanged. Wrap them in this manifest only when someone prepares a portable package; preserve their source and evidence. Existing reusable native templates still use `TEMPLATE.md` for handoff. The new manifest does not register templates, add MCP tools or change the five production routes.

The reference toolkit is a private local module in the standalone root npm repository. It has no workspace dependencies or independent npm publication. The [Product Story sample](../packages/motion-package/examples/product-story/README.md) is a recipe with a deterministic shot-plan helper, an illustrative element and two fictional input presets. It is not an animated project or a rendered benchmark.

## References and acknowledgements

Reviewed on 2026-11-15:

- [Google DESIGN.md specification](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md): the upstream `alpha` document/token boundary. This draft preserves that boundary rather than adopting its schema as a new Motion schema.
- [awesome-design-md](https://github.com/voltagent/awesome-design-md): community discovery and independently reusable design documents. Its README describes a different section convention; inclusion there is not proof of current Google schema validation or rights to use a brand's assets.
- [Agent Skills specification](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx): optional task instructions, metadata and supporting-resource conventions. No upstream source or brand assets are copied into the new sample.

These references can evolve independently. Record the exact upstream version/tool used for validation of a particular package; this review date is not a frozen upstream dependency.
