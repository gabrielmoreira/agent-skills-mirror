# Iris Development

Iris is Redis's umbrella for AI-focused products. This skill houses development guidelines for products under the Iris umbrella, organized into per-product sections — currently covering Redis Agent Memory (RAM). Optimized for agents and LLMs.


## Structure

- `rules/` - Individual rule files (one per rule)
  - `_sections.md` - Section metadata (titles, impacts, descriptions)
  - `_template.md` - Template for creating new rules
  - `_contributing.md` - Contribution guidelines (excluded from build)
  - `prefix-description.md` - Individual rule files
- `metadata.json` - Document metadata (version, organization, abstract)
- `AGENTS.md` - Compiled output (generated)
- `SKILL.md` - Skill definition and entry point
- `README.md` - This file


## Getting Started

1. Install dependencies from the repo root:
   ```bash
   npm install
   ```

2. Validate rule files:
   ```bash
   npm run validate
   ```

3. Build AGENTS.md from rules:
   ```bash
   npm run build
   ```


## Creating a New Rule

1. Copy `rules/_template.md` to `rules/prefix-description.md`
2. Choose the appropriate area prefix (see `rules/_sections.md`)
3. Fill in the frontmatter and content
4. Ensure you have clear examples with explanations
5. Run `npm run build` (in the build package) to regenerate AGENTS.md


## File Naming Convention

- Files starting with `_` are special (excluded from build)
- Rule files: `prefix-description.md` (e.g., `setup-install.md`)
- Section is automatically inferred from filename prefix
- Rules are sorted alphabetically by title within each section


## Impact Levels

- `HIGH` - Significant performance improvements or critical security practices
- `MEDIUM` - Moderate performance improvements or recommended patterns
- `LOW` - Incremental improvements


## Scripts

(Run these from the repo root)

- `npm run build` - Compile rules into AGENTS.md
- `npm run validate` - Validate all rule files


## Contributing

When adding or modifying rules:

1. Use the correct filename prefix for your section
2. Follow the `_template.md` structure
3. Include clear bad/good examples with explanations
4. Add appropriate tags
5. Run `npm run build` to regenerate AGENTS.md
