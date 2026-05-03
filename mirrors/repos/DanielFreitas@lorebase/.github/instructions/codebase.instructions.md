---
applyTo: "**"
---

# Codebase — Regras para uso de `docs/lorebase/*.md`

## Fonte oficial

- `docs/lorebase/*.md` é a referência técnica verificada do projeto para o Copilot.
- Esses documentos refletem o que foi verificado no código — não intenções ou planos.

## Antes de mudanças relevantes

Consulte apenas o(s) documento(s) de `docs/lorebase/` específico(s) para o tema da mudança:

| Tema da mudança | Documento |
|----------------|-----------|
| Linguagem, runtime, libs, ferramentas, package manager | `STACK.md` |
| Estrutura de pastas, módulos, organização de arquivos | `STRUCTURE.md` |
| Padrões, decisões arquiteturais, camadas do sistema | `ARCHITECTURE.md` |
| Convenções de código, nomenclatura, estilo | `CONVENTIONS.md` |
| APIs externas, serviços, dependências de terceiros | `INTEGRATIONS.md` |
| Estratégia de testes, cobertura, ferramentas de teste | `TESTING.md` |
| Riscos, dívidas técnicas, alertas | `CONCERNS.md` |

Não carregue todos os sete documentos por padrão — apenas os relevantes para a tarefa atual.

## Quando o código contradisser a documentação

- Não corrija `docs/lorebase/*.md` diretamente.
- Registre um sinal em `docs/lorebase/learn/inbox.md` com evidência.
- Avise o desenvolvedor sobre a divergência encontrada.
- Somente `/learn-update` pode promover sinais para os documentos oficiais.
