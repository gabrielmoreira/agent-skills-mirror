---
name: llm-structured-output
description: "Gets schema-constrained JSON from LLMs via OpenAI json_schema, Anthropic tool_use extraction, Gemini responseSchema, or local GBNF. Use when extracting typed objects, enums, or validated JSON from model APIs (zodResponseFormat, instructor, marvin). Not for free-form prose, Zod form/API validation (zod-validation-expert), or real tool orchestration."
version: 1.0.1
risk: safe
source: community
date_added: "2026-03-12"
---

# LLM Structured Output

## Overview

Extract typed, validated data from LLM API responses instead of parsing free-text. This skill covers the three main provider approaches — OpenAI's `response_format` with JSON Schema, Anthropic's `tool_use` block for structured extraction, and Google's `responseSchema` in Gemini — plus constrained decoding for local models. You will learn when each approach works, when it breaks, and how to build retry logic around schema validation failures that every production system encounters.

## When to Use

Use this skill when:

- The user needs to extract structured data (JSON objects, arrays, enums) from an LLM response.
- The user is building a pipeline where LLM output feeds directly into code (database writes, API calls, UI rendering).
- The user asks about `response_format`, `json_mode`, `json_object`, or `json_schema` in OpenAI.
- The user asks about using Anthropic's `tool_use` or `tool_result` blocks for data extraction (not for actual tool execution).
- The user asks about Zod schemas with `zodResponseFormat()` from the `openai` npm package.
- The user needs to parse LLM output into Pydantic models using `instructor`, `marvin`, or manual validation.
- The user is getting malformed JSON, missing fields, or wrong types from LLM responses and needs a fix.
- The user asks about `controlled generation`, `constrained decoding`, or `grammar-based sampling` in local models.

Do NOT use this skill when:

- The user wants free-form text generation (summaries, essays, chat).
- The user is asking about Zod for form validation or API input validation (use `zod-validation-expert` instead).
- The user needs prompt engineering for better text quality (not structure).
- The user wants to call real external tools/APIs (this skill covers using `tool_use` as a structured output hack, not actual tool orchestration).

## Prerequisites

- An API key for the target provider (OpenAI, Anthropic, or Google). Use placeholder `YOUR_KEY` in examples — never commit live secrets.
- Python 3.10+ with `openai`, `anthropic`, or `google-generativeai` SDK installed, or Node.js 18+ with the `openai` npm package.
- For Pydantic workflows: `pip install pydantic openai instructor` (or `marvin` if preferred).
- For Zod workflows: `npm install openai zod`.
- For local model constrained decoding: `llama.cpp` (GBNF grammars) or `vLLM` (`--json-schema` flag).
- Windows host is primary. Use PowerShell for all CLI commands. Path separators in examples use backslash on Windows.

## Procedure

### Step 1 — Identify the target schema

Ask the user what fields they need extracted. Define every field with its type, whether it is required or optional, and valid enum values if applicable. Do not proceed without a concrete schema.

### Step 2 — Choose the provider-appropriate method

| Provider | Method | Key Setting |
|---|---|---|
| OpenAI (gpt-4o, gpt-4o-mini) | `response_format: { type: "json_schema", json_schema: { ... } }` | Set `"strict": true` for constrained decoding |
| Anthropic (Claude) | Define a single tool with target schema as `input_schema` | Set `tool_choice: { type: "tool", name: "extract_data" }` |
| Google (Gemini) | `generationConfig.responseSchema` + `responseMimeType: "application/json"` | Provide a JSON Schema object |
| Local models (llama.cpp, vLLM) | GBNF grammars or `--json-schema` flag | Constrained decoding at token level |

### Step 3 — Write the schema in the user's language

- **Python:** Define a Pydantic `BaseModel`.
- **TypeScript:** Define a Zod schema and convert with `zodResponseFormat()`.
- **Raw API calls:** Write JSON Schema directly.

### Step 4 — Include field-level descriptions in the schema

Every field must have a `description` string that tells the model what to put there. Models use these descriptions as implicit prompt instructions. A field described as `"The user's sentiment as positive, negative, or neutral"` produces better results than a bare `sentiment: str` with no context.

### Step 5 — Set the system prompt to reinforce structure

Tell the model its job is data extraction, not conversation.

Example system prompt:

```
You are a data extraction system. Analyze the input and return the requested fields. Do not include explanations outside the JSON structure.
```

### Step 6 — Enable strict mode (OpenAI)

If using OpenAI's `json_schema` mode, set `"strict": true` in the schema definition. This activates constrained decoding where the model can only output tokens that conform to the schema. Without `strict: true`, the model may still produce invalid JSON.

### Step 7 — Extract data from the correct block (Anthropic)

If using Anthropic's `tool_use` approach, extract the structured data from `response.content` by finding the block where `type == "tool_use"` and reading its `input` field. Do not parse the text blocks — the structured data lives exclusively in the `tool_use` block.

### Step 8 — Validate the response in application code

Even with constrained decoding, validate with Pydantic's `model_validate()` or Zod's `.parse()` before passing data downstream. This catches semantic issues (empty strings, out-of-range numbers) that schema conformance alone cannot prevent.

### Step 9 — Build a retry loop for validation failures

When validation fails, send the original input plus the failed output and the validation error back to the model with an instruction like:

```
Your previous output failed validation: {error}. Fix the output.
```

Cap retries at 3 attempts.

### Step 10 — Log every structured output call

Log: the input, the raw response, the parsed result, and any validation errors. When structured output breaks in production, you need these logs to determine whether the failure was a schema design issue, a prompt issue, or a model regression.

## Examples

### Example 1: OpenAI Structured Outputs with Pydantic (Python)

```python
from pydantic import BaseModel, Field
from openai import OpenAI
from enum import Enum

class Sentiment(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"

class ReviewAnalysis(BaseModel):
    sentiment: Sentiment = Field(description="Overall sentiment of the review")
    key_topics: list[str] = Field(description="Main topics mentioned, max 5")
    purchase_intent: bool = Field(description="Whether the reviewer would buy again")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Model confidence 0-1")

client = OpenAI()
response = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "Extract structured review analysis."},
        {"role": "user", "content": "This laptop is amazing. The battery lasts forever and the keyboard feels great. Definitely buying the next version."}
    ],
    response_format=ReviewAnalysis,
)
result = response.choices[0].message.parsed
# result.sentiment == Sentiment.positive
# result.key_topics == ["battery life", "keyboard"]
# result.purchase_intent == True
```

### Example 2: Anthropic tool_use for Structured Extraction (Python)

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="You are a data extraction system. Use the provided tool to return structured data.",
    tools=[{
        "name": "extract_invoice",
        "description": "Extract invoice fields from text",
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor_name": {"type": "string", "description": "Company that issued the invoice"},
                "total_amount": {"type": "number", "description": "Total amount in USD"},
                "line_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "quantity": {"type": "integer"},
                            "unit_price": {"type": "number"}
                        },
                        "required": ["description", "quantity", "unit_price"]
                    }
                }
            },
            "required": ["vendor_name", "total_amount", "line_items"]
        }
    }],
    tool_choice={"type": "tool", "name": "extract_invoice"},
    messages=[{"role": "user", "content": "Invoice from Acme Corp: 3x Widget A at $10 each, 1x Widget B at $25. Total: $55."}]
)
# Find the tool_use block — do NOT parse text blocks
tool_block = next(b for b in response.content if b.type == "tool_use")
invoice = tool_block.input
# invoice["vendor_name"] == "Acme Corp"
# invoice["total_amount"] == 55.0
```

### Example 3: TypeScript with Zod + zodResponseFormat

```typescript
import OpenAI from "openai";
import { z } from "zod";
import { zodResponseFormat } from "openai/helpers/zod";

const EventSchema = z.object({
  event_name: z.string().describe("Name of the event"),
  date: z.string().describe("ISO 8601 date string"),
  location: z.string().describe("City and venue"),
  attendee_count: z.number().int().describe("Expected number of attendees"),
  is_virtual: z.boolean().describe("Whether the event is online-only"),
});

const client = new OpenAI();
const completion = await client.beta.chat.completions.parse({
  model: "gpt-4o-2024-08-06",
  messages: [
    { role: "system", content: "Extract event details from the text." },
    { role: "user", content: "Tech Summit 2025 in Austin at the Convention Center on March 15th. Expecting 2000 attendees, in-person only." },
  ],
  response_format: zodResponseFormat(EventSchema, "event_extraction"),
});
const event = completion.choices[0].message.parsed;
// event.event_name === "Tech Summit 2025"
// event.is_virtual === false
```

## Pitfalls

### HARD RULES — never violate these

1. **Never use `response_format: { type: "json_object" }` without a schema.** This is OpenAI's legacy JSON mode — it guarantees valid JSON syntax but not schema conformance. The model can return `{"result": "hello"}` when you expected `{"name": str, "age": int}`. Always use `json_schema` with a full schema definition instead.

2. **Never parse Anthropic's text blocks for structured data.** When using `tool_choice` to force structured output, the data is in the `tool_use` content block, not in any `text` block. Parsing `response.content[0].text` will either return empty string or a conversational preamble — never the data you need.

3. **Never define schema fields without descriptions.** A field named `status` with no description can mean HTTP status, order status, or review status. Models use field descriptions as extraction instructions. Omitting them is equivalent to omitting half your prompt.

4. **Never use `additionalProperties: true` in strict mode schemas.** OpenAI's strict mode requires `additionalProperties: false` on every object in the schema. If you set it to true or omit it, the API rejects the request with a 400 error — not at response time. You will never get a response at all.

5. **Never put extraction instructions only in the user message and not the system prompt.** The system prompt has higher attention weight for behavioral instructions. Putting "extract the following fields" only in the user message alongside the source text forces the model to split attention between the instruction and the data. System prompt defines behavior; user message provides input data.

6. **Never assume structured output means correct output.** Constrained decoding guarantees the response matches the schema's types and structure. It does not guarantee the values are correct. A model can return `{"sentiment": "positive"}` for a negative review if the source text is ambiguous. Always validate semantics in application code after schema validation.

7. **Never use recursive or deeply nested schemas without testing.** Recursive types (`$ref` pointing to the same definition) and schemas deeper than 3 levels increase decoding latency significantly and raise the probability of the model hitting `max_tokens` before completing the JSON structure. Flatten nested schemas where possible.

### Edge cases to watch for

1. **Long source text exceeding context window.** When the input text is too long, the model may truncate its reading and return incomplete extractions. Split long documents into chunks, extract from each chunk independently, then merge results in application code. Do not rely on the model to handle 50-page documents in a single call.

2. **The model returns a `refusal` instead of structured data.** OpenAI's structured output can return a `refusal` field when the model considers the request unsafe. Check `response.choices[0].message.refusal` before accessing `.parsed`. If `refusal` is not None, the parsed data will be None and accessing it throws an error.

3. **Array fields returning empty when data exists.** Models sometimes return `[]` for array fields when the source text contains the data but the field description is too vague. Fix by making the description prescriptive: `"List of all product names mentioned in the text. Return at least one if any product is referenced."`.

4. **Enum values not matching due to casing.** If you define an enum as `["Active", "Inactive"]` but the model returns `"active"`, validation fails. Either lowercase all enum values in the schema or add a normalization step before validation. OpenAI's strict mode respects exact casing; Anthropic may not.

5. **Streaming with structured output.** OpenAI supports streaming structured output where partial JSON arrives chunk by chunk. You cannot parse intermediate chunks as valid JSON. Use the `openai` SDK's built-in partial parsing or buffer chunks until the stream completes. Anthropic's `tool_use` blocks arrive complete in a single `content_block_stop` event — no partial assembly needed.

## Verification

After implementing a structured output pipeline, verify correctness with these checks:

1. **Schema conformance check — confirm the API accepts the schema:**

   ```powershell
   # Python: run a single extraction and confirm no 400 error
   python -c "from your_module import extract; print(extract('test input'))"
   ```

   If you see a `400 Bad Request` mentioning `additionalProperties` or `strict`, your schema is missing `"additionalProperties": false` on one or more objects.

2. **Parsed result is not None:**

   ```python
   result = response.choices[0].message.parsed
   assert result is not None, "Parsed result is None — check for refusal or schema error"
   ```

3. **Refusal check (OpenAI):**

   ```python
   if response.choices[0].message.refusal is not None:
       print(f"Model refused: {response.choices[0].message.refusal}")
       # Do not proceed — handle safety refusal
   ```

4. **Tool_use block exists (Anthropic):**

   ```python
   tool_blocks = [b for b in response.content if b.type == "tool_use"]
   assert len(tool_blocks) == 1, f"Expected 1 tool_use block, got {len(tool_blocks)}"
   ```

5. **Semantic validation passes:**

   ```python
   # Pydantic validation with constraints
   validated = ReviewAnalysis.model_validate(result)
   assert 0.0 <= validated.confidence_score <= 1.0
   assert len(validated.key_topics) <= 5
   ```

6. **Retry loop fires on bad output:**

   Inject a deliberately malformed response into your retry path and confirm the loop sends the validation error back to the model and retries up to 3 times.

7. **Logs contain all four fields:**

   Confirm your log entries include: input text, raw API response, parsed result, and any validation errors. Without all four, production debugging is impossible.

## Best Practices

1. **Start with the simplest schema that solves the problem.** Flat objects with 3–5 fields produce higher accuracy than nested schemas with 20+ fields. If you need complex data, extract in two passes: first extract top-level entities, then make a second call to extract details for each entity.

2. **Use enums instead of free-form strings for categorical data.** A field `mood: str` can return anything. A field `mood: Literal["happy", "sad", "neutral", "angry"]` constrains the model to exactly those values. This reduces downstream parsing logic to zero.

3. **Pin the model version in production.** `gpt-4o` is an alias that changes when OpenAI releases new versions. Structured output behavior can change between versions. Use `gpt-4o-2024-08-06` explicitly so that your schema+prompt combination remains stable until you deliberately upgrade.

4. **Test schema changes against 20+ real inputs before deploying.** Schema changes (adding a field, changing a type, modifying a description) can break extraction on inputs that previously worked. Build a test suite of real inputs with expected outputs and run it on every schema change. This is the structured output equivalent of unit testing.

5. **Use `default` values in Pydantic models for optional fields.** When a field might not have relevant data in the source text, define it as `Optional[str] = None` in Pydantic or `.optional()` in Zod. Without defaults, the model is forced to hallucinate a value for fields where the source text has no answer.

6. **Separate extraction schemas from application schemas.** Your LLM extraction schema should match what the model can reliably produce. Your application database schema may have additional computed fields, foreign keys, or constraints. Map between them in application code — do not force the LLM to understand your database schema.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.

## Related Skills

- `zod-validation-expert` — for Zod-based form and API input validation (not LLM structured output).
- `prompt-engineering` — for improving free-form text generation quality.
