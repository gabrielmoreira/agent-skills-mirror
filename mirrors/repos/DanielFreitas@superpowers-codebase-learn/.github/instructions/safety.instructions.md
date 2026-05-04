---
applyTo: "**"
---

# Safety — Regras de segurança para agentes de IA

## Ações irreversíveis — sempre pedir confirmação

Antes de executar qualquer ação das categorias abaixo, siga esta sequência:

1. **Pare** — não execute a ação.
2. **Descreva** ao desenvolvedor exatamente o que seria feito e por quê.
3. **Aguarde confirmação explícita** antes de prosseguir.
4. **Se não houver resposta**, não prossiga — registre a ação pendente para revisão posterior.

| Categoria | Exemplos — requer confirmação |
|-----------|-------------------------------|
| Comandos de terminal destrutivos | `rm -rf` com `-f` em diretórios, `git reset --hard`, `git clean -fd`, `git push --force`, `DROP TABLE`, `DROP DATABASE`, `TRUNCATE`, `kubectl delete`, `terraform destroy` |
| Arquivos protegidos | `.env`, `.env.*`, `*.env`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, arquivos com `secret`, `credential`, `password` ou `token` no nome, configs de infraestrutura de produção |
| Commits e push | Push direto em `main` ou `master`; incluir secrets, tokens, senhas ou chaves em conteúdo de commit |

## Princípio geral

Se desfazer a ação exigir uma intervenção que afete o histórico compartilhado (ex: novo commit forçado, rebase publicado) ou um sistema externo (ex: deploy, banco de dados, infraestrutura), ela exige confirmação antes de ser executada.

Em caso de dúvida sobre se uma ação é irreversível ou pode afetar a segurança de dados ou sistemas compartilhados: **pare, descreva o que faria, e aguarde instrução.**
