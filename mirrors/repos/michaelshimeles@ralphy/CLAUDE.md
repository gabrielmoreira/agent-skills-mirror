# Claude Code Guidelines for Ralphy

## Code Change Philosophy

### Keep Changes Small and Focused
- **One logical change per commit** - Each commit should do exactly one thing
- If a task feels too large, break it into subtasks
- Prefer multiple small commits over one large commit
- Run feedback loops after each change, not at the end

**Quality over speed. Small steps compound into big progress.**

### Task Prioritization

When choosing the next task, prioritize in this order:

1. **Architectural decisions and core abstractions** - Get the foundation right
2. **Integration points between modules** - Ensure components connect properly
3. **Unknown unknowns and spike work** - De-risk early
4. **Standard features and implementation** - Build on solid foundations
5. **Polish, cleanup, and quick wins** - Save easy wins for later

**Fail fast on risky work. Save easy wins for later.**

## Code Quality Standards

### Write Concise Code
After writing any code file, ask yourself: *"Would a senior engineer say this is overcomplicated?"*

If yes, **simplify**.

### Avoid Over-Engineering
- Only make changes that are directly requested or clearly necessary
- Don't add features beyond what was asked
- Don't refactor code that doesn't need it
- A bug fix doesn't need surrounding code cleaned up
- A simple feature doesn't need extra configurability

### Clean Code Practices
- Don't fill files just for the sake of it
- Don't leave dead code - if it's unused, delete it completely
- Be organized, concise, and clean in your work
- No backwards-compatibility hacks for removed code
- No `// removed` comments or re-exports for deleted items

### Task Decomposition
- Use micro tasks - smaller the task, better the code
- Break complex work into discrete, testable units
- Each micro task should be completable in one focused session

## Legacy and Technical Debt

This codebase will outlive you. Every shortcut you take becomes someone else's burden. Every hack compounds into technical debt that slows the whole team down.

You are not just writing code. You are shaping the future of this project. The patterns you establish will be copied. The corners you cut will be cut again.

**Fight entropy. Leave the codebase better than you found it.**

## Project-Specific Rules

### Tech Stack
- Runtime: Bun (with Node.js 18+ fallback)
- Language: TypeScript (strict mode)
- Linting/Formatting: Biome
- CLI Framework: Commander

### Directory Structure
```
cli/
├── src/
│   ├── cli/        # CLI argument parsing and commands
│   ├── config/     # Configuration management
│   ├── engines/    # AI engine integrations
│   ├── execution/  # Task execution orchestration
│   ├── git/        # Git operations
│   ├── tasks/      # Task source handlers
│   ├── notifications/  # Webhook notifications
│   ├── telemetry/  # Usage analytics
│   └── ui/         # User interface/logging
```

### Code Standards
- Use tabs for indentation (Biome config)
- Line width: 100 characters
- Use LF line endings
- Run `bun run check` before committing
- Keep imports organized (Biome handles this)

### Boundaries - Never Modify
- PRD files during execution
- `.ralphy/progress.txt`
- `.ralphy-worktrees`
- `.ralphy-sandboxes`
- `*.lock` files

### Testing
- Write tests for new features
- Run tests before committing: `bun test`
- Ensure linting passes: `bun run check`

## Commit Guidelines

1. One logical change per commit
2. Write descriptive commit messages
3. Commit message format: `type: brief description`
   - `feat:` new feature
   - `fix:` bug fix
   - `refactor:` code restructuring
   - `docs:` documentation
   - `test:` test additions/changes
   - `chore:` maintenance tasks
