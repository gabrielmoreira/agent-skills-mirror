# src/ Structure

Three-process Electron architecture:

## Processes
- `main/` - Node.js runtime (file system, IPC, lifecycle)
- `preload/` - Secure bridge (contextBridge API)
- `renderer/` - React/Chromium (UI, state, visualization)
- `shared/` - Cross-process types and utilities

## Import Pattern
Use barrel exports from domain folders:
```typescript
import { ChunkBuilder, ProjectScanner } from './services';
```

## IPC Communication
Exposed API via `window.electronAPI`, organized by domain:

| Domain | Methods | Examples |
|--------|---------|---------|
| Sessions | 10 | `getProjects()`, `getSessions()`, `getSessionsPaginated()`, `getSessionDetail()`, `getSessionMetrics()`, `getWaterfallData()`, `getSubagentDetail()`, `searchSessions()`, `getAppVersion()` |
| Repository | 2 | `getRepositoryGroups()`, `getWorktreeSessions()` |
| Validation | 2 | `validatePath()`, `validateMentions()` |
| CLAUDE.md | 3 | `readClaudeMdFiles()`, `readDirectoryClaudeMd()`, `readMentionedFile()` |
| Config | 16 | `config.get()`, `config.update()`, `config.addTrigger()`, `config.openInEditor()`, `config.pinSession()`, `config.unpinSession()`, etc. |
| Notifications | 9 | `notifications.get()`, `notifications.markRead()`, `notifications.onNew()`, etc. |
| Utilities | 7 | `openPath()`, `openExternal()`, `onFileChange()`, `onTodoChange()`, `getZoomFactor()`, `onZoomFactorChanged()` |
| Session | 1 | `session.scrollToLine()` |

Full API signatures in `src/preload/index.ts`, channel constants in `src/preload/constants/ipcChannels.ts`.
