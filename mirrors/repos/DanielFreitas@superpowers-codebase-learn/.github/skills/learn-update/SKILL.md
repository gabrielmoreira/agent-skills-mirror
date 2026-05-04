---
name: learn-update
description: Valida sinais do inbox e promove para docs/lorebase/*.md apenas com evidência verificável
---

# learn-update

Skill de consolidação. Lê o inbox, valida cada sinal contra o código atual e atualiza `docs/lorebase/*.md` apenas quando há evidência verificável.

## Quando usar

- Fim de sprint ou ciclo de desenvolvimento
- Quando o inbox acumular 5 ou mais sinais
- Antes de onboarding de novo desenvolvedor
- Após mudanças arquiteturais significativas no projeto

---

## Fluxo

Execute as fases na ordem abaixo. Cada uma está detalhada em `phases/`:

1. [`phases/1-inbox.md`](phases/1-inbox.md) — Leitura do inbox
2. [`phases/2-validation.md`](phases/2-validation.md) — Validação de cada sinal
3. [`phases/3-conflicts.md`](phases/3-conflicts.md) — Detecção de conflitos
4. [`phases/4-classify.md`](phases/4-classify.md) — Classificação e confirmação humana por sinal
5. [`phases/5-promote.md`](phases/5-promote.md) — Promoção dos sinais aprovados
6. [`phases/6-changelog.md`](phases/6-changelog.md) — Registro no changelog
7. [`phases/7-inbox-update.md`](phases/7-inbox-update.md) — Atualização de status no inbox

---

## Regras

- Nunca promova sem evidência verificável no código atual.
- Nunca altere mais de um conceito distinto por edição de arquivo.
- Sempre registre no changelog antes de atualizar o inbox.
- Se o inbox estiver vazio ou todos os sinais já tiverem status, informe ao desenvolvedor e encerre.


