# Preload Process

Secure bridge between main and renderer processes via Electron's contextBridge.

## Structure
- `index.ts` - ElectronAPI implementation
- `constants/ipcChannels.ts` - IPC channel name constants

## ElectronAPI Organization
Groups exposed methods by domain:

### Session APIs
- `getProjects()`, `getSessions()`, `getSessionsPaginated()`
- `getSessionDetail()`, `getSessionMetrics()`, `getWaterfallData()`
- `getSessionGroups()`, `searchSessions()`, `getAppVersion()`

### Repository APIs
- `getRepositoryGroups()`, `getWorktreeSessions()`

### Validation APIs
- `validatePath()`, `validateMentions()`

### CLAUDE.md APIs
- `readClaudeMdFiles()`, `readDirectoryClaudeMd()`, `readMentionedFile()`

### Notifications
- `notifications.{get,markRead,markAllRead,delete,clear,getUnreadCount}`
- `notifications.{onNew,onUpdated,onClicked}` - Event listeners

### Config API
- `config.{get,update}` - Read/write config
- `config.{addTrigger,updateTrigger,removeTrigger,getTriggers,testTrigger}`
- `config.{addIgnoreRegex,removeIgnoreRegex,addIgnoreRepository,removeIgnoreRepository}`
- `config.{snooze,clearSnooze,selectFolders}`
- `config.{openInEditor,pinSession,unpinSession}`

### Utilities
- `openPath()` - Shell operations
- `openExternal()` - Open URLs in browser
- `onFileChange()` - File watcher events
- `getZoomFactor()` - Get current zoom level
- `onZoomFactorChanged()` - Zoom change listener
- `session.scrollToLine()` - Deep link navigation

## IPC Pattern
Config operations use `IpcResult<T>` wrapper pattern:
```typescript
interface IpcResult<T> {
  success: boolean;
  data?: T;
  error?: string;
}
```
The `invokeIpcWithResult<T>()` helper unwraps and throws on failure.

## Adding New IPC Methods
1. Define channel constant in `constants/ipcChannels.ts`
2. Implement handler in `src/main/ipc/{domain}.ts`
3. Register in `handlers.ts` via `register{Domain}Handlers()`
4. Add method to ElectronAPI in `preload/index.ts`
5. Update `@shared/types/ElectronAPI` if cross-process type needed
