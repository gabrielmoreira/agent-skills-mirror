---
applyTo: "**"
---

# Codebase — Regras para uso de `docs/lorebase/*.md`

## Fonte oficial

- `docs/lorebase/*.md` é a referência técnica verificada do projeto para o Copilot.
- Esses documentos refletem o que foi verificado no código — não intenções ou planos.

## Antes de mudanças relevantes

Durante o step `brainstorming`, consulte apenas o(s) documento(s) de `docs/lorebase/` específico(s) para o tema da mudança:

| Tema da mudança | Documento |
|----------------|-----------|
| Linguagem, runtime, libs, ferramentas, package manager | `STACK.md` |
| Estrutura de pastas, módulos, organização de arquivos | `STRUCTURE.md` |
| Padrões, decisões arquiteturais, camadas do sistema | `ARCHITECTURE.md` |
| Convenções de código, nomenclatura, estilo | `CONVENTIONS.md` |
| APIs externas, serviços, dependências de terceiros | `INTEGRATIONS.md` |
| Estratégia de testes, cobertura, ferramentas de teste | `TESTING.md` |
| Riscos, dívidas técnicas, alertas | `CONCERNS.md` |

Não carregue todos os sete documentos por padrão — carregue apenas o(s) documento(s) diretamente relacionado(s) à categoria da mudança, conforme a tabela acima.

## Quando o código contradisser a documentação

Siga esta sequência:

1. Não corrija `docs/lorebase/*.md` diretamente.
2. Registre um sinal em `docs/lorebase/learn/inbox.md` com evidência verificável no código.
3. Avise o desenvolvedor sobre a divergência encontrada.
4. Aguarde: somente `/learn-update` pode promover sinais para os documentos oficiais.
