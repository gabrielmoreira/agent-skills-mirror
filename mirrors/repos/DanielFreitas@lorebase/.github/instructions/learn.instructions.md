---
applyTo: "**"
---

# Learn — Governança do conhecimento do codebase

## Regras fundamentais

- `docs/lorebase/*.md` é a fonte oficial. Nunca altere diretamente — somente via `/learn-update` ou `/learn-discovery` (bootstrap).
- `docs/lorebase/learn/inbox.md` é fila de sinais não validados — não deve ser tratado como documentação autoritária.
- Se um sinal contradizer a documentação existente, priorize o sinal somente se ele for diretamente suportado por evidência verificável no código.

## Fluxos permitidos

| Fluxo | O que faz | Onde escreve |
|-------|-----------|--------------|
| `/learn-capture` | Captura sinal durante qualquer fase do fluxo | `docs/lorebase/learn/inbox.md` |
| `/learn-discovery` (bootstrap) | Cria os sete documentos pela primeira vez | `docs/lorebase/*.md` |
| `/learn-discovery` (redescoberta) | Compara código com docs e registra divergências | `docs/lorebase/learn/inbox.md` |
| `/learn-update` | Valida e promove sinais do inbox | `docs/lorebase/*.md` + `changelog.md` |

## O que é proibido

- Editar `docs/lorebase/*.md` diretamente em resposta a uma tarefa de implementação.
- Promover sinais sem evidência verificável no código — como comentários, testes ou artefatos explícitos que suportem diretamente a alteração.
- Sobrescrever `docs/lorebase/*.md` em modo redescoberta do `/learn-discovery`.
