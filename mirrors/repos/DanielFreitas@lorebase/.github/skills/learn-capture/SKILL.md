---
name: learn-capture
description: Captura sinais de aprendizado relevantes durante o fluxo do Superpowers para revisão futura
---

# learn-capture

Skill leve de captura. Registra um sinal em `docs/lorebase/learn/inbox.md` quando um aprendizado observado durante o trabalho pode afetar `docs/lorebase/*.md`.

## Quando usar

Use durante qualquer fase do Superpowers ao observar:

- Convenção real que contradiz ou complementa `docs/lorebase/CONVENTIONS.md`
- Padrão de arquitetura não documentado em `docs/lorebase/ARCHITECTURE.md`
- Integração externa não registrada em `docs/lorebase/INTEGRATIONS.md`
- Abordagem de teste diferente de `docs/lorebase/TESTING.md`
- Tecnologia ou lib não registrada em `docs/lorebase/STACK.md`
- Risco ou dívida não listada em `docs/lorebase/CONCERNS.md`
- Estrutura de diretório não refletida em `docs/lorebase/STRUCTURE.md`

## Filtro de relevância

**Capture:**
- Aprendizado que pode corrigir ou complementar `docs/lorebase/*.md`
- Padrão verificável no código atual

**Não capture:**
- Bug pontual sem impacto na documentação
- Tarefa ou TODO pendente
- Preferência pessoal do desenvolvedor
- Decisão ainda não implementada ou validada
- Anotação genérica sem evidência no código

## Processo

1. Identifique qual arquivo de `docs/lorebase/*.md` seria afetado.
2. Localize a evidência no código (arquivo, linha, configuração, teste).
3. Se não houver evidência verificável, não capture — apenas avise o desenvolvedor.
4. Adicione ao final de `docs/lorebase/learn/inbox.md`:

```markdown
## [YYYY-MM-DD] Captura durante [fase]

- **Arquivo afetado**: docs/lorebase/NOME.md
- **Seção**: nome da seção
- **Observação**: o que foi encontrado
- **Evidência**: caminho/arquivo e trecho que comprova
- **Ação sugerida**: corrigir / complementar / adicionar
- **Confiança**: HIGH / MEDIUM / LOW
```

**Critérios de confiança:**

| Nível | Quando usar |
|-------|-------------|
| `HIGH` | Evidência direta e inequívoca: configuração explícita, teste, implementação confirmada |
| `MEDIUM` | Evidência indireta: convenção inferida de múltiplos arquivos, padrão recorrente |
| `LOW` | Evidência circunstancial: padrão parece existir mas não foi confirmado diretamente |

5. Confirme ao desenvolvedor que o sinal foi registrado com a localização da evidência.

## Regras

- Só escreve em `docs/lorebase/learn/inbox.md`.
- Nunca altera `docs/lorebase/*.md` diretamente.
- Um sinal por observação distinta — não agrupe múltiplas observações em um sinal.
- Sempre inclua evidência verificável. Sem evidência, não capture.

## Cadeia

Os sinais capturados aqui são consumidos pela skill `learn-update`, que valida e promove para `docs/lorebase/*.md`.
Use a skill `learn-discovery` para detectar divergências estruturais que esta skill não cobre.
