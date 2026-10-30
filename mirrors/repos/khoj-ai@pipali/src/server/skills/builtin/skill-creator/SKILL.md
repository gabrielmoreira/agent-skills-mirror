---
name: skill-creator
description: Guide to create effective skills. Use when users want to create a new skill (or update an existing skill) that extends your capabilities with specialized knowledge, workflows, or tool integrations.
---

# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend your capabilities by providing specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific domains or tasks.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else: system prompt, conversation history, other skills' metadata, and the user request.

**Default assumption: you are already very smart.** Only add context you don't already have. Challenge each piece of information: "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields read to determine when the skill gets used, so be clear and comprehensive in describing what the skill does and when it should be used.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers.

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Benefits**: Token efficient, deterministic, may be executed without loading into context

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context.

- **When to include**: For documentation that you should reference while working
- **Examples**: Database schemas, API documentation, domain knowledge, company policies
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: Templates, images, icons, boilerplate code, fonts

#### What NOT to Include

A skill should only contain essential files. Do NOT create:
- README.md, INSTALLATION_GUIDE.md, CHANGELOG.md, etc.
- User-facing documentation
- Setup and testing procedures

### Progressive Disclosure

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed (unlimited)

Keep SKILL.md body under 500 lines. Split content into separate files when approaching this limit.

**Key principle:** When a skill supports multiple variations, keep only the core workflow in SKILL.md. Move variant-specific details into separate reference files.

## Skill Creation Process

1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, assets)
3. Initialize the skill (run init_skill.py)
4. Edit the skill (implement resources and write SKILL.md)
5. Iterate based on real usage

### Step 1: Understanding the Skill

To create an effective skill, understand concrete examples of how it will be used. Ask questions like:

- "What functionality should this skill support?"
- "Can you give examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"

You may ask the user if you can't infer the required information yourself.

### Step 2: Planning Reusable Contents

Analyze each example by:
1. Considering how to execute the example from scratch
2. Identifying what scripts, references, and assets would help when executing repeatedly

### Step 3: Initializing the Skill

When creating a new skill, run the `init_skill.py` script:

```bash
scripts/init_skill.py <skill-name>
```

The script creates the skill directory in `~/.pipali/skills/` with:
- SKILL.md template with proper frontmatter
- Example resource directories: `scripts/`, `references/`, and `assets/`

### Step 4: Edit the Skill

When editing the skill, remember it's being created for another instance of you to use. Include information that would be beneficial and non-obvious.

#### Learn Proven Design Patterns

Consult these guides based on your skill's needs:
- **Multi-step processes**: See references/workflows.md
- **Specific output formats**: See references/output-patterns.md

#### Start with Reusable Contents

Begin with the reusable resources identified in Step 2. Test any added scripts by running them.

#### Update SKILL.md

**Writing Guidelines:** Always use imperative/infinitive form.

##### Frontmatter

Write the YAML frontmatter with `name` and `description`:

- `name`: The skill name (hyphen-case)
- `description`: The primary triggering mechanism. Include both what the skill does and specific triggers/contexts for when to use it.

##### Body

Write instructions for using the skill and its bundled resources.

### Step 5: Iterate

After using the skill on real tasks:
1. Notice struggles or inefficiencies
2. Identify how SKILL.md or bundled resources should be updated
3. Implement changes and test again
