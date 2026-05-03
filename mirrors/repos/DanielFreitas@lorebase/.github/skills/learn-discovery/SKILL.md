---
name: learn-discovery
description: Orquestra acquire-codebase-knowledge para bootstrap ou redescoberta do conhecimento do codebase
---

# learn-discovery

Skill de orquestração. Usa `acquire-codebase-knowledge` para criar ou comparar o conhecimento técnico do projeto.

## Determinação do modo

Execute em modo **bootstrap** se **qualquer um** dos arquivos abaixo estiver ausente ou vazio:

```
docs/lorebase/STACK.md
docs/lorebase/STRUCTURE.md
docs/lorebase/ARCHITECTURE.md
docs/lorebase/CONVENTIONS.md
docs/lorebase/INTEGRATIONS.md
docs/lorebase/TESTING.md
docs/lorebase/CONCERNS.md
docs/lorebase/learn/inbox.md
docs/lorebase/learn/changelog.md
```

Se todos existirem com conteúdo → execute em modo **redescoberta**.

---

## SKILL_ROOT

O caminho para a skill `acquire-codebase-knowledge` é sempre relativo à raiz do projeto:

```
.github/skills/acquire-codebase-knowledge
```

Ao invocar o script de varredura, use:

```bash
python3 .github/skills/acquire-codebase-knowledge/scripts/scan.py --output docs/lorebase/.codebase-scan.txt
```

Esse caminho funciona em Windows, macOS e Linux, desde que o comando seja executado na raiz do projeto.

---

## Modo bootstrap

**Quando usar:** primeira execução no projeto.

**Processo:**

1. Execute a skill `acquire-codebase-knowledge` completamente usando o caminho acima como `$SKILL_ROOT`.
2. Crie os sete documentos oficiais de conhecimento em `docs/lorebase/`:

   ```
   STACK.md  STRUCTURE.md  ARCHITECTURE.md  CONVENTIONS.md
   INTEGRATIONS.md  TESTING.md  CONCERNS.md
   ```

   Adicione no topo de cada documento criado o seguinte header de staleness:

   ```markdown
   <!-- last-validated: [YYYY-MM-DD] [COMMIT-HASH] -->
   ```

   **Diretriz de tamanho:** esses docs são guias rápidos para IA — contexto mínimo necessário para gerar código alinhado, não documentação completa. Ao escrever, questione: toda a informação é essencial? A IA precisa disso para gerar um serviço? Prefira:
   - Termos específicos com versões e caminhos reais, não descrições vagas
   - 1-2 trechos de código real para illustrar convenções (especialmente em `CONVENTIONS.md`)
   - Antipadrões explícitos junto dos padrões recomendados
   - Omitir casos extremos raramente relevantes

   > A raiz de `docs/lorebase/` pode conter outros arquivos além desses sete — em particular `docs/lorebase/learn/` (metadados de manutenção) e `docs/lorebase/.codebase-scan.txt` (saída do script de scan). Esses não são documentos oficiais de contexto e não devem ser confundidos com os sete acima.
3. Crie `docs/lorebase/learn/inbox.md` usando o formato "Cabeçalho inicial do inbox" em `FORMATS.md`.

4. Crie `docs/lorebase/learn/changelog.md` usando o formato "Entrada inicial do changelog" em `FORMATS.md`.

   > `FORMATS.md` fica em `.github/skills/learn-update/FORMATS.md`.

5. Confirme ao desenvolvedor os arquivos criados.

---

## Modo redescoberta

**Quando usar:** execuções futuras para detectar divergências.

**Atenção:** em redescoberta, o `acquire-codebase-knowledge` é usado apenas como **referência metodológica** — não como executor de escrita. Não invoque o fluxo completo da skill.

Use apenas:
- o script de scan: `python3 .github/skills/acquire-codebase-knowledge/scripts/scan.py`
- os templates em `assets/templates/` como referência de comparação
- os inquiry checkpoints como guia de investigação
- os critérios de evidência definidos na skill

**Não escreva em `docs/lorebase/*.md`.** A única saída permitida é `docs/lorebase/learn/inbox.md`.

**Processo:**

1. Execute o script de scan para obter o estado atual do projeto.
2. Verifique o header `<!-- last-validated: -->` de cada um dos sete documentos:
   - Se um doc não tiver o header → marque como **sem histórico de validação**.
   - Se o commit registrado no header estiver mais de 20 commits atrás do HEAD atual → marque como **potencialmente desatualizado**.
   - Informe ao desenvolvedor quais docs estão nessas situações antes de prosseguir.
3. Para cada um dos sete documentos em `docs/lorebase/*.md`, compare:
   - O que o código atual revela sobre aquele tema
   - O que está documentado atualmente
3. Para cada divergência relevante encontrada, registre um sinal em `docs/lorebase/learn/inbox.md`:

```markdown
## [YYYY-MM-DD] Sinal de redescoberta

- **Arquivo afetado**: docs/lorebase/NOME.md
- **Seção**: nome da seção
- **Observação**: o que foi encontrado no código
- **Divergência**: como difere do doc atual
- **Evidência**: arquivo(s) ou trecho(s) que comprovam
```

4. **Não sobrescreva** `docs/lorebase/*.md`.
5. Divergências relevantes encontradas devem ser registradas como sinais usando o formato da skill `learn-capture`. O consolidador final desses sinais é a skill `learn-update`.
6. Informe ao desenvolvedor quantos sinais foram registrados e em quais arquivos.

---

## Regras

- Em modo redescoberta, nunca altere `docs/lorebase/*.md` diretamente.
- Somente `/learn-update` pode promover sinais para os documentos oficiais.
- Registre sempre a data e a evidência em cada sinal.
- Se não houver divergências, informe que os documentos parecem atualizados.
