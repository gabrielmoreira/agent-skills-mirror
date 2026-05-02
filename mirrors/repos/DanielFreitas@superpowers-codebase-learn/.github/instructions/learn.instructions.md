---
applyTo: "**"
---

# Learn — Governança do conhecimento do codebase

## Regras fundamentais

- `docs/codebase/*.md` é a fonte oficial. Nunca altere diretamente fora do `/learn-update`.
- `docs/codebase/learn/inbox.md` é fila de sinais — não é verdade oficial.

## Fluxos permitidos

| Fluxo | O que faz | Onde escreve |
|-------|-----------|--------------|
| `/learn-capture` | Captura sinal durante implementação | `docs/codebase/learn/inbox.md` |
| `/learn-discovery` (bootstrap) | Cria os sete documentos pela primeira vez | `docs/codebase/*.md` |
| `/learn-discovery` (redescoberta) | Compara código com docs e registra divergências | `docs/codebase/learn/inbox.md` |
| `/learn-update` | Valida e promove sinais do inbox | `docs/codebase/*.md` + `changelog.md` |

## O que é proibido

- Editar `docs/codebase/*.md` diretamente em resposta a uma tarefa de implementação.
- Promover sinais sem evidência verificável no código.
- Sobrescrever `docs/codebase/*.md` em modo redescoberta do `/learn-discovery`.
