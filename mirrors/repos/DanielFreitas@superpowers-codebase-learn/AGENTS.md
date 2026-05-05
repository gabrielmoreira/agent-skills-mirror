<!-- managed-by: lorebase -->
# Instruções para agentes de IA

Este arquivo é lido automaticamente por agentes como GitHub Copilot, Codex, Claude e outros que reconhecem `AGENTS.md` como ponto de entrada de instruções.

## Fonte de verdade técnica

A documentação técnica verificada do projeto vive em `docs/lorebase/`:

| Documento | Conteúdo |
|---|---|
| `STACK.md` | Linguagem, runtime, libs, ferramentas |
| `STRUCTURE.md` | Estrutura de pastas e módulos |
| `ARCHITECTURE.md` | Padrões e decisões arquiteturais |
| `CONVENTIONS.md` | Convenções de código e nomenclatura |
| `INTEGRATIONS.md` | APIs externas e serviços de terceiros |
| `TESTING.md` | Estratégia de testes e cobertura |
| `CONCERNS.md` | Riscos e dívidas técnicas |

Antes de planejar mudanças relevantes, consulte o documento mais específico para o tema — não carregue todos por padrão.

## Instruções detalhadas

As regras completas para este projeto vivem em `.github/instructions/`:

| Arquivo | Conteúdo |
|---|---|
| `lorebase.instructions.md` | Quando e como consultar `docs/lorebase/*.md` |
| `learn.instructions.md` | Governança da memória técnica — fluxos permitidos e proibidos |
| `safety.instructions.md` | Ações irreversíveis, arquivos protegidos, commits seguros |
| `superpowers.instructions.md` | Ordem de trabalho com as skills operacionais do agente |

## Fluxo de trabalho

Veja `.github/instructions/superpowers.instructions.md` para a ordem completa do fluxo.

Resumo: `brainstorming` → `writing-plans` → `executing-plans` → `test-driven-development` → `requesting-code-review` → `finishing-a-development-branch`.

Use `learn-capture` durante o trabalho e `learn-update` ao final de cada ciclo de manutenção do contexto.

## Regras de segurança

Veja `.github/instructions/safety.instructions.md` para as regras completas.

Resumo: confirme antes de qualquer ação irreversível (`rm -rf`, `DROP TABLE`, `git reset --hard`, push em `main`). Nunca inclua secrets em commits.

## Bootstrap do conhecimento

Se `docs/lorebase/` estiver vazio ou ausente, execute `/learn-discovery` no Copilot em modo Agent para gerar os documentos iniciais.
