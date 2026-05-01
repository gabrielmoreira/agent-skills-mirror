# GitHub Copilot Instructions

> Organization-wide instructions for GitHub Copilot across all epicpast repositories

## Organization Context

**epicpast** is focused on building practical open source tools that improve developer workflows and platform engineering practices. Projects emphasize automation, developer experience, and AI-assisted development.

## General Coding Principles

### Code Quality Standards

1. **Readability First**: Write code that is self-documenting and easy to understand
2. **Explicit Over Implicit**: Prefer explicit type annotations and clear variable names
3. **Fail Fast**: Validate inputs early and provide clear error messages
4. **Test Coverage**: Aim for 80%+ test coverage on all projects
5. **Security by Default**: Never commit secrets, use environment variables

### Documentation Requirements

- All public APIs must have documentation
- READMEs should include quick start, installation, and usage examples
- Complex logic should have inline comments explaining the "why"
- Architectural decisions should be documented in ADRs when applicable

### Git Practices

- Use conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`
- Keep commits atomic and focused on a single change
- Write descriptive commit messages explaining the change
- Reference issues in commit messages when applicable

## Language-Specific Guidelines

### Python Projects

```python
# Always include type annotations
def process_data(items: list[str], limit: int = 10) -> dict[str, int]:
    """Process items and return counts.

    Args:
        items: List of items to process.
        limit: Maximum items to process.

    Returns:
        Dictionary mapping items to their counts.
    """
    ...
```

**Standards:**
- Python 3.12+ with modern syntax
- Use `uv` for package management
- Format with `ruff`, type check with `pyright`
- Google-style docstrings
- Prefer `dataclasses` or `pydantic` for data structures

### TypeScript/JavaScript Projects

```typescript
// Use explicit types, avoid any
interface UserConfig {
  name: string;
  timeout?: number;
}

export function createClient(config: UserConfig): Client {
  // Implementation
}
```

**Standards:**
- Node.js 22+ with ESM modules
- Use `pnpm` for package management
- ESLint 9+ flat config with strict rules
- Prefer `interface` over `type` for object shapes
- Use `vitest` for testing

### Go Projects

```go
// Package users provides user management functionality.
package users

// User represents a user in the system.
type User struct {
    ID    string
    Name  string
    Email string
}

// GetByID retrieves a user by their ID.
func (s *Service) GetByID(ctx context.Context, id string) (*User, error) {
    if id == "" {
        return nil, fmt.Errorf("id cannot be empty")
    }
    // Implementation
}
```

**Standards:**
- Go 1.23+ with modules
- Use `golangci-lint` for linting
- Standard project layout: cmd/, internal/, pkg/
- Table-driven tests with subtests
- Context propagation for cancellation

### Rust Projects

```rust
/// Processes the input data and returns results.
///
/// # Arguments
///
/// * `input` - The data to process
///
/// # Returns
///
/// A Result containing the processed data or an error.
///
/// # Examples
///
/// ```
/// let result = process("input")?;
/// ```
pub fn process(input: &str) -> Result<Output, Error> {
    // Implementation
}
```

**Standards:**
- Latest stable Rust
- Use `clippy` with pedantic lints
- Use `cargo-deny` for dependency auditing
- Prefer `thiserror` for error types
- Document all public items with examples

### Java Projects

```java
/**
 * Service for managing resources.
 *
 * <p>Handles business logic for resource operations including
 * creation, retrieval, and updates.
 */
@Service
@Transactional(readOnly = true)
public class ResourceService {

    private final ResourceRepository repository;

    public ResourceService(ResourceRepository repository) {
        this.repository = repository;
    }

    /**
     * Finds a resource by its unique identifier.
     *
     * @param id the resource identifier
     * @return the resource if found
     * @throws ResourceNotFoundException if not found
     */
    public Resource findById(Long id) {
        return repository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException(id));
    }
}
```

**Standards:**
- Java 21 LTS with Spring Boot 3.3+
- Gradle with Kotlin DSL
- Constructor injection (no field injection)
- Use Java Records for DTOs
- Checkstyle with Google style (modified)

## Project Structure Patterns

### Standard Layouts

**Python:**
```
src/package_name/
tests/
  unit/
  integration/
pyproject.toml
```

**TypeScript:**
```
src/
tests/
package.json
tsconfig.json
```

**Go:**
```
cmd/app/
internal/
pkg/
go.mod
```

## AI Assistant Integration

### CLAUDE.md Files

Each repository should have a `CLAUDE.md` file at the root containing:
- Project overview and structure
- Build and test commands
- Code style requirements
- Architecture guidelines
- Common patterns and examples

### MCP Server Configuration

Projects using VS Code should include `.vscode/mcp.json` with:
- context7 for documentation lookup
- filesystem for project navigation
- memory for session persistence (when applicable)

## Security Practices

1. **No Hardcoded Secrets**: Use environment variables or secret managers
2. **Dependency Scanning**: Enable Dependabot and review CVEs
3. **SHA-Pinned Actions**: All GitHub Actions pinned to commit SHAs
4. **Minimal Permissions**: GITHUB_TOKEN with least privilege
5. **Secret Scanning**: Pre-commit hooks with gitleaks

## CI/CD Standards

All projects should include:

```yaml
# Minimum CI workflow structure
name: CI
on: [push, pull_request]

jobs:
  lint:
    # Linting and formatting checks
  test:
    # Unit and integration tests
  build:
    # Build verification
```

For language-specific workflows, use the reusable workflows in `.github/workflows/`:
- `reusable-ci-python.yml`
- `reusable-ci-typescript.yml`
- `reusable-ci-go.yml`
- `reusable-ci-rust.yml`
- `reusable-release.yml`
- `reusable-security.yml`

## Common Patterns

### Error Handling

```python
# Python - explicit error messages
msg = f"Failed to process {item}: {reason}"
raise ValueError(msg)
```

```typescript
// TypeScript - Result pattern or explicit throws
function process(input: string): Result<Output, ProcessError> {
  if (!input) {
    return err(new ProcessError("Input required"));
  }
  return ok(doProcess(input));
}
```

```go
// Go - wrap errors with context
if err != nil {
    return fmt.Errorf("failed to fetch user %s: %w", id, err)
}
```

### Testing Patterns

- Use table-driven tests for multiple cases
- Mock external dependencies
- Test edge cases and error paths
- Include integration tests for API boundaries

### Configuration

- Use environment variables for runtime config
- Use structured config files (YAML/TOML) for complex settings
- Validate configuration at startup
- Provide sensible defaults

## Content and Documentation

For content repositories and documentation:

- Use Markdown with consistent formatting
- Include frontmatter with required metadata
- Validate links and spelling in CI
- Follow SEO best practices for public content

## When Generating Code

1. **Match existing style**: Look at surrounding code for patterns
2. **Include tests**: Generate tests alongside implementation
3. **Add documentation**: Include docstrings/comments for complex logic
4. **Handle errors**: Include proper error handling
5. **Consider edge cases**: Account for null, empty, and boundary conditions
