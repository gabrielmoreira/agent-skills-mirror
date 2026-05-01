# Services

Business logic organized by domain.

## Domains
- `analysis/` - Chunk building, semantic steps, tool execution
- `discovery/` - Project/session scanning, subagent resolution
- `error/` - Error detection, trigger checking
- `infrastructure/` - Cache, file watching, config, notifications
- `parsing/` - JSONL parsing, message classification

## Key Services

### Analysis
- **ChunkBuilder** - Orchestrates chunk building
- **ChunkFactory** - Creates chunk objects
- **ConversationGroupBuilder** - Builds conversation groups
- **ProcessLinker** - Links subagents to chunks
- **SemanticStepExtractor** - Extracts steps
- **SemanticStepGrouper** - Groups semantic steps
- **SubagentDetailBuilder** - Builds subagent detail views
- **ToolExecutionBuilder** - Builds tool execution tracking
- **ToolResultExtractor** - Extracts tool results
- **ToolSummaryFormatter** - Formats tool summaries

### Discovery
- **ProjectPathResolver** - Resolves project paths
- **ProjectScanner** - Scans ~/.claude/projects/
- **SessionContentFilter** - Filters session content
- **SessionSearcher** - Searches session content
- **SubagentLocator** - Locates subagent files
- **SubagentResolver** - Parses subagent files, detects parallel execution, enriches team metadata/colors
- **SubprojectRegistry** - Tracks subproject associations
- **WorktreeGrouper** - Groups projects by git worktree

### Parsing
- **SessionParser** - Parses JSONL files
- **MessageClassifier** - Categorizes messages (user, system, AI, noise)
- **ClaudeMdReader** - Reads CLAUDE.md configuration
- **GitIdentityResolver** - Resolves git identities

### Error
- **ErrorDetector** - Per-tool-use token counting, returns `DetectedError[]`
- **ErrorMessageBuilder** - Builds error notification messages
- **ErrorTriggerChecker** - Matches against notification triggers
- **ErrorTriggerTester** - Tests triggers against historical data
- **TriggerMatcher** - Pattern matching for triggers

### Infrastructure
- **DataCache** - LRU cache (50 entries, 10min TTL)
- **FileWatcher** - 100ms debounced file watching
- **ConfigManager** - App configuration
- **NotificationManager** - Notification handling
- **TriggerManager** - Notification trigger management

## Adding Service
1. Create in appropriate domain folder
2. Export from domain's index.ts
3. Re-export from services/index.ts
