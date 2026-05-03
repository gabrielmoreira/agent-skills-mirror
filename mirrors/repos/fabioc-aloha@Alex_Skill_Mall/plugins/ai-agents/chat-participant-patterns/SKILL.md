---
type: skill
lifecycle: stable
inheritance: inheritable
name: chat-participant-patterns
description: VS Code Chat API patterns.
tier: standard
applyTo: '**/*chat*,**/*participant*,**/*patterns*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Chat Participant Patterns Skill


> VS Code Chat API patterns.

## ⚠️ Staleness Warning

Chat APIs evolve with VS Code releases. **Last validated:** March 2026 (VS Code 1.111+)

**Check:** [Chat API](https://code.visualstudio.com/api/extension-guides/ai/chat), [LM API](https://code.visualstudio.com/api/extension-guides/ai/language-model), [Tools API](https://code.visualstudio.com/api/extension-guides/ai/tools), [AI Extensibility Overview](https://code.visualstudio.com/api/extension-guides/ai/ai-extensibility-overview), [EXTERNAL-API-REGISTRY.md](../../EXTERNAL-API-REGISTRY.md)

---

## When to Use Chat Participant vs. Skills/Tools

| Approach | Use When | VS Code API |
| -------- | --------- | ----------- |
| **Chat Participant** | Need full control of prompt + response, domain-specific @-mention | `vscode.chat.createChatParticipant` |
| **LM Tool** | Domain capability invoked automatically in agent sessions | `vscode.lm.registerTool` |
| **Agent Skill** (SKILL.md) | Domain knowledge embedded into any agent session (no code) | `chat.useAgentSkills` + SKILL.md file |
| **MCP Server** | Cross-platform tool providing data/actions to any MCP client | MCP SDK |

→ Prefer Skills for domain knowledge. Reserve participants for full prompt orchestration.

---

## Create Participant

```typescript
// package.json contribution
"contributes": {
    "chatParticipants": [{
        "id": "my-ext.participant",
        "name": "myparticipant",
        "fullName": "My Participant",
        "description": "What can I help with?",
        "isSticky": true,
        "commands": [{ "name": "help", "description": "Get help" }]
    }]
}

// In activate()
const participant = vscode.chat.createChatParticipant('my-ext.participant', handler);
participant.iconPath = vscode.Uri.joinPath(context.extensionUri, 'icon.png');
```

## Handler Signature

```typescript
const handler: vscode.ChatRequestHandler = async (
    request: vscode.ChatRequest,
    context: vscode.ChatContext,
    stream: vscode.ChatResponseStream,
    token: vscode.CancellationToken
): Promise<IChatResult> => {
    // Handle request
};
```

## Key Operations

| Operation | Method |
| --------- | ------ |
| Stream text | `stream.markdown()` |
| Show progress | `stream.progress()` |
| Add button | `stream.button()` |
| File tree | `stream.filetree()` |
| Reference | `stream.reference()` |
| Inline anchor | `stream.anchor()` |
| Access history | `context.history` |
| Get references | `request.references` |
| Get model | `request.model` |
| Check command | `request.command` |
| Chat location | `request.location` |

## Response Types

```typescript
// Markdown (supports CommonMark)
stream.markdown('# Title\n**bold** and _italic_');

// Code block with IntelliSense
stream.markdown('```typescript\nconst x = 1;\n```');

// Progress message
stream.progress('Processing...');

// Button (invokes VS Code command)
stream.button({ command: 'my.command', title: 'Run' });

// Command link in markdown
const md = new vscode.MarkdownString('[Run](command:my.command)');
md.isTrusted = { enabledCommands: ['my.command'] };
stream.markdown(md);

// File tree
stream.filetree([{ name: 'src', children: [{ name: 'app.ts' }] }], baseUri);

// Reference
stream.reference(vscode.Uri.file('/path/to/file.ts'));
stream.reference(new vscode.Location(uri, range));
```

## LM Integration

```typescript
const models = await vscode.lm.selectChatModels({ vendor: 'copilot' });
const response = await models[0].sendRequest(messages, {}, token);
for await (const chunk of response.text) {
    stream.markdown(chunk);
}
```

## Tool Calling

```typescript
// Using @vscode/chat-extension-utils library (recommended)
import * as chatUtils from '@vscode/chat-extension-utils';

const tools = vscode.lm.tools.filter(t => t.tags.includes('my-tag'));
const result = chatUtils.sendChatParticipantRequest(request, context, {
    prompt: 'System instructions here',
    responseStreamOptions: { stream, references: true, responseText: true },
    tools
}, token);
return await result.result;
```

## Tool Registration

```typescript
vscode.lm.registerTool('tool_name', {
    async invoke(options, token) {
        return new vscode.LanguageModelToolResult([
            new vscode.LanguageModelTextPart('result text')
        ]);
    }
});
```

## Participant Detection (Auto-routing)

```json
"chatParticipants": [{
    "id": "my-ext.participant",
    "disambiguation": [{
        "category": "my-domain",
        "description": "Questions about X domain",
        "examples": ["How do I do X?", "Explain Y concept"]
    }]
}]
```

## Follow-up Provider

```typescript
participant.followupProvider = {
    provideFollowups(result, context, token) {
        return [{ prompt: 'Tell me more', label: 'More details' }];
    }
};
```

## Message History

```typescript
// Get previous requests to this participant
const previousRequests = context.history.filter(
    h => h instanceof vscode.ChatRequestTurn
);
```

## Best Practices

| Do | Don't |
| -- | ----- |
| Stream responses incrementally | Block until complete |
| Handle cancellation via token | Ignore cancellation token |
| Catch and handle errors | Let exceptions crash |
| Use progress for long operations | Leave user waiting silently |
| Limit to one participant per extension | Create multiple participants |
| Ask consent for costly operations | Auto-execute destructive actions |

## Chat Intent Routing QA Decision Table (PL2)

When a chat participant routes user intent to an action (muscle execution, file modification, or LLM judgment), evaluate the routing decision against this table. The goal: never silently auto-decide between a mechanical action and a semantic follow-up.

| # | Check | Pass | Fail | Action on Fail |
|---|-------|------|------|----------------|
| 1 | **Mechanical vs semantic classification** — handler knows whether the request needs script execution, LLM judgment, or both | Request classified as M (muscle), S (LLM-only), or H (hybrid with handoff) | Handler treats all requests the same way | Classify intent; route M to muscle, S to LLM, H to muscle-then-prompt |
| 2 | **Hybrid handoff signal** — when a muscle runs and produces artifacts, the chat response references the decision table for Phase 2 | Response includes skill reference + table rows the LLM should evaluate | Muscle result returned as plain text with no follow-up guidance | Use `skillPrompt()` helper from muscleRunner.ts to generate Phase 2 prompt |
| 3 | **No silent auto-decision** — when multiple valid actions exist, participant surfaces the choice to the user | QuickPick, follow-up buttons, or explicit question before acting | Handler picks one action without user input | Add follow-up provider or QuickPick for ambiguous intents |
| 4 | **Cancellation respected** — long-running operations check CancellationToken | Token checked before each phase; early exit on cancellation | Operation runs to completion ignoring cancel | Add `token.isCancellationRequested` checks between phases |
| 5 | **Error context preserved** — when an operation fails, the error includes enough context for the user to retry or escalate | Error message includes: what was attempted, what failed, suggested next step | Generic "something went wrong" or raw exception text | Wrap errors with action context; suggest concrete recovery steps |
| 6 | **Decision table reference in response** — when the LLM makes a judgment, the response cites which decision table row matched | "Based on row N of [table name]: [rationale]" | LLM responds with freeform judgment and no table reference | Reference the specific skill + decision table in the system prompt |

**Current state of `handler.ts`**: Minimal stub — delegates entirely to Copilot via workspace context. This is architecturally correct (Cardinal Rule I6: architecture doesn't depend on extension). The decision table applies when/if the handler gains intent-routing logic in the future.
