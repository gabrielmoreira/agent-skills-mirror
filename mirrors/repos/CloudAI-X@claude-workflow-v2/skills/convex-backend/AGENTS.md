# Convex Backend Guidelines - Complete Reference

Comprehensive guide for building Convex backends. This document contains all rules with detailed code examples.

---

## 1. Function Guidelines

### 1.1 New Function Syntax

ALWAYS use the new function syntax for Convex functions:

```typescript
import { query } from "./_generated/server";
import { v } from "convex/values";

export const f = query({
  args: {},
  returns: v.null(),
  handler: async (ctx, args) => {
    // Function body
  },
});
```

### 1.2 HTTP Endpoint Syntax

HTTP endpoints are defined in `convex/http.ts` and require an `httpAction` decorator:

```typescript
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";

const http = httpRouter();

http.route({
  path: "/echo",
  method: "POST",
  handler: httpAction(async (ctx, req) => {
    const body = await req.bytes();
    return new Response(body, { status: 200 });
  }),
});

export default http;
```

HTTP endpoints are always registered at the exact path you specify. For example, `/api/someRoute` registers at `/api/someRoute`.

### 1.3 Function Registration

**Public Functions** - Use `query`, `mutation`, and `action`:

```typescript
import { query, mutation, action } from "./_generated/server";
```

These functions are part of the public API and are exposed to the public Internet. Do NOT use them for sensitive internal functions.

**Internal Functions** - Use `internalQuery`, `internalMutation`, and `internalAction`:

```typescript
import {
  internalQuery,
  internalMutation,
  internalAction,
} from "./_generated/server";
```

These functions are private and can only be called by other Convex functions.

**Important Rules:**

- You CANNOT register a function through the `api` or `internal` objects
- ALWAYS include argument and return validators for ALL Convex functions
- If a function doesn't return anything, include `returns: v.null()` as its output validator
- If the JavaScript implementation doesn't have a return value, it implicitly returns `null`

### 1.4 Function Calling

| Method            | Can Be Called From      | Purpose         |
| ----------------- | ----------------------- | --------------- |
| `ctx.runQuery`    | query, mutation, action | Call a query    |
| `ctx.runMutation` | mutation, action        | Call a mutation |
| `ctx.runAction`   | action                  | Call an action  |

**Rules:**

- ONLY call an action from another action if you need to cross runtimes (e.g., V8 to Node)
- Otherwise, extract shared code into a helper async function
- Minimize calls from actions to queries/mutations (they are transactions, splitting introduces race conditions)
- All calls take a `FunctionReference` - do NOT pass the function directly

**Type Annotation for Same-File Calls:**

```typescript
export const f = query({
  args: { name: v.string() },
  returns: v.string(),
  handler: async (ctx, args) => {
    return "Hello " + args.name;
  },
});

export const g = query({
  args: {},
  returns: v.null(),
  handler: async (ctx, args) => {
    // Specify type annotation for same-file calls
    const result: string = await ctx.runQuery(api.example.f, { name: "Bob" });
    return null;
  },
});
```

### 1.5 Function References

Function references are pointers to registered Convex functions.

```typescript
// Public functions - use `api` object
import { api } from "./_generated/api";
api.example.f; // convex/example.ts → f

// Internal functions - use `internal` object
import { internal } from "./_generated/api";
internal.example.g; // convex/example.ts → g (internal)

// Nested directories
api.messages.access.h; // convex/messages/access.ts → h
```

### 1.6 API Design

- Convex uses file-based routing - organize files thoughtfully within `convex/`
- Use `query`, `mutation`, `action` for public functions
- Use `internalQuery`, `internalMutation`, `internalAction` for private functions

---

## 2. Validators

### 2.1 Complete Validator Reference

| Convex Type | TS/JS Type  | Example Usage        | Validator                 | Notes                                |
| ----------- | ----------- | -------------------- | ------------------------- | ------------------------------------ |
| Id          | string      | `doc._id`            | `v.id(tableName)`         |                                      |
| Null        | null        | `null`               | `v.null()`                | `undefined` is not valid; use `null` |
| Int64       | bigint      | `3n`                 | `v.int64()`               | Supports -2^63 to 2^63-1             |
| Float64     | number      | `3.1`                | `v.number()`              | All IEEE-754 doubles                 |
| Boolean     | boolean     | `true`               | `v.boolean()`             |                                      |
| String      | string      | `"abc"`              | `v.string()`              | UTF-8, < 1MB                         |
| Bytes       | ArrayBuffer | `new ArrayBuffer(8)` | `v.bytes()`               | < 1MB                                |
| Array       | Array       | `[1, 3.2, "abc"]`    | `v.array(values)`         | Max 8192 values                      |
| Object      | Object      | `{a: "abc"}`         | `v.object({prop: value})` | Max 1024 entries                     |
| Record      | Record      | `{"a": "1"}`         | `v.record(keys, values)`  | ASCII keys only                      |

### 2.2 Array Validator Example

```typescript
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export default mutation({
  args: {
    simpleArray: v.array(v.union(v.string(), v.number())),
  },
  handler: async (ctx, args) => {
    //...
  },
});
```

### 2.3 Discriminated Union Validator

```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  results: defineTable(
    v.union(
      v.object({
        kind: v.literal("error"),
        errorMessage: v.string(),
      }),
      v.object({
        kind: v.literal("success"),
        value: v.number(),
      }),
    ),
  ),
});
```

### 2.4 Null Return Value

Always use `v.null()` when returning null:

```typescript
import { query } from "./_generated/server";
import { v } from "convex/values";

export const exampleQuery = query({
  args: {},
  returns: v.null(),
  handler: async (ctx, args) => {
    console.log("This query returns a null value");
    return null;
  },
});
```

### 2.5 Deprecated Validators

- `v.bigint()` is deprecated - use `v.int64()` instead
- `v.map()` and `v.set()` are NOT supported - use `v.record()` instead

---

## 3. Schema Guidelines

### 3.1 Schema Definition

Always define your schema in `convex/schema.ts`:

```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    name: v.string(),
    email: v.string(),
  }),

  messages: defineTable({
    channelId: v.id("channels"),
    authorId: v.optional(v.id("users")),
    content: v.string(),
  }).index("by_channel", ["channelId"]),
});
```

### 3.2 System Fields

Automatically added to all documents:

| Field           | Validator         | Description                |
| --------------- | ----------------- | -------------------------- |
| `_id`           | `v.id(tableName)` | Unique document identifier |
| `_creationTime` | `v.number()`      | Timestamp of creation      |

### 3.3 Index Naming Convention

Always include all index fields in the index name:

```typescript
// Good - index name reflects fields
.index("by_field1_and_field2", ["field1", "field2"])

// Bad - unclear what fields are indexed
.index("myIndex", ["field1", "field2"])
```

### 3.4 Index Field Order

Index fields must be queried in the same order they are defined:

```typescript
// If you need to query by field1→field2 AND field2→field1
// Create TWO separate indexes:
.index("by_field1_and_field2", ["field1", "field2"])
.index("by_field2_and_field1", ["field2", "field1"])
```

---

## 4. TypeScript Guidelines

### 4.1 ID Types

Use the `Id` helper type for document IDs:

```typescript
import { Id } from "./_generated/dataModel";

// Type-safe ID
const userId: Id<"users"> = doc._id;
```

### 4.2 Record with ID Keys

```typescript
import { query } from "./_generated/server";
import { Id } from "./_generated/dataModel";
import { v } from "convex/values";

export const exampleQuery = query({
  args: { userIds: v.array(v.id("users")) },
  returns: v.record(v.id("users"), v.string()),
  handler: async (ctx, args) => {
    const idToUsername: Record<Id<"users">, string> = {};
    for (const userId of args.userIds) {
      const user = await ctx.db.get(userId);
      if (user) {
        idToUsername[user._id] = user.username;
      }
    }
    return idToUsername;
  },
});
```

### 4.3 Best Practices

- Be strict with types, especially document IDs (`Id<'users'>` not `string`)
- Use `as const` for string literals in discriminated unions
- Define arrays as `const array: Array<T> = [...]`
- Define records as `const record: Record<K, V> = {...}`
- Add `@types/node` to `package.json` when using Node.js built-ins

---

## 5. Query Guidelines

### 5.1 Use Indexes, Not Filters

```typescript
// BAD - uses filter (slow table scan)
const messages = await ctx.db
  .query("messages")
  .filter((q) => q.eq(q.field("channelId"), channelId))
  .collect();

// GOOD - uses index (fast)
const messages = await ctx.db
  .query("messages")
  .withIndex("by_channel", (q) => q.eq("channelId", channelId))
  .collect();
```

### 5.2 Ordering

```typescript
// Default: ascending _creationTime
await ctx.db.query("messages").collect();

// Explicit ordering
await ctx.db.query("messages").order("asc").collect();
await ctx.db.query("messages").order("desc").collect();

// With index (ordered by index columns)
await ctx.db
  .query("messages")
  .withIndex("by_channel", (q) => q.eq("channelId", id))
  .order("desc")
  .take(10);
```

### 5.3 Getting Single Documents

```typescript
// Get by ID
const doc = await ctx.db.get(documentId);

// Get unique from query (throws if multiple match)
const doc = await ctx.db
  .query("users")
  .withIndex("by_email", (q) => q.eq("email", email))
  .unique();
```

### 5.4 Async Iteration

```typescript
// Don't use .collect() with async iteration
for await (const message of ctx.db.query("messages")) {
  // Process message
}
```

### 5.5 Deleting Documents

Convex queries do NOT support `.delete()`. Collect and delete individually:

```typescript
const docs = await ctx.db
  .query("messages")
  .withIndex("by_channel", (q) => q.eq("channelId", channelId))
  .collect();

for (const doc of docs) {
  await ctx.db.delete(doc._id);
}
```

### 5.6 Full Text Search

```typescript
const messages = await ctx.db
  .query("messages")
  .withSearchIndex("search_body", (q) =>
    q.search("body", "hello hi").eq("channel", "#general"),
  )
  .take(10);
```

### 5.7 Pagination

```typescript
import { v } from "convex/values";
import { query } from "./_generated/server";
import { paginationOptsValidator } from "convex/server";

export const listWithExtraArg = query({
  args: {
    paginationOpts: paginationOptsValidator,
    author: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("messages")
      .withIndex("by_author", (q) => q.eq("author", args.author))
      .order("desc")
      .paginate(args.paginationOpts);
  },
});
```

**Pagination Options:**

- `numItems`: max documents to return (`v.number()`)
- `cursor`: cursor for next page (`v.union(v.string(), v.null())`)

**Pagination Result:**

- `page`: array of documents
- `isDone`: boolean, true if last page
- `continueCursor`: string for next page

---

## 6. Mutation Guidelines

### 6.1 Insert

```typescript
const id = await ctx.db.insert("tasks", {
  name: "Buy milk",
  completed: false,
});
```

### 6.2 Replace (Full Document)

Fully replaces an existing document. Throws if document doesn't exist:

```typescript
await ctx.db.replace(taskId, {
  name: "Buy milk",
  completed: false,
});
```

### 6.3 Patch (Shallow Merge)

Shallow merges updates into existing document. Throws if document doesn't exist:

```typescript
await ctx.db.patch(taskId, { completed: true });
```

### 6.4 Delete

```typescript
await ctx.db.delete(taskId);
```

---

## 7. Action Guidelines

### 7.1 Node.js Runtime

Add `"use node";` to the top of files using Node.js built-in modules:

```typescript
"use node";

import { action } from "./_generated/server";
import { v } from "convex/values";

export const exampleAction = action({
  args: {},
  returns: v.null(),
  handler: async (ctx, args) => {
    // Can use Node.js APIs here
    return null;
  },
});
```

### 7.2 No Database Access

Actions cannot use `ctx.db`. Use `runQuery` and `runMutation` instead:

```typescript
export const myAction = action({
  args: {},
  returns: v.null(),
  handler: async (ctx, args) => {
    // BAD: ctx.db is not available
    // const data = await ctx.db.query("table").collect();

    // GOOD: Use runQuery
    const data = await ctx.runQuery(api.example.getData, {});
    return null;
  },
});
```

---

## 8. Scheduling Guidelines

### 8.1 Delayed Execution

```typescript
await ctx.scheduler.runAfter(0, internal.example.processData, {
  dataId: id,
});

// With delay (milliseconds)
await ctx.scheduler.runAfter(60000, internal.example.sendReminder, {
  userId: id,
});
```

### 8.2 Cron Jobs

Define crons in `convex/crons.ts`:

```typescript
import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";
import { internalAction } from "./_generated/server";
import { v } from "convex/values";

const cleanupInactiveUsers = internalAction({
  args: {},
  returns: v.null(),
  handler: async (ctx, args) => {
    console.log("Cleaning up inactive users");
    return null;
  },
});

const crons = cronJobs();

// Run every two hours
crons.interval(
  "cleanup inactive users",
  { hours: 2 },
  internal.crons.cleanupInactiveUsers,
  {},
);

// Cron expression (every day at midnight)
crons.cron("daily report", "0 0 * * *", internal.crons.generateDailyReport, {});

export default crons;
```

**Rules:**

- Only use `crons.interval` or `crons.cron` - do NOT use `crons.hourly`, `crons.daily`, etc.
- Pass a `FunctionReference`, not the function directly
- Always import `internal` from `_generated/api`, even for same-file functions

---

## 9. File Storage Guidelines

### 9.1 Getting File URLs

```typescript
const url = await ctx.storage.getUrl(fileId);
// Returns null if file doesn't exist
```

### 9.2 File Metadata

Query the `_storage` system table (do NOT use deprecated `ctx.storage.getMetadata`):

```typescript
import { query } from "./_generated/server";
import { Id } from "./_generated/dataModel";
import { v } from "convex/values";

type FileMetadata = {
  _id: Id<"_storage">;
  _creationTime: number;
  contentType?: string;
  sha256: string;
  size: number;
};

export const getFileMetadata = query({
  args: { fileId: v.id("_storage") },
  returns: v.union(
    v.object({
      _id: v.id("_storage"),
      _creationTime: v.number(),
      contentType: v.optional(v.string()),
      sha256: v.string(),
      size: v.number(),
    }),
    v.null(),
  ),
  handler: async (ctx, args) => {
    const metadata: FileMetadata | null = await ctx.db.system.get(args.fileId);
    return metadata;
  },
});
```

### 9.3 File Format

Convex storage stores items as `Blob` objects. Convert to/from `Blob` when using storage.

---

## 10. Complete Example: Chat App

### Task Requirements

- Allow creating users with names
- Support multiple chat channels
- Enable users to send messages to channels
- Automatically generate AI responses
- Show recent message history (10 messages)

### convex/schema.ts

```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  channels: defineTable({
    name: v.string(),
  }),

  users: defineTable({
    name: v.string(),
  }),

  messages: defineTable({
    channelId: v.id("channels"),
    authorId: v.optional(v.id("users")),
    content: v.string(),
  }).index("by_channel", ["channelId"]),
});
```

### convex/index.ts

```typescript
import {
  query,
  mutation,
  internalQuery,
  internalMutation,
  internalAction,
} from "./_generated/server";
import { v } from "convex/values";
import OpenAI from "openai";
import { internal } from "./_generated/api";

/**
 * Create a user with a given name.
 */
export const createUser = mutation({
  args: {
    name: v.string(),
  },
  returns: v.id("users"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("users", { name: args.name });
  },
});

/**
 * Create a channel with a given name.
 */
export const createChannel = mutation({
  args: {
    name: v.string(),
  },
  returns: v.id("channels"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("channels", { name: args.name });
  },
});

/**
 * List the 10 most recent messages from a channel in descending order.
 */
export const listMessages = query({
  args: {
    channelId: v.id("channels"),
  },
  returns: v.array(
    v.object({
      _id: v.id("messages"),
      _creationTime: v.number(),
      channelId: v.id("channels"),
      authorId: v.optional(v.id("users")),
      content: v.string(),
    }),
  ),
  handler: async (ctx, args) => {
    const messages = await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channelId", args.channelId))
      .order("desc")
      .take(10);
    return messages;
  },
});

/**
 * Send a message to a channel and schedule AI response.
 */
export const sendMessage = mutation({
  args: {
    channelId: v.id("channels"),
    authorId: v.id("users"),
    content: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const channel = await ctx.db.get(args.channelId);
    if (!channel) {
      throw new Error("Channel not found");
    }
    const user = await ctx.db.get(args.authorId);
    if (!user) {
      throw new Error("User not found");
    }
    await ctx.db.insert("messages", {
      channelId: args.channelId,
      authorId: args.authorId,
      content: args.content,
    });
    await ctx.scheduler.runAfter(0, internal.index.generateResponse, {
      channelId: args.channelId,
    });
    return null;
  },
});

const openai = new OpenAI();

export const generateResponse = internalAction({
  args: {
    channelId: v.id("channels"),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const context = await ctx.runQuery(internal.index.loadContext, {
      channelId: args.channelId,
    });
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: context,
    });
    const content = response.choices[0].message.content;
    if (!content) {
      throw new Error("No content in response");
    }
    await ctx.runMutation(internal.index.writeAgentResponse, {
      channelId: args.channelId,
      content,
    });
    return null;
  },
});

export const loadContext = internalQuery({
  args: {
    channelId: v.id("channels"),
  },
  returns: v.array(
    v.object({
      role: v.union(v.literal("user"), v.literal("assistant")),
      content: v.string(),
    }),
  ),
  handler: async (ctx, args) => {
    const channel = await ctx.db.get(args.channelId);
    if (!channel) {
      throw new Error("Channel not found");
    }
    const messages = await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channelId", args.channelId))
      .order("desc")
      .take(10);

    const result = [];
    for (const message of messages) {
      if (message.authorId) {
        const user = await ctx.db.get(message.authorId);
        if (!user) {
          throw new Error("User not found");
        }
        result.push({
          role: "user" as const,
          content: `${user.name}: ${message.content}`,
        });
      } else {
        result.push({ role: "assistant" as const, content: message.content });
      }
    }
    return result;
  },
});

export const writeAgentResponse = internalMutation({
  args: {
    channelId: v.id("channels"),
    content: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.insert("messages", {
      channelId: args.channelId,
      content: args.content,
    });
    return null;
  },
});
```

### package.json

```json
{
  "name": "chat-app",
  "version": "1.0.0",
  "dependencies": {
    "convex": "^1.31.2",
    "openai": "^4.79.0"
  },
  "devDependencies": {
    "typescript": "^5.7.3"
  }
}
```

### convex/tsconfig.json

```json
{
  "compilerOptions": {
    "allowJs": true,
    "strict": true,
    "moduleResolution": "Bundler",
    "jsx": "react-jsx",
    "skipLibCheck": true,
    "allowSyntheticDefaultImports": true,
    "target": "ESNext",
    "lib": ["ES2021", "dom"],
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "isolatedModules": true,
    "noEmit": true
  },
  "include": ["./**/*"],
  "exclude": ["./_generated"]
}
```
