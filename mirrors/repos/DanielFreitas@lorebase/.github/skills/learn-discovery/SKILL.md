---
name: learn-discovery
description: Orquestra acquire-codebase-knowledge para bootstrap ou redescoberta do conhecimento do codebase
---

# learn-discovery

Skill de orquestração. Usa `acquire-codebase-knowledge` (instalada em `.github/skills/acquire-codebase-knowledge/`) para criar ou comparar o conhecimento técnico do projeto.

## Determinação do modo

Execute em modo **bootstrap** se **qualquer um** dos sete arquivos abaixo estiver ausente ou vazio:

```
docs/lorebase/STACK.md
docs/lorebase/STRUCTURE.md
docs/lorebase/ARCHITECTURE.md
docs/lorebase/CONVENTIONS.md
docs/lorebase/INTEGRATIONS.md
docs/lorebase/TESTING.md
docs/lorebase/CONCERNS.md
```

Se todos os sete existirem com conteúdo → execute em modo **redescoberta**.

Se modo **bootstrap** → leia e execute [`modes/bootstrap.md`](modes/bootstrap.md).
Se modo **redescoberta** → leia e execute [`modes/rediscovery.md`](modes/rediscovery.md).
