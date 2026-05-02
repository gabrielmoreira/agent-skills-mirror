---
name: learn-update
description: Valida sinais do inbox e promove para docs/codebase/*.md apenas com evidência verificável
---

# learn-update

Skill de consolidação. Lê o inbox, valida cada sinal contra o código atual e atualiza `docs/codebase/*.md` apenas quando há evidência verificável.

## Quando usar

- Fim de sprint ou ciclo de desenvolvimento
- Quando o inbox acumular 5 ou mais sinais
- Antes de onboarding de novo desenvolvedor
- Após mudanças arquiteturais significativas no projeto

---

## Fase 1 — Leitura do inbox

Leia `docs/codebase/learn/inbox.md` integralmente.
Liste todos os sinais pendentes com seus arquivos afetados.

---

## Fase 2 — Validação de cada sinal

Para cada sinal, verifique:

1. **Evidência existe?** — O arquivo ou trecho citado existe e confirma o sinal?
2. **Sinal está atual?** — O código não foi alterado desde a captura de forma que invalide o sinal?
3. **Impacto real?** — O sinal realmente muda a compreensão técnica do projeto?

---

## Fase 3 — Detecção de conflitos

Antes de classificar, identifique sinais que **afetam o mesmo arquivo e seção** com observações contraditórias.

Para cada conflito detectado:

1. Apresente os sinais conflitantes ao desenvolvedor com a descrição de cada um.
2. Pergunte qual deve prevalecer, ou se ambos devem ser descartados.
3. Aguarde resposta antes de prosseguir com a classificação.
4. Registre a resolução como nota inline em cada sinal (formato em `FORMATS.md`).

**Não classifique sinais conflitantes sem resolução explícita do desenvolvedor.**

---

## Fase 4 — Classificação

Classifique cada sinal com uma das três classes:

| Classe | Critério | Ação |
|--------|----------|------|
| `PROMOVER` | Evidência verificada, sinal relevante e atual | Atualiza `docs/codebase/*.md` |
| `OBSERVAR` | Evidência parcial, incerta ou não verificada ainda | Mantém no inbox com nota |
| `DESCARTAR` | Sem evidência, obsoleto, irrelevante ou duplicado | Remove do inbox |

O campo `**Confiança**` do sinal serve como ponto de partida: sinais `LOW` devem ser tratados como `OBSERVAR` por padrão salvo verificação direta; sinais `HIGH` podem ser promovidos diretamente se a evidência ainda for válida.

**Em caso de dúvida, classifique como `OBSERVAR`, não como `PROMOVER`.**

---

## Fase 5 — Promoção dos sinais `PROMOVER`

Para cada sinal classificado como `PROMOVER`:

1. Abra o arquivo `docs/codebase/*.md` correspondente.
2. Localize a seção indicada no sinal.
3. **Antes de escrever, aplique o filtro de qualidade:**

   | Armadilha | Verificação |
   |-----------|-------------|
   | Conteúdo a adicionar é essencial para a IA gerar código? | Se não, omita. Documentação detalhada pode ficar em outro local. |
   | Conteúdo vago? ("boas práticas", "padrões modernos") | Substitua por termos específicos: versões, caminhos, exemplos reais. |
   | Promoção em `CONVENTIONS.md` sem exemplo de código? | Inclua 1-2 trechos reais do codebase. |
   | Sinal descreve o que fazer, mas não o que evitar? | Adicione o antipadrão correspondente quando aplicável. |

4. Adicione ou corrija a informação com base na evidência.
5. Mantenha o estilo e a estrutura existente do arquivo — não reformate o documento inteiro.
6. Não promova mais de um conceito distinto por edição.
7. Atualize o header `<!-- last-validated: -->` no topo do arquivo (formato em `FORMATS.md`).
   Se o header não existir, adicione-o como primeira linha do arquivo.

---

## Fase 6 — Registro no changelog

Adicione entrada em `docs/codebase/learn/changelog.md` usando o formato em `FORMATS.md`.

Após adicionar a nova entrada, verifique quantas entradas existem no arquivo. Se houver mais de 10, remova as mais antigas até manter apenas as 10 mais recentes.

---

## Fase 7 — Atualização de status no inbox

Atualize o status de cada sinal inline usando os formatos em `FORMATS.md`.

Após atualizar todos os status, apresente um resumo ao desenvolvedor e pergunte:

> "Todos os sinais foram processados. Deseja limpar o inbox agora? Isso vai apagar todos os sinais com status ✅ e ❌, mantendo apenas os ⏸ (observados). Os sinais promovidos já estão em `docs/codebase/*.md` e no `changelog.md`."

Se o desenvolvedor confirmar, reescreva `docs/codebase/learn/inbox.md` mantendo apenas:
- O cabeçalho original do arquivo
- Os sinais com status `⏸` (observados)

---

## Regras

- Nunca promova sem evidência verificável no código atual.
- Nunca altere mais de um conceito distinto por edição de arquivo.
- Sempre registre no changelog antes de atualizar o inbox.
- Se o inbox estiver vazio ou todos os sinais já tiverem status, informe ao desenvolvedor e encerre.

## Cadeia

O inbox processado por esta skill é alimentado pela skill `learn-capture` (sinais pontuais durante implementação)
e pela skill `learn-discovery` (divergências estruturais detectadas em redescobertas).
