# Official-source audit — 2026-11-03

This review covers the 16 existing vendor routes, not every model ever released.
Dates below mean **retrieved and reviewed**, not vendor publication dates. A rolling
"latest" page is a discovery entrypoint, not a promise that its content remains fixed.
The strategies are project adaptations, not vendor-authored prompts or proven optimal
templates. General guardrails such as preserving scope are project decisions.

| Route | Official pages reviewed | Scope and update |
|---|---|---|
| OpenAI | [Current models](https://developers.openai.com/api/docs/guides/latest-model), [reasoning](https://developers.openai.com/api/docs/guides/reasoning-best-practices), [skills and prompts](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) | Current index covers GPT-6 and GPT-6.1. Removed the hard-coded GPT-5.6 family default; retain outcome, evidence, and task boundaries. API capabilities remain conditional. |
| Anthropic | [Best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), [Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1), [Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) | Removed mandatory thinking transcripts and XML. The index links separate model guides; the Opus 5 over-verification caution is model-specific. |
| Google Gemini | [Prompt design](https://aistudio.google.com/docs/prompting-strategies) | Old ai.google.dev page redirects here. Retained scoped Gemini 3 guidance; consistent delimiters do not justify a universal ban on mixed Markdown/XML. |
| Meta Llama | [Prompt engineering](https://dev.meta.ai/llama/docs/how-to-guides/prompting) | Old llama.com link redirects to Meta's developer site. Kept clear tasks/examples; removed mandatory roles and universal capability assurances. |
| DeepSeek | [API overview](https://api-docs.deepseek.com/), [thinking](https://api-docs.deepseek.com/guides/thinking_mode/), [vision](https://api-docs.deepseek.com/guides/vision/), [R1 card](https://huggingface.co/deepseek-ai/DeepSeek-R1) | The former reasoning-model URL returns the API overview. Thinking defaults on; Flash and V4-Pro differ in top_p behavior. Flash now supports images. R1 recommendations stay explicitly legacy-specific. |
| Mistral | [Prompting](https://docs.mistral.ai/studio/conversations/chat-completion/prompting) | Old capabilities URL redirects here. Retained structured sections and conditional decision trees; do not invent priority between conflicting user requirements. |
| Qwen | [Prompt guide](https://help.aliyun.com/zh/model-studio/prompt-engineering-guide), [deep thinking](https://help.aliyun.com/zh/model-studio/deep-thinking) | Framework dimensions are aids, not permission to invent context. Thinking controls vary by model and endpoint. |
| Grok | [Best practices](https://docs.x.ai/developers/model-capabilities/text/best-practices), [web search](https://docs.x.ai/developers/tools/web-search) | Replaced homepage/product-system-prompt citations with API guidance. Search is a configured tool, not an intrinsic promise of current knowledge. |
| Perplexity | [Agent API prompt guide](https://docs.perplexity.ai/docs/agent-api/prompt-guide) | Old general URL redirects to Agent API. Its instructions/input and parameter advice must not be presented as universal Sonar syntax. Custom instructions can replace effort-level defaults. |
| Kimi | [Prompt practices](https://platform.kimi.ai/docs/guide/prompt-best-practice), [thinking](https://platform.kimi.ai/docs/guide/use-thinking-models), [index](https://platform.kimi.ai/docs/llms.txt) | K3.1 Pro has always-on reasoning and Preserved Thinking. Removed obsolete models URL; general prompt organization remains distinct from API history handling. |
| Z.ai GLM | [Thinking](https://docs.z.ai/guides/capabilities/thinking-mode), [function calling](https://docs.z.ai/guides/capabilities/function-calling), [structured output](https://docs.z.ai/guides/capabilities/struct-output) | GLM-5.3 and GLM-5.3-FLASH cannot disable thinking. Removed blanket mode-selection advice and old model-specific capability assumptions. |
| MiniMax | [Model invocation](https://platform.minimax.io/docs/guides/text-generation), [tool loops](https://platform.minimax.io/docs/guides/text-m3-function-call), [caching](https://platform.minimax.io/docs/api-reference/text-prompt-caching), [index](https://platform.minimax.io/docs/llms.txt) | Current M3.1-Flash may omit thinking on simple tool turns. Preserve full messages when integrating. The old prompting-tips URL returned 404; no replacement general prompt guide was verified. |
| AI21 Jamba | [Prompt engineering](https://docs.ai21.com/docs/prompt-engineering), [family](https://docs.ai21.com/docs/jamba-foundation-models) | Family page includes Jamba2 Mini and Jamba2 3B. Retained IDH and optional prompt elements; removed legacy endpoint/streaming claims from the general strategy. |
| Cohere | [Effective prompts](https://docs.cohere.com/docs/crafting-effective-prompts), [RAG](https://docs.cohere.com/docs/retrieval-augmented-generation-rag) | Corrected instructions-first guidance; use supported document inputs and returned citations in API integrations. |
| Amazon Nova | [General practices](https://docs.aws.amazon.com/nova/latest/nova2-userguide/prompting-best-practices.html), [precise prompts](https://docs.aws.amazon.com/nova/latest/nova2-userguide/create-precise-prompts.html) | Scope is Nova 2 text prompting. Media and speech have separate guides; removed mandatory enterprise framing. |
| Microsoft Phi | [Cookbook](https://github.com/microsoft/PhiCookBook), [Phi-4-reasoning card](https://huggingface.co/microsoft/Phi-4-reasoning) | Family includes distinct reasoning/instruction/media checkpoints. Removed universal small-window claims. Inference templates stay in the serving layer. |

## Retrieval limits and interpretation

- MiniMax's former `/docs/token-plan/prompting-best-practices` returned 404.
  The strategy labels its fallback as conservative organization plus verified API facts.
- The Gemini 3 developer page could not be fetched during this review. The successfully
  fetched general prompt-design page contains the Gemini 3 section used here; the
  strategy cites that page rather than claiming the unavailable page was checked.
- Kimi's former `/docs/guide/models` and the K3.1 Pro quickstart were unavailable to
  the web fetcher. The official index and successfully fetched thinking guide establish
  the model-specific statements retained here.
- Native API documentation sometimes exposes reasoning history for transport. Preserving
  returned fields is not a request to reveal or synthesize private reasoning.
- A live link check establishes reachability only. It cannot prove that a redirected
  page still supports the associated claim; review the page content on future updates.

## Installation sources

- [Codex skills](https://learn.chatgpt.com/docs/build-skills): filesystem discovery.
- [Claude Code skills](https://code.claude.com/docs/en/skills): personal skills and
  account-synced skills have separate locations and name-resolution rules.
- [Claude account skills](https://support.claude.com/en/articles/12512180-use-skills-in-claude):
  upload the skill folder as ZIP through Customize → Skills. Desktop account state
  must be checked separately from local Claude Code files.

## Validation boundaries

Repository tests, source review, and the [scenario review](refinement-scenarios.md)
do not measure output-quality uplift on all models. Existing A/B results remain historical;
the updated strategies require new live evaluations before any new performance claim.

For future maintenance, inspect the current official index, fetch the specific page,
record the date and model scope, then run repository checks. Do not bump version names
solely because an unverified search result calls them "latest".
