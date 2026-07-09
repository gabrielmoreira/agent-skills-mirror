# Coding Standards

## TypeScript Style

```typescript
// ✅ Good: Type-safe, clear naming
export interface Bundle {
    id: string;
    name: string;
    version: string;
}

// ❌ Bad: Any types, unclear names
async function fetch(id: any): Promise<any> { }
```

## Naming

| Element | Convention | Example |
|---------|------------|---------|
| Classes | `PascalCase` | `GitHubAdapter` |
| Functions | `camelCase` | `fetchBundles` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_TIMEOUT` |
| Files | Match class or `camelCase` | `GitHubAdapter.ts` |

## Imports

```typescript
// External
import * as vscode from 'vscode';
// Internal
import { Logger } from '../utils/logger';
// Types
import { Bundle } from '../types/registry';
```

## Error Handling

```typescript
try {
    const data = await api.fetch();
} catch (error) {
    logger.error('Failed to fetch', error as Error);
    throw new Error('Fetch failed');
}
```

## Commit Messages

Follow the conventionnal commits from the opensource world [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary)

## PR Checklist

Have a look at the [pull_request_template](../../.github/pull_request_template.md)
- [ ] Code follows style guidelines
- [ ] Tests added
- [ ] Documentation updated
- [ ] Manual testing of the functionnality done
- [ ] No new warnings

## See Also

- [Development Setup](./development-setup.md)
- [Testing](./testing.md)
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Full contribution guidelines
