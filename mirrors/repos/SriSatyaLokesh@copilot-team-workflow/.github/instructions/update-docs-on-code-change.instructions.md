---
description: 'Automatically update README.md and documentation files when application code changes require documentation updates'
applyTo: '**/*.{md,js,mjs,cjs,ts,tsx,jsx,py,java,cs,go,rb,php,rs,cpp,c,h,hpp}'
---

# Update Documentation on Code Change

## Core Rule

**Update documentation in the same commit as the code change. Never separate them.**

## When to Update Docs

Automatically check if documentation updates are needed when:

- New features or functionality are added
- API endpoints, methods, or interfaces change
- Breaking changes are introduced
- Dependencies or requirements change
- Configuration options or environment variables are modified
- Installation or setup procedures change
- CLI commands or scripts are updated
- Code examples in documentation become outdated

## What to Update

### README.md — Update when:
- Adding new features → add to "Features" section with usage example
- Modifying installation/setup → update "Getting Started"
- Adding CLI commands → document syntax, options, examples
- Changing configuration → update config examples and env var table

### API Documentation (`docs/apis/`) — Update when:
- New endpoints added → document HTTP method, path, request/response
- Endpoint signatures change → update parameter lists and response schemas
- Auth/authorization changes → update auth examples and security docs
- Use `/update-api-doc` or `/generate-api-doc` prompts for this

### External API Docs (`docs/external-apis/`) — Update when:
- External API adds fields → add rows to field mapping table
- External API changes auth → update auth section
- Rate limits change → update rate limits table
- New gotchas discovered → add to gotchas section

### Code Examples — Update when:
- Function signatures change → update all snippets using that function
- API interfaces change → update example requests/responses
- Best practices evolve → replace outdated patterns

### Configuration Docs — Update when:
- New env vars added → document in README and `.env.example`
- Config file structure changes → update example config
- Deployment config changes → update deployment guides

## Changelog Management

Add changelog entries for every meaningful change:

```markdown
## [Version] - YYYY-MM-DD

### Added
- New feature description

### Changed
- **BREAKING**: Description of breaking change
- Other changes

### Fixed
- Bug fix description

### Deprecated
- Feature marked for removal in vX.X
```

## Quality Standards

### Do's
- ✅ Update documentation in the same commit as code
- ✅ Include before/after examples for breaking changes
- ✅ Test code examples before committing
- ✅ Use consistent formatting and terminology
- ✅ Document limitations and edge cases
- ✅ Provide migration paths for breaking changes
- ✅ Keep documentation DRY — link instead of duplicating

### Don'ts
- ❌ Commit code changes without updating documentation
- ❌ Leave outdated examples in documentation
- ❌ Document features that don't exist yet
- ❌ Use vague or ambiguous language
- ❌ Forget to update changelog
- ❌ Ignore broken links or failing examples

## API Documentation Format

```markdown
### `functionName(param1, param2)`

Brief description of what the function does.

**Parameters:**
- `param1` (type): Description
- `param2` (type, optional): Description with default value

**Returns:**
- `type`: Description of return value

**Throws:**
- `ErrorType`: When and why error is thrown

**Example:**
\`\`\`typescript
const result = functionName('value', 42);
\`\`\`
```

## Review Checklist

Before considering documentation complete:
- [ ] README.md reflects current project state
- [ ] All new features are documented
- [ ] Code examples are tested and work
- [ ] API documentation is complete and accurate
- [ ] Configuration examples are up to date
- [ ] Breaking changes documented with migration guide
- [ ] CHANGELOG.md is updated
- [ ] Links are valid
- [ ] Environment variables are documented

> Source: [github/awesome-copilot](https://github.com/github/awesome-copilot)
