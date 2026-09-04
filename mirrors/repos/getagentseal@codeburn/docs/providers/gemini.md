# Gemini

Google Gemini CLI.

- **Source:** `src/providers/gemini.ts`
- **Loading:** eager (`src/providers/index.ts`)
- **Test:** `tests/providers/gemini.test.ts`

## Where it reads from

`~/.gemini/tmp/<project>/chats/session-*.json` and `session-*.jsonl` (`gemini.ts:218-252`).

## Storage format

Either a single JSON document per session or JSONL, depending on Gemini CLI version. The parser tries `JSON.parse` on the whole file first (single-JSON, Gemini CLI <=0.38); if that throws or the result doesn't look like a session, it falls back to parsing the file line by line as JSONL (`gemini.ts:194-204`).

## Caching

None.

## Deduplication

Per session and message: the key is `gemini:<sessionId>:<messageId>`, where `messageId` falls back to a per-message ordinal when the message has no `id` (`gemini.ts:97`).

## Quirks

- **Cached tokens are a subset of input.** Gemini reports cached tokens included inside `promptTokenCount`. The parser subtracts them so callers see Anthropic semantics (cached are separate).
- **Thoughts are billed at output rate** (`gemini.ts:125`).
- One call per assistant message that carries usage. `parseSession` walks every `gemini`-type message with `tokens` and `model` set and emits one `ParsedProviderCall` per message, not one per session.

## When fixing a bug here

1. Add a fixture-based regression test alongside any parsing change; `tests/providers/gemini.test.ts` is the place for it.
2. If the bug involves a new Gemini version's schema, keep the same try-JSON-then-JSONL fallback; do not assume one format based on a byte sniff.
3. If the bug is "Gemini sessions report less than expected", check whether the cached-token subtraction is over-correcting.
