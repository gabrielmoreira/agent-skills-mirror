<!-- managed-by: lorebase -->
# Instruções globais do repositório para o GitHub Copilot

## Idioma

- Responda em pt-BR como idioma principal.
- Use inglês somente para termos técnicos usados como padrão no ecossistema e sem tradução oficial estável em pt-BR (ex.: `pull request`, `commit`, `runtime`, `stack trace`) e para artefatos técnicos literais (código, comandos, nomes de arquivos, APIs, libs, frameworks, padrões, logs e mensagens de erro).

## Conhecimento do codebase

- Regra 1: antes de planejar mudanças relevantes, consulte apenas o(s) documento(s) de `docs/lorebase/` diretamente relacionado(s) ao tema da mudança.
- Regra 2: considere como relacionados os documentos explicitamente citados na solicitação; se não houver citação explícita, use o mapeamento em `.github/instructions/lorebase.instructions.md`.
- Regra 3: carregue todos os sete documentos em `docs/lorebase/` somente se o desenvolvedor pedir explicitamente.
- Regra 4: se a solicitação do desenvolvedor estiver ambígua ou incompleta, peça esclarecimento antes de prosseguir e liste todos os dados faltantes necessários para continuar, priorizando: objetivo da mudança, módulo/arquivo afetado, escopo e critério de sucesso.
- Regra 5: se a solicitação do desenvolvedor estiver clara, mas o mapeamento em `.github/instructions/lorebase.instructions.md` estiver incompleto, ambíguo ou contraditório, priorize a solicitação do desenvolvedor e peça confirmação explícita do escopo documental antes de continuar.
- Regra 6: se o código contradizer a documentação, não corrija diretamente; registre um sinal em `docs/lorebase/learn/inbox.md`.

## Fluxo de trabalho

1. Em tarefas de implementação, siga o fluxo Superpowers: `brainstorming` → `writing-plans` → `executing-plans` → `test-driven-development` → `requesting-code-review` → `finishing-a-development-branch`.
2. Acione `learn-capture` quando ocorrer qualquer um destes gatilhos:
	- Um subagente reportar `DONE_WITH_CONCERNS`.
	- Um code reviewer apontar comportamento inesperado de biblioteca ou ambiente.
	- Uma implementação divergir do design especificado.
	- A verificação revelar comportamento inesperado da stack.
3. Para `docs/lorebase/*.md`, aplique as regras em ordem:
	- Só altere diretamente quando estiver executando `learn-update` ou `learn-discovery` (bootstrap).
	- Fora desses dois fluxos, não altere diretamente; registre sinal em `docs/lorebase/learn/inbox.md`.
	- Quando a alteração for permitida, escreva conteúdo em pt-BR e mantenha em inglês apenas nomes de arquivos, caminhos, comandos, versões, nomes de libs/frameworks e trechos de código.
