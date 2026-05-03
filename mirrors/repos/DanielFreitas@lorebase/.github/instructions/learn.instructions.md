---
applyTo: "**"
---

# Learn — Governança do conhecimento do codebase

## Regras fundamentais

- `docs/lorebase/*.md` é a fonte oficial. Nunca altere diretamente fora do `/learn-update`.
- `docs/lorebase/learn/inbox.md` é fila de sinais — não é verdade oficial.

## Fluxos permitidos

| Fluxo | O que faz | Onde escreve |
|-------|-----------|--------------|
| `/learn-capture` | Captura sinal durante implementação | `docs/lorebase/learn/inbox.md` |
| `/learn-discovery` (bootstrap) | Cria os sete documentos pela primeira vez | `docs/lorebase/*.md` |
| `/learn-discovery` (redescoberta) | Compara código com docs e registra divergências | `docs/lorebase/learn/inbox.md` |
| `/learn-update` | Valida e promove sinais do inbox | `docs/lorebase/*.md` + `changelog.md` |

## O que é proibido

- Editar `docs/lorebase/*.md` diretamente em resposta a uma tarefa de implementação.
- Promover sinais sem evidência verificável no código.
- Sobrescrever `docs/lorebase/*.md` em modo redescoberta do `/learn-discovery`.
