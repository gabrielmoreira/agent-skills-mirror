# Claude Family Prompting Guide

Covers Claude Opus 4.6, Claude Sonnet 4.6, Claude Sonnet 4.5, and Claude Haiku 4.5. Based on official Anthropic documentation.

Sources:
- [Prompting Best Practices — Claude 4](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Prompt Engineering Overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Extended Thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)
- [Adaptive Thinking](https://docs.anthropic.com/en/docs/build-with-claude/adaptive-thinking)
- [Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Structured Outputs](https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs)
- [Citations](https://docs.anthropic.com/en/docs/build-with-claude/citations)
- [Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Vision](https://docs.anthropic.com/en/docs/build-with-claude/vision)
- [Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)
- [The "Think" Tool](https://www.anthropic.com/engineering/claude-think-tool)

## Model Comparison

| Aspect | Opus 4.6 | Sonnet 4.6 | Sonnet 4.5 | Haiku 4.5 |
|--------|----------|------------|------------|-----------|
| Context window | 1M (beta) | 200K (1M beta) | 200K | 200K |
| Default thinking | Adaptive | Adaptive | Extended (`budget_tokens`) | None |
| Effort parameter | Yes (default: high) | Yes (default: high) | No | No |
| Prefill support | **No** (deprecated) | **No** (deprecated) | Yes | Yes |
| Structured outputs | Yes (`strict: true`) | Yes | Yes | Limited |
| Cost (in/out per 1M) | $15/$75 | $3/$15 | $3/$15 | $0.80/$4 |
| Key strength | Hardest problems, deep research | Fast agentic coding, balance | Extended thinking with budget | Speed, volume |

## Thinking Modes

### Adaptive Thinking (Claude 4.6 — Recommended)

Claude dynamically decides when and how much to think based on query complexity and `effort` parameter.

```python
client.messages.create(
    model="claude-opus-4-6",
    max_tokens=64000,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},  # max, high, medium, low
    messages=[{"role": "user", "content": "..."}],
)
```

**Effort levels:**
- `max` — deepest reasoning, highest latency/cost
- `high` — default for Opus 4.6 and Sonnet 4.6
- `medium` — recommended for most applications
- `low` — high-volume, latency-sensitive workloads

**When adaptive thinking wins:**
- Autonomous multi-step agents (coding, data analysis, bug finding)
- Computer use agents (best-in-class accuracy)
- Bimodal workloads (mix of easy and hard tasks)

**Steering adaptive thinking:**
If the model thinks too often (common with complex system prompts):

```
Extended thinking adds latency and should only be used when it will
meaningfully improve answer quality — typically for problems that require
multi-step reasoning. When in doubt, respond directly.
```

### Extended Thinking (Claude Sonnet 4.5 and older)

Manual token budget for reasoning.

```python
client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=64000,
    thinking={"type": "enabled", "budget_tokens": 16384},
    messages=[{"role": "user", "content": "..."}],
)
```

- Minimum `budget_tokens`: 1,024
- Must be less than `max_tokens`
- Accuracy improves logarithmically with thinking tokens
- Claude often won't use the entire budget, especially above 32K

### Interleaved Thinking (Sonnet 4.6 with Extended)

Sonnet 4.6 supports thinking between tool calls when using extended mode:

```python
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16384,
    thinking={"type": "enabled", "budget_tokens": 16384},
    output_config={"effort": "medium"},
    messages=[{"role": "user", "content": "..."}],
)
```

### Overthinking Prevention (Opus 4.6)

Opus 4.6 explores extensively at higher effort. If undesirable:

```
When deciding how to approach a problem, choose an approach and commit to it.
Avoid revisiting decisions unless you encounter new information that directly
contradicts your reasoning. If you're weighing two approaches, pick one and
see it through.
```

For Sonnet 4.6: switch from adaptive to extended thinking with a `budget_tokens` cap for a hard ceiling on thinking costs.

### The "Think" Tool

A lightweight alternative to extended thinking — a tool with no side effects that gives Claude a scratchpad for multi-step reasoning:

```json
{
    "name": "think",
    "description": "Use this tool to think through complex problems step-by-step before responding.",
    "input_schema": {
        "type": "object",
        "properties": {
            "thought": {
                "type": "string",
                "description": "Your step-by-step thinking about the problem."
            }
        },
        "required": ["thought"]
    }
}
```

Best used when extended thinking is disabled but you want structured reasoning at specific points.

## Prefill Deprecation (Claude 4.6)

Prefilling the assistant turn is **no longer supported** on Claude 4.6 models.

### Migration Paths

| Previous Prefill Use | New Approach |
|---------------------|-------------|
| Force JSON output (`{`) | Structured Outputs (`strict: true`) |
| Skip preamble (`Here is...`) | System prompt: "Respond directly without preamble" |
| Avoid bad refusals | Improved in Claude 4.6; clear user-message prompting sufficient |
| Continue partial response | Move continuation text to user message |
| Context hydration | Inject reminders in user turn or via tools |

## General Prompting Principles

### Be Clear and Direct

Claude responds well to explicit instructions. Think of Claude as a brilliant new employee lacking your context.

**Golden rule:** Show your prompt to a colleague with minimal context. If they'd be confused, Claude will be too.

```
# Less effective
Create an analytics dashboard

# More effective
Create an analytics dashboard. Include as many relevant features and
interactions as possible. Go beyond the basics to create a fully-featured
implementation.
```

### Add Context / Motivation

Explain WHY behind instructions. Claude generalizes from explanations:

```
# Less effective
NEVER use ellipses

# More effective
Your response will be read aloud by a text-to-speech engine, so never use
ellipses since the engine won't know how to pronounce them.
```

### Use Examples (Few-Shot)

3–5 well-crafted examples dramatically improve accuracy. Make them:
- **Relevant** — mirror actual use cases
- **Diverse** — cover edge cases
- **Structured** — wrap in `<example>` / `<examples>` tags

### XML Tags for Structure

Use semantic XML tags to separate concerns:
- `<instructions>`, `<context>`, `<input>`, `<documents>`
- Consistent tag names across prompts
- Nest naturally: `<documents><document index="1">...</document></documents>`

### Role Setting

```python
client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    system="You are a helpful coding assistant specializing in Python.",
    messages=[{"role": "user", "content": "..."}],
)
```

## Output & Formatting Control

### Claude 4.6 Communication Style

More concise and natural than previous models:
- More direct and grounded (fact-based, not self-celebratory)
- More conversational and less machine-like
- Less verbose — may skip summaries after tool calls

If you need more visibility:
```
After completing a task that involves tool use, provide a quick summary
of the work you've done.
```

### Steer Format Positively

Tell Claude what to do, not what NOT to do:
- Instead of "Do not use markdown" → "Compose smoothly flowing prose paragraphs"
- Use XML format indicators: "Write in `<prose>` tags"
- Match prompt style to desired output style (removing markdown from prompts reduces markdown in output)

### Minimize Markdown/Bullets

```xml
<avoid_excessive_markdown_and_bullet_points>
Write in clear, flowing prose using complete paragraphs. Reserve markdown
for inline code, code blocks, and simple headings.
DO NOT use ordered/unordered lists unless: a) presenting truly discrete items,
or b) user explicitly requests a list.
Instead of bullets, incorporate items naturally into sentences.
</avoid_excessive_markdown_and_bullet_points>
```

### LaTeX Control (Opus 4.6)

Opus 4.6 defaults to LaTeX for math. To prevent:
```
Format in plain text only. Do not use LaTeX, MathJax, or markup notation
such as \( \), $, or \frac{}{}. Write math using standard text characters.
```

## Tool Use Best Practices

### Explicit Action Instructions

Claude may suggest rather than act. Be explicit:
```
# Claude will only suggest
Can you suggest some changes to improve this function?

# Claude will make changes
Change this function to improve its performance.
```

### Proactive vs Conservative Action

**Proactive (default to action):**
```xml
<default_to_action>
By default, implement changes rather than only suggesting them. If user intent
is unclear, infer the most useful likely action and proceed, using tools to
discover missing details instead of guessing.
</default_to_action>
```

**Conservative (default to analysis):**
```xml
<do_not_act_before_instructions>
Do not jump into implementation unless clearly instructed. When intent is
ambiguous, default to providing information and recommendations. Only proceed
with edits when explicitly requested.
</do_not_act_before_instructions>
```

### Parallel Tool Calling

Claude 4.6 excels at parallel execution. Boost to ~100% success:

```xml
<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between
calls, make all independent calls in parallel. Prioritize simultaneous
execution whenever actions can be done in parallel. Never use placeholders
or guess missing parameters.
</use_parallel_tool_calls>
```

To reduce parallel execution:
```
Execute operations sequentially with brief pauses between each step.
```

### Tool Overtriggering (Opus 4.6)

Opus 4.6 is more responsive to system prompts. Aggressive tool instructions from older models will cause overtriggering:

```
# Too aggressive (was needed for older models)
CRITICAL: You MUST use this tool when...

# Appropriate for 4.6
Use this tool when...
```

### Structured Outputs (Tool-Based)

Add `strict: true` to tool definitions for guaranteed schema validation:
```json
{
    "name": "extract_data",
    "description": "Extract structured data from text",
    "strict": true,
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "category": {"type": "string", "enum": ["A", "B", "C"]}
        },
        "required": ["name", "category"]
    }
}
```

Eliminates type mismatches and missing fields. Enable with beta header: `structured-outputs-2025-11-13`.

**Note:** Cannot use with Citations (citations require interleaving blocks).

## Long Context Best Practices

### Document Placement

Place long documents (20K+ tokens) at the **top** of the prompt, above queries and instructions. Up to 30% quality improvement.

### Document Structure

```xml
<documents>
  <document index="1">
    <source>annual_report_2023.pdf</source>
    <document_content>{{ANNUAL_REPORT}}</document_content>
  </document>
  <document index="2">
    <source>competitor_analysis.xlsx</source>
    <document_content>{{COMPETITOR_ANALYSIS}}</document_content>
  </document>
</documents>

Analyze the annual report and competitor analysis.
```

### Ground Responses in Quotes

Ask Claude to quote relevant parts before answering:
```
Find quotes from the patient records relevant to diagnosing symptoms.
Place these in <quotes> tags. Then, based on these quotes, list diagnostic
information in <info> tags.
```

### 1M Token Context (Beta)

Available for Opus 4.6 and Sonnet 4.6 with header `context-1m-2025-08-07`. Requests exceeding 200K auto-charged at premium long-context rates.

## Prompt Caching

### Cost Savings

- Cache writes: 1.25x input price
- Cache reads: 0.1x input price (90% savings)
- Up to 85% latency reduction

### Strategy

- Place cacheable content at prompt beginning
- Use `cache_control` breakpoints to separate cacheable sections
- Ensure cached sections are byte-identical across requests
- Calls must occur within 5-minute (default) or 1-hour cache lifetime

### Best Use Cases

- Long system instructions + documents
- Few-shot examples (dozens of diverse examples)
- Conversational agents with persistent context
- Agentic search with repeated tool definitions

## Citations

Ground answers in source documents with sentence-level granularity.

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {"type": "text", "media_type": "text/plain", "data": doc_text},
                "citations": {"enabled": True}
            },
            {"type": "text", "text": "Summarize the key findings."}
        ]
    }]
)
```

- Supports PDF and plain text
- `cited_text` doesn't count toward output tokens
- Up to 15% improvement in recall accuracy
- **Cannot combine with Structured Outputs**

## Vision

### Image Placement

Best performance: images before text (image-then-text structure).

### Capabilities

- Chart interpretation and analysis
- Form content extraction
- Document processing
- Image evaluation and comparison
- Up to 100 images per request (API), 20 per request (Claude.ai)

### Crop Tool for Accuracy Uplift

Consistent uplift on image evaluations when Claude can "zoom" into relevant regions:
- Provide a crop/zoom tool in tool definitions
- Claude selects relevant regions to examine in detail
- Effective for detailed analysis tasks

## Agentic Patterns

### Long-Horizon State Tracking

Claude 4.6 excels at maintaining orientation across extended sessions through incremental progress.

#### Context Awareness

Claude 4.6/4.5 tracks remaining context window. If using compaction or external files:

```
Your context window will be automatically compacted as it approaches its limit.
Do not stop tasks early due to token budget concerns. As you approach the limit,
save current progress and state to memory before the context window refreshes.
```

#### Multi-Context Window Workflows

1. **First window**: Set up framework (write tests, create setup scripts)
2. **Subsequent windows**: Iterate on todo-list
3. **Write tests in structured format**: e.g., `tests.json` — "It is unacceptable to remove or edit tests"
4. **Create QoL tools**: `init.sh` to start servers, run tests, linters
5. **Starting fresh vs compacting**: Claude 4.6 is extremely effective at discovering state from filesystem
6. **Provide verification tools**: Playwright MCP, computer use for UI testing

#### State Management

- **Structured formats** for state data (JSON for test results, task status)
- **Freeform text** for progress notes
- **Git** for state tracking across sessions — Claude 4.6 excels at this

### Autonomy vs Safety

```
Consider the reversibility and potential impact of your actions. Take local,
reversible actions freely (editing files, running tests), but for hard-to-reverse
or shared-system actions, ask the user before proceeding.

Examples warranting confirmation:
- Destructive: deleting files/branches, dropping tables, rm -rf
- Hard to reverse: git push --force, git reset --hard
- Visible to others: pushing code, commenting on PRs, sending messages
```

### Subagent Orchestration

Claude 4.6 proactively delegates to subagents without explicit instruction. Control overuse:

```
Use subagents when tasks can run in parallel, require isolated context, or
involve independent workstreams. For simple tasks, sequential operations,
or single-file edits, work directly rather than delegating.
```

### Research Pattern

```
Search for this information in a structured way. As you gather data, develop
competing hypotheses. Track confidence levels. Regularly self-critique your
approach. Update a hypothesis tree or research notes file. Break down complex
research systematically.
```

### Anti-Overengineering

```xml
<avoid_overengineering>
Only make changes directly requested or clearly necessary. Keep solutions simple:
- Don't add features, refactor code, or "improve" beyond what was asked
- Don't add docstrings/comments/annotations to unchanged code
- Don't add error handling for impossible scenarios
- Don't create abstractions for one-time operations
- Don't design for hypothetical future requirements
</avoid_overengineering>
```

### Anti-Hallucination in Agentic Coding

```xml
<investigate_before_answering>
Never speculate about code you have not opened. If the user references a specific
file, you MUST read the file before answering. Investigate and read relevant files
BEFORE answering questions about the codebase. Never make claims about code before
investigating.
</investigate_before_answering>
```

### Anti-Test-Hacking

```
Write a high-quality, general-purpose solution using standard tools.
Do not hard-code values or create solutions that only work for specific test inputs.
Implement the actual logic that solves the problem generally.
Tests verify correctness, not define the solution.
If tests are incorrect, inform me rather than working around them.
```

## Context Engineering

### The "Right Altitude" for System Prompts

Avoid two failure modes:
1. **Overly brittle**: Hardcoded if-else logic — fragile, high maintenance
2. **Overly vague**: High-level guidance without concrete signals

**Optimal:** Specific enough to guide behavior, flexible enough for strong heuristics.

### Three Strategies for Long-Horizon Tasks

**1. Compaction**
- Summarize conversations approaching context limits
- Preserve architectural decisions, unresolved bugs, implementation details
- Discard redundant tool outputs
- Start by maximizing recall, then iterate for precision

**2. Structured Note-Taking (Agentic Memory)**
- Agent writes notes persisted outside context window
- Enables multi-hour task sequences with context resets
- Claude Code uses to-do lists; custom agents use NOTES.md

**3. Sub-Agent Architectures**
- Specialized agents handle focused tasks with clean context
- Return condensed summaries (1,000–2,000 tokens)
- Achieves separation between detailed search and synthesis

### Tool Result Trimming

Remove raw tool results from deep message history. Once a tool is called, the agent needs the summary, not raw output. This is the "safest, lightest touch" form of compaction.

### Just-In-Time Context Retrieval

Maintain lightweight identifiers (file paths, queries) and dynamically load data at runtime via tools, rather than pre-processing all data upfront.

Claude Code hybrid: pre-load CLAUDE.md files, use glob/grep for just-in-time retrieval.

## Token Efficiency

### Key Optimizations

| Technique | Savings |
|-----------|---------|
| Tool Search Tool | 85% token reduction while maintaining full tool library |
| Programmatic tool calling | 37% reduction (43,588 → 27,297 tokens) |
| Tool call output token reduction | 70% for tool calling (14% average overall) |
| Lower extended thinking budget | ~70% reduction in hidden thinking costs |
| Model routing (Sonnet for 80% of tasks) | 60% cost reduction |
| Context compaction at 50% vs 95% | Healthier sessions, less degradation |

### Temperature & Sampling

- **Temperature** (0.0–1.0, default 1.0):
  - Near 0.0 for analytical/classification tasks
  - Near 1.0 for creative/generative tasks
- **Critical:** Since Opus 4.1, temperature AND top_p cannot both be specified (API-level enforcement). Use only temperature for typical use cases.

## Frontend Design

Claude 4.6 excels at web applications but can default to "AI slop" aesthetics without guidance:

```xml
<frontend_aesthetics>
Avoid generic "AI slop" aesthetics. Make creative, distinctive frontends.
Focus on:
- Typography: Choose beautiful, unique fonts. Avoid Arial, Inter, Roboto.
- Color: Commit to a cohesive aesthetic. Dominant colors with sharp accents.
  Use CSS variables. Draw from IDE themes and cultural aesthetics.
- Motion: Prioritize CSS-only animations. Focus on high-impact moments:
  one well-orchestrated page load with staggered reveals.
- Backgrounds: Create atmosphere and depth, not solid colors.

Interpret creatively and make unexpected choices. Vary between light/dark
themes, different fonts, different aesthetics across generations.
</frontend_aesthetics>
```

## Migration to Claude 4.6

### Key Changes

1. **Prefills deprecated** — use Structured Outputs or instructions instead
2. **Adaptive thinking replaces extended thinking** — use `effort` parameter
3. **Dial back aggressive tool prompts** — 4.6 overtriggers on CAPS/MUST language
4. **Be specific about desired behavior** — add modifiers for quality/detail
5. **Request features explicitly** — animations, interactions won't appear unless asked
6. **Anti-laziness prompts may backfire** — 4.6 is already proactive

### Sonnet 4.5 → Sonnet 4.6

- Set `effort` explicitly (default `high` may increase latency)
- `medium` for most applications; `low` for high-volume
- Set large `max_tokens` (64K recommended at medium/high effort)
- For coding: start with `medium` effort
- For chat/non-coding: start with `low` effort

### Extended → Adaptive Thinking Migration

```python
# Before (Sonnet 4.5)
thinking={"type": "enabled", "budget_tokens": 32000}

# After (Opus/Sonnet 4.6)
thinking={"type": "adaptive"},
output_config={"effort": "high"}
```

### When to Use Opus vs Sonnet 4.6

- **Opus 4.6**: Hardest problems, large-scale code migrations, deep research, extended autonomous work
- **Sonnet 4.6**: Fast turnaround, cost efficiency, most production workloads
