# Writing Guidelines for Iris Rules

Guidelines for creating effective Iris best practice rules for AI agents and LLMs.

## Key Principles

### 1. Concrete Patterns

Show exact code/command transformations. Avoid abstract advice.

**Good:** "Use `iris setup --foo` instead of `iris init` for X"
**Bad:** "Configure Iris correctly"

### 2. Problem-First Structure

Show the correct pattern first, then the incorrect one. This helps agents understand what to do and what to avoid.

```markdown
**Correct:** Description of good approach.

[good example]

**Incorrect:** Description of problematic approach.

[bad example]
```

### 3. Practical Impact

Include specific benefits. Helps agents prioritize.

**Good:** "10x faster setup", "Eliminates restart loop", "Avoids data loss"
**Bad:** "Faster", "Better", "More efficient"

### 4. Complete Examples

Examples should be runnable or close to it.

### 5. Semantic Naming

Use meaningful names. Names carry intent for LLMs.

---

## Code Standards

### Language Tags

- `bash` - CLI commands and shell scripts
- `python` - Python examples
- `javascript` - Node.js examples
- `yaml` - Configuration files

### Comments

- Explain _why_, not _what_
- Highlight pitfalls and gotchas
- Point out common mistakes

---

## Impact Levels

| Level | Improvement | Examples |
|-------|-------------|----------|
| **HIGH** | 5-100x or critical | Misconfiguration, security issues, blocking setup |
| **MEDIUM** | 2-5x | Suboptimal patterns, missing best practices |
| **LOW** | Incremental | Advanced patterns, edge cases |

---

## Review Checklist

Before submitting a rule:

- [ ] Title is clear and action-oriented
- [ ] Impact level matches the benefit
- [ ] impactDescription includes quantification
- [ ] Has at least 1 **Correct** example
- [ ] Has at least 1 **Incorrect** example (or `When to use` / `When NOT needed`)
- [ ] Code uses semantic naming
- [ ] Comments explain _why_
- [ ] Reference links included
