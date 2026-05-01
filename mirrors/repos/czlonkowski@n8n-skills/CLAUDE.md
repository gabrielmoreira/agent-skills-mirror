# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **n8n-skills** repository - a collection of Claude Code skills designed to teach AI assistants how to build flawless n8n workflows using the n8n-mcp MCP server.

**Repository**: https://github.com/czlonkowski/n8n-skills

**Purpose**: 7 complementary skills that provide expert guidance on using n8n-mcp MCP tools effectively for building n8n workflows.

**Architecture**:
- **n8n-mcp MCP Server**: Provides data access (800+ nodes, validation, templates, workflow management)
- **Claude Skills**: Provides expert guidance on HOW to use MCP tools
- **Together**: Expert workflow builder with progressive disclosure

## Repository Structure

```
n8n-skills/
├── README.md              # Project overview with video
├── LICENSE                # MIT License
├── skills/                # Individual skill implementations
│   ├── n8n-expression-syntax/
│   ├── n8n-mcp-tools-expert/
│   ├── n8n-workflow-patterns/
│   ├── n8n-validation-expert/
│   ├── n8n-node-configuration/
│   ├── n8n-code-javascript/
│   └── n8n-code-python/
├── evaluations/           # Test scenarios for each skill
├── docs/                  # Documentation
├── dist/                  # Distribution packages
└── .claude-plugin/        # Claude Code plugin configuration
```

## The 7 Skills

### 1. n8n Expression Syntax
- Teaches correct n8n expression syntax ({{}} patterns)
- Covers common mistakes and fixes
- Critical gotcha: Webhook data under `$json.body`

### 2. n8n MCP Tools Expert (HIGHEST PRIORITY)
- Teaches how to use n8n-mcp MCP tools effectively
- Covers unified tools: `get_node`, `validate_node`, `search_nodes`
- Workflow management with `n8n_update_partial_workflow`
- New: `n8n_deploy_template`, `n8n_workflow_versions`, `activateWorkflow`

### 3. n8n Workflow Patterns
- Teaches proven workflow architectural patterns
- 5 patterns: webhook, HTTP API, database, AI, scheduled

### 4. n8n Validation Expert
- Interprets validation errors and guides fixing
- Handles false positives and validation loops
- Auto-fix with `n8n_autofix_workflow`

### 5. n8n Node Configuration
- Operation-aware node configuration guidance
- Property dependencies and common patterns

### 6. n8n Code JavaScript
- Write JavaScript in n8n Code nodes
- Data access patterns, `$helpers`, DateTime

### 7. n8n Code Python
- Write Python in n8n Code nodes
- Limitations awareness (no external libraries)

## Key MCP Tools

The n8n-mcp server provides these unified tools:

### Node Discovery
- `search_nodes` - Find nodes by keyword
- `get_node` - Unified node info with detail levels (minimal, standard, full) and modes (info, docs, search_properties, versions)

### Validation
- `validate_node` - Unified validation with modes (minimal, full) and profiles (runtime, ai-friendly, strict)
- `validate_workflow` - Complete workflow validation

### Workflow Management
- `n8n_create_workflow` - Create new workflows
- `n8n_update_partial_workflow` - Incremental updates (19 operation types including `patchNodeField`, `activateWorkflow`, `transferWorkflow`)
- `n8n_validate_workflow` - Validate by ID
- `n8n_autofix_workflow` - Auto-fix common issues
- `n8n_deploy_template` - Deploy template to n8n instance
- `n8n_workflow_versions` - Version history and rollback
- `n8n_test_workflow` - Test execution
- `n8n_executions` - Manage executions

### Data Tables
- `n8n_manage_datatable` - Manage data tables and rows (CRUD, filtering, dry-run)

### Credential Management
- `n8n_manage_credentials` - Full credential CRUD (list, get, create, update, delete) + schema discovery (`getSchema`)

### Security & Audit
- `n8n_audit_instance` - Security audit combining n8n built-in audit (5 risk categories) + custom deep scan (hardcoded secrets, unauthenticated webhooks, error handling, data retention)

### Templates
- `search_templates` - Multiple modes (keyword, by_nodes, by_task, by_metadata)
- `get_template` - Get template details

### Other Workflow Tools
- `n8n_list_workflows` - List workflows with filtering/pagination
- `n8n_get_workflow` - Get workflow details (full, structure, minimal modes)
- `n8n_delete_workflow` - Permanently delete workflows
- `n8n_update_full_workflow` - Full workflow replacement

### Guides
- `tools_documentation` - Meta-documentation for all tools
- `ai_agents_guide` - AI agent workflow guidance

## Important Patterns

### Most Common Tool Usage Pattern
```
search_nodes → get_node (18s avg between steps)
```

### Most Common Validation Pattern
```
n8n_update_partial_workflow → n8n_validate_workflow (7,841 occurrences)
Avg 23s thinking, 58s fixing
```

### Most Used Tool
```
n8n_update_partial_workflow (38,287 uses, 99.0% success)
Avg 56 seconds between edits
```

## Working with This Repository

### When Adding New Skills
1. Create skill directory under `skills/`
2. Write SKILL.md with frontmatter
3. Add reference files as needed
4. Create 3+ evaluations in `evaluations/`
5. Test thoroughly before committing

### Skill Activation
Skills activate automatically when queries match their description triggers:
- "How do I write n8n expressions?" → n8n Expression Syntax
- "Find me a Slack node" → n8n MCP Tools Expert
- "Build a webhook workflow" → n8n Workflow Patterns

### Cross-Skill Integration
Skills are designed to work together:
- Use n8n Workflow Patterns to identify structure
- Use n8n MCP Tools Expert to find nodes
- Use n8n Node Configuration for setup
- Use n8n Expression Syntax for data mapping
- Use n8n Code JavaScript/Python for custom logic
- Use n8n Validation Expert to validate

## Requirements

- n8n-mcp MCP server installed and configured
- Claude Code, Claude.ai, or Claude API access
- Understanding of n8n workflow concepts

## Distribution

Available as:
1. **GitHub Repository**: Full source code and documentation
2. **Claude Code Plugin**: `npm install @anthropic/claude-code-plugin-n8n-skills`
3. **Individual Skill Uploads**: For Claude.ai users

## Credits

Conceived by Romuald Członkowski - [www.aiadvisors.pl/en](https://www.aiadvisors.pl/en)

Part of the n8n-mcp project.

## License

MIT License - See LICENSE file for details.
