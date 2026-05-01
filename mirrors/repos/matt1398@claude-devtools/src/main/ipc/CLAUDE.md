# IPC Handlers

Domain-organized IPC request handlers for main process.

## Structure
```
ipc/
├── handlers.ts          # Initialization and registration
├── config.ts            # App configuration handlers
├── configValidation.ts  # Config input validation/sanitization
├── guards.ts            # IPC argument type guards
├── notifications.ts     # Notification management
├── projects.ts          # Project listing, repository grouping
├── search.ts            # Session content search
├── sessions.ts          # Session operations, pagination
├── subagents.ts         # Subagent detail drill-down
├── utility.ts           # Shell operations, file reading
└── validation.ts        # Path validation, file mentioning
```

## Handler Pattern
Each domain module exports:
```typescript
// Setup with services
initialize{Domain}Handlers(services)

// Register with ipcMain
register{Domain}Handlers(ipcMain)

// Cleanup on app quit
remove{Domain}Handlers(ipcMain)
```

## Service Dependencies
`initializeIpcHandlers()` receives service instances:
- `ProjectScanner` - File system scanning
- `SessionParser` - JSONL parsing
- `SubagentResolver` - Subagent linking
- `ChunkBuilder` - Chunk analysis
- `DataCache` - Result caching

## Response Pattern
Config handlers use `IpcResult<T>` wrapper:
```typescript
return { success: true, data: result };
return { success: false, error: message };
```

Other handlers return data directly or `null` on error.

## Adding New Handler
1. Add to existing domain file or create new file
2. Call `initialize{Domain}Handlers()` if new domain
3. Add `register/remove{Domain}Handlers` in `handlers.ts`
4. Add channel constant in `preload/constants/ipcChannels.ts`
5. Add method to ElectronAPI in `preload/index.ts`
6. Implement service logic in `src/main/services/`
