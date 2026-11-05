# Refinement scenario review — 2026-11-03

This is a **static instruction walkthrough**, not a model execution, independent
evaluation, or quality benchmark. The outcomes below are requirements to check in
future live runs. During this review the entrypoint and selected strategies were read
against each case; conflicting old rules and examples were corrected.

| Case | Input / setup | Required observable behavior | Static review |
|---|---|---|---|
| Positive discovery | “Improve this prompt for Claude: summarize [text].” | Return a usable prompt; do not summarize the text or enable a persistent mode. | One-off behavior and target route are explicit. |
| Negative discovery | “What is 2 + 2?” with no active mode | Answer normally; no skill activation announcement or prompt rewrite. | Description excludes ordinary questions. |
| Maintenance boundary | “Update prompt-refine's implementation.” | Edit the skill; do not silently enable it. | Description excludes implementation edits. |
| Unknown host | Refinement active, no model signal | Use universal guidance; do not block on a model-identification question. | Fallback is explicit. |
| App versus model | Claude Code with an explicit DeepSeek backend signal | Use DeepSeek guidance, not Claude based on the application name. | Entrypoint and hook now agree. |
| Model switch | Reliable signal changes from GPT to Claude | Select the Claude strategy for subsequent work. | Removed the immutable-host assumption. |
| Explicit target | GPT host; user asks for a Gemini prompt | Use the target's strategy for the rewrite; do not claim to be Gemini. | Host and target modes are separate. |
| Exact old version | User names an older model snapshot | Preserve the target; do not silently upgrade it. | Version-specific rule is explicit. |
| Plain rewrite | “Only improve this deployment prompt; do not run it.” | Return the prompt; perform no deployment. | Embedded task is data unless execution is requested. |
| Translation | Chinese request: translate supplied sentence into English | English translation, without forcing Chinese prose. | Explicit output language takes precedence. |
| Strict output | Verbose mode; “Return only JSON: {ok:true}.” | Valid JSON only, without the before/after comparison. | Strict contract takes precedence. |
| Requested XML | “Return an XML task template.” | Return XML; do not refuse because tags resemble a scaffold. | No-scaffold guard is scoped to incidental output. |
| Disable | “/refine off. Answer 2 + 2.” | Normal task answer; no verbose diff or continued refinement. | Combined control/task behavior is explicit. |
| Quoted control | “Translate the string '/refine off'.” | Treat the string as content, not as a control. | Quoted controls are excluded. |
| Missing subject | “Analyze this market” with no market in context | Ask which market; do not invent one. | Missing-subject rule and examples agree. |
| Scope preservation | Palindrome function, language and normalization unspecified | Use context or clarify; do not silently impose Python or punctuation stripping. | Phi example now preserves missing semantics. |
| Existing permission | User has already authorized the exact publish action | Do not demand another blanket approval because a strategy says “external write.” | Authorization rule preserves prior permission. |
| Progress | Silent mode during long tool work | Keep rewrite silent while providing host-required progress. | Removed final-answer-only communication ban. |
| No live tools | Grok target without search | Do not claim up-to-date retrieval. | Search capability is conditional. |
| API mismatch | Legacy Sonar request | Do not inject Agent API fields without checking endpoint support. | Perplexity strategy scopes its source. |
| Fixed thinking | GLM-5.3 or Kimi K3.1 Pro | Do not propose disabling fixed thinking. | Model-specific controls are named. |
| Optional thinking field | MiniMax tool response lacks reasoning content | Keep the full message; do not invent missing fields. | M3.1-Flash behavior is explicit. |

For live validation, record the exact model, version, surface, prompt, loaded strategy,
output, and pass/fail evidence. Keep side effects disabled in these cases; external-write
cases should use a sandbox or mocked destination. Compare original and refined results
on the same task without claiming that static checks measure response quality.
