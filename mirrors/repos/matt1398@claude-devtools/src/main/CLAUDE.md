# Main Process

Node.js runtime handling file system, IPC, and app lifecycle.

## Structure
- `index.ts` - App entry point, lifecycle management
- `ipc/` - IPC handlers organized by domain
- `services/` - Business logic by domain
- `types/` - Type definitions
- `utils/` - Utility functions
- `constants/` - Shared constants (messageTags, worktreePatterns)

## IPC Organization
Handlers in `ipc/` by domain:
- `projects.ts` - Project listing
- `sessions.ts` - Session operations
- `search.ts` - Search functionality
- `subagents.ts` - Subagent details
- `validation.ts` - Path validation
- `utility.ts` - Shell & file operations
- `config.ts` - Configuration
- `notifications.ts` - Notifications

## Adding IPC Handler
1. Add to domain file in `ipc/`
2. If new domain, create file and register in `handlers.ts`
3. Add type in `preload/index.ts`
4. Implement in appropriate service

## File Watching
FileWatcher service monitors session files with 100ms debounce.
Notifies renderer of changes via IPC events.
