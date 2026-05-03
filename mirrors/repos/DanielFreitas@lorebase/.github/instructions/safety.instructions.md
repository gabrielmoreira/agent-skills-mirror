---
applyTo: "**"
---

# Safety — Regras de segurança para agentes de IA

## Ações irreversíveis — sempre pedir confirmação

Antes de executar qualquer ação das listas abaixo, **pare e peça confirmação explícita** ao desenvolvedor. Descreva exatamente o que será feito e aguarde resposta antes de prosseguir.

### Comandos de terminal destrutivos

- `rm -rf` ou qualquer variante com `-f` em diretórios
- `git reset --hard`, `git clean -fd`, `git push --force`
- `DROP TABLE`, `DROP DATABASE`, `TRUNCATE`
- `kubectl delete`, `terraform destroy`
- Qualquer comando que apague, sobrescreva ou destrua dados em produção

### Arquivos protegidos — nunca editar sem confirmação

- `.env`, `.env.*`, `*.env`
- `*.pem`, `*.key`, `*.p12`, `*.pfx`
- Arquivos com `secret`, `credential`, `password`, `token` no nome
- Arquivos de configuração de infraestrutura de produção

### Commits e push

- Nunca incluir secrets, tokens, senhas ou chaves em conteúdo de commit
- Nunca fazer push direto em `main` ou `master` sem confirmação
- Se um arquivo parece conter credencial, não o inclua no commit — avise o desenvolvedor

## Princípio geral

Se uma ação não puder ser desfeita com um único comando simples (`git revert`, `Ctrl+Z`, restaurar backup), ela exige confirmação antes de ser executada.

Em caso de dúvida: **pare, descreva o que faria, e aguarde instrução.**
