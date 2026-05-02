# Instruções globais do repositório para o GitHub Copilot

## Idioma

- Responda sempre em pt-BR.
- Mantenha termos técnicos, código, comandos, nomes de arquivos, APIs, libs, frameworks, padrões, logs e mensagens de erro em inglês quando for mais preciso.

## Conhecimento do codebase

- Antes de planejar mudanças relevantes, consulte o documento de `docs/codebase/` mais específico para o tema — não carregue todos os sete por padrão.
- Veja o mapeamento em `.github/instructions/codebase.instructions.md`.
- Se o código contradizer a documentação, não corrija diretamente: registre um sinal em `docs/codebase/learn/inbox.md`.

## Fluxo de trabalho

- Use o fluxo Superpowers para tarefas de implementação: `brainstorming` → `writing-plans` → `executing-plans` → `test-driven-development` → `requesting-code-review` → `finishing-a-development-branch`.
- Use a skill `learn-capture` quando encontrar aprendizado que possa atualizar `docs/codebase/*.md`.
- Não altere `docs/codebase/*.md` diretamente, exceto quando estiver executando a skill `learn-update`.
