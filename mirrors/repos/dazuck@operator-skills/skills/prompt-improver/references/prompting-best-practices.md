# Prompting Best Practices

## Core Principles

### 1. Clarity and Specificity

- Be clear about what you want the AI to do
- Provide context about the task's purpose and constraints
- Use concrete examples when applicable
- Avoid ambiguous language

### 2. Strategic Structure

- Put instructions at the beginning or end (recency bias)
- Separate instructions from content using XML tags or delimiters
- Break complex tasks into smaller steps
- Use headings and structure to organize information

### 3. Leverage AI Strengths

- Trust the model's intelligence - don't over-specify when flexibility is better
- Avoid rigid scoring rubrics unless truly needed for consistency
- Let the AI reason and make judgments rather than forcing mechanical processes

## Effective Techniques

### Persona Assignment

Assign relevant expertise or perspective:

- "You are an expert [role] with [qualifications]"
- "You approach this task as [perspective]"
- Only use when the persona genuinely helps with the task

### Examples and Demonstrations

- Provide 1-3 examples of desired input/output
- Use XML tags to clearly separate examples from instructions
- Show both positive examples (do this) and negative examples (not this)

### Step-by-Step Reasoning

- Ask the AI to think through problems step by step
- Use phrases like "Think through this step by step" or "Explain your reasoning"
- For complex tasks, explicitly structure the reasoning process

### Output Formatting

- Specify desired format clearly (markdown, JSON, XML, etc.)
- Use XML tags to structure complex outputs
- Provide a template or schema when consistency matters

### Encouragement and Stakes

- Add phrases like "This is very important" for critical tasks
- "Take your time and think carefully"
- "You're excellent at this type of task"
- Explain why the task matters (but don't overdo it)

### Context and Constraints

- Provide relevant background information
- Specify constraints (length, style, tone, audience)
- Mention what to avoid or exclude

## What to Avoid

### Over-Specification

- Detailed rubrics when judgment is better
- Mechanical checklists that stifle intelligence
- Rigid formulas that don't fit all cases
- Excessive structure that limits adaptability

### Redundancy

- Don't repeat the same instruction multiple times
- Trust that clear instructions will be followed
- Avoid over-explaining simple concepts

### Ambiguity

- Vague success criteria
- Unclear scope or boundaries
- Mixed or contradictory instructions

## Prompt Structure Template

```
[Optional: Role/Persona]
[Core Task Description]
[Context and Background]
[Specific Requirements and Constraints]
[Examples if helpful]
[Desired Output Format]
[Quality Criteria or Success Measures]
```

## Key Patterns

### Chain of Thought

Request explicit reasoning: "Before answering, think through: [aspects to consider]"

### Multi-Shot Learning

Provide 2-5 examples showing input → process → output

### Recursive Refinement

Ask for initial output, then request improvements: "Review your response and refine it"

### Conditional Logic

Use if/then structures: "If X, do Y; otherwise do Z"

### Prefilling

Start the AI's response with desired beginning: "Assistant: Here's a detailed analysis:"

## Quality Indicators

Good prompts typically:

- Have clear success criteria
- Balance specificity with flexibility
- Provide just enough context
- Use natural, conversational language
- Leverage AI strengths rather than constraining them
- Are easy to iterate and modify
