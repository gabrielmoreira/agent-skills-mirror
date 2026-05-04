---
applyTo: "**"
---

# Superpowers — Regras de fluxo de trabalho

## Durante qualquer fase

Use `learn-capture` imediatamente quando:
- Um subagente reportar `DONE_WITH_CONCERNS`
- Um code reviewer apontar comportamento inesperado de biblioteca, ambiente ou API
- Uma decisão de implementação divergir do que foi especificado no design
- A etapa de verificação revelar comportamento inesperado da stack ou do ambiente

Não acumule aprendizados técnicos para depois — capture no momento em que aparecem.

## Regras intra-task

Ao usar `subagent-driven-development`: se o implementador retornar `DONE_WITH_CONCERNS`, use `learn-capture` antes de despachar o revisor de spec.

## Ordem de trabalho

Use as skills do Superpowers digitando o nome no chat em modo Agent. Execute cada step em ordem e conclua-o antes de avançar para o próximo:

1. `brainstorming` — entender a tarefa antes de planejar; consulte o(s) documento(s) relevante(s) de `docs/lorebase/` antes de propor qualquer direção; se nenhum documento relevante existir, prossiga com conhecimento geral ou peça esclarecimento ao desenvolvedor
2. `writing-plans` — criar plano executável com tarefas e riscos explícitos
3. `executing-plans` ou `subagent-driven-development` — executar
4. `test-driven-development` + `verification-before-completion` — verificar antes de declarar pronto
5. `learn-capture` — checkpoint obrigatório: houve `DONE_WITH_CONCERNS`, comportamento inesperado de biblioteca/ambiente, ou divergência de design? Se sim, registre agora antes de avançar
6. `requesting-code-review` — ao concluir; `receiving-code-review` ao receber feedback
7. `finishing-a-development-branch` — ao finalizar o trabalho
