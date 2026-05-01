# Contextação — Output

## Subject Analyzed
> [describe the subject/task]

## Phase 0 — Triage
**Complexity**: Simple / Medium / Complex
**Justification**: [objective criteria that led to the classification]

---

## Phase 1 — Decomposition

### Assumptions — *"What am I treating as fact without evidence?"*
| # | Assumed premise | Verified? | Risk if false |
|---|-----------------|-----------|---------------|
| 1 | | | |

### Scope — *"What is in, out, and undefined?"*
- **Included**: 
- **Excluded**: 
- **Ambiguous**: 

### Dependencies — *"What needs to exist for the solution to work?"*
| Dependency | Type | Version/State | Staleness risk |
|------------|------|---------------|----------------|
| | | | |

### Sources of Truth — *"Where does the knowledge come from and is it reliable?"*
| Required knowledge | Source | Confidence | Action |
|-------------------|--------|------------|--------|
| | | 🟢/🟡/🔴 | |

### Failure Modes — *"How can this go wrong and what am I not seeing?"*
| # | Failure mode | Probability | Impact | Mitigation |
|---|-------------|-------------|--------|------------|
| 1 | | | | |

### Stakeholders — *"Who is affected and who decides?"*
| Who | Role | Needs to validate? |
|-----|------|--------------------|
| | | |

---

## Phase 2 — Confidence Classification

> ⚠️ Model estimate. LLMs tend to be overconfident. Always validate with a human before high-impact decisions.

| Axis | Confidence | Justification | Tools used |
|------|------------|---------------|------------|
| Assumptions | 🟢/🟡/🔴 | | |
| Scope | 🟢/🟡/🔴 | | |
| Dependencies | 🟢/🟡/🔴 | | |
| Sources of Truth | 🟢/🟡/🔴 | | |
| Failure Modes | 🟢/🟡/🔴 | | |
| Stakeholders | 🟢/🟡/🔴 | | |

> **Tool evidence rule**: For axes classified as 🟡 or 🔴, list the actual tool calls used to research before accepting the classification. Format: `tool_name("argument")` — e.g., `grep_search("auth pattern")`, `read_file("src/auth.ts#L1-50")`, `fetch_webpage("https://docs.example.com")`. For 🟢 axes, tools column may be `—` (no research needed). **The anti-hallucination hook validates listed tools against the session transcript.**

**Overall confidence**: 🟢/🟡/🔴

---

## Phase 3 — Action Plan

### Questions for the User (MANDATORY)
> Every analysis MUST generate at least 1 question. If there are no questions, the analysis was shallow.

1. 

### Can be done now (high confidence)
- 

### Needs external consultation
| What | Where to look |
|------|--------------|
| | |

### Needs human validation
- 

### Do NOT do yet
- 

---

## Phase 4 — Transparency

**Unverified assumptions**:
- 

**Limitations of this analysis**:
- 

**What was left out and why**:
- 

---

## Self-validation

- [ ] Pelo menos 1 premissa que, se falsa, invalida a abordagem?
- [ ] Pelo menos 1 eixo 🟡 ou 🔴?
- [ ] Pelo menos 1 pergunta ao usuário?
- [ ] Perguntas específicas ao contexto?
- [ ] Cada risco com consequência concreta?
- [ ] Declarou o que não sabe?

---

## Fase 5 — Feedback Loop (preencher após o usuário agir)

**Resultado da análise**: [acertou / parcial / errou]
**O que não foi previsto**: 
**Aprendizado (regra concisa)**:
**Eixo afetado**:
**Salvar como exemplo real em exemplos.md?**: Sim / Não
- 

**O que ficou de fora e por quê**:
- 
