# AGENTS.md

## Visão Geral do Projeto

Este é um repositório de currículo educativo para ensinar fundamentos do desenvolvimento web a iniciantes. O currículo é um curso abrangente de 12 semanas desenvolvido pelos Microsoft Cloud Advocates, apresentando 24 lições práticas que cobrem JavaScript, CSS e HTML.

### Componentes Principais

- **Conteúdo Educativo**: 24 lições estruturadas organizadas em módulos baseados em projetos
- **Projetos Práticos**: Terrarium, Jogo de Digitação, Extensão de Navegador, Jogo Espacial, Aplicação Bancária, Editor de Código e Assistente de Chat IA
- **Questionários Interativos**: 48 questionários com 3 perguntas cada (avaliações pré/pós-lição)
- **Suporte Multilíngue**: Traduções automáticas para mais de 50 idiomas via GitHub Actions
- **Tecnologias**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (para projetos de IA)

### Arquitetura

- Repositório educativo com estrutura baseada em lições
- Cada pasta de lição contém README, exemplos de código e soluções
- Projetos independentes em diretórios separados (quiz-app, vários projetos de lição)
- Sistema de tradução usando GitHub Actions (co-op-translator)
- Documentação servida via Docsify e disponível em PDF

## Comandos de Configuração

Este repositório destina-se principalmente ao consumo de conteúdo educativo. Para trabalhar com projetos específicos:

### Configuração Principal do Repositório

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Configuração do Quiz App (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Iniciar servidor de desenvolvimento
npm run build      # Construir para produção
npm run lint       # Executar ESLint
```

### API do Projeto Bancário (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Iniciar servidor API
npm run lint       # Executar ESLint
npm run format     # Formatar com Prettier
```

### Projetos de Extensão de Navegador

```bash
cd 5-browser-extension/solution
npm install
# Siga as instruções específicas do navegador para carregar extensões
```

### Projetos de Jogo Espacial

```bash
cd 6-space-game/solution
npm install
# Abra index.html no navegador ou use o Live Server
```

### Projeto de Chat (Backend em Python)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Definir variável de ambiente GITHUB_TOKEN
python api.py
```

## Fluxo de Trabalho de Desenvolvimento

### Para Contribuidores de Conteúdo

1. **Faça fork do repositório** na sua conta GitHub
2. **Clone o seu fork** localmente
3. **Crie uma nova branch** para as suas alterações
4. Faça alterações no conteúdo da lição ou nos exemplos de código
5. Teste quaisquer alterações de código nos diretórios de projeto relevantes
6. Submeta pull requests seguindo as diretrizes de contribuição

### Para Aprendizes

1. Faça fork ou clone o repositório
2. Navegue sequencialmente pelos diretórios das lições
3. Leia os ficheiros README de cada lição
4. Complete os quizzes pré-lição em https://ff-quizzes.netlify.app/web/
5. Trabalhe os exemplos de código nas pastas das lições
6. Complete trabalhos e desafios
7. Realize os quizzes pós-lição

### Desenvolvimento ao Vivo

- **Documentação**: Execute `docsify serve` na raiz (porta 3000)
- **Quiz App**: Execute `npm run dev` no diretório quiz-app
- **Projetos**: Use a extensão Live Server do VS Code para projetos HTML
- **Projetos API**: Execute `npm start` nos diretórios API respetivos

## Instruções de Teste

### Teste do Quiz App

```bash
cd quiz-app
npm run lint       # Verificar problemas de estilo de código
npm run build      # Verificar se a compilação é bem-sucedida
```

### Teste da API Bancária

```bash
cd 7-bank-project/api
npm run lint       # Verificar problemas de estilo de código
node server.js     # Verificar se o servidor inicia sem erros
```

### Abordagem Geral de Testes

- Este é um repositório educativo sem testes automatizados abrangentes
- O teste manual foca-se em:
  - Exemplos de código que executam sem erros
  - Links na documentação funcionam corretamente
  - Builds dos projetos completam com sucesso
  - Exemplos seguem as boas práticas

### Verificações Pré-Submissão

- Execute `npm run lint` nos diretórios com package.json
- Verifique que os links markdown são válidos
- Teste exemplos de código no navegador ou Node.js
- Confirme que as traduções mantêm a estrutura adequada

## Diretrizes de Estilo de Código

### JavaScript

- Use sintaxe moderna ES6+
- Siga as configurações padrão do ESLint fornecidas nos projetos
- Use nomes significativos de variáveis e funções para clareza educativa
- Adicione comentários explicativos para os conceitos
- Formate com Prettier onde estiver configurado

### HTML/CSS

- Elementos semânticos HTML5
- Princípios de design responsivo
- Convenções claras de nomeação de classes
- Comentários explicando técnicas CSS para aprendizes

### Python

- Diretrizes de estilo PEP 8
- Exemplos de código claros e educativos
- Anotações de tipo onde ajudarem na aprendizagem

### Documentação Markdown

- Hierarquia clara de títulos
- Blocos de código com especificação de linguagem
- Links para recursos adicionais
- Capturas de ecrã e imagens nas pastas `images/`
- Texto alternativo para imagens para acessibilidade

### Organização de Ficheiros

- Lições numeradas sequencialmente (1-getting-started-lessons, 2-js-basics, etc.)
- Cada projeto tem diretórios `solution/` e frequentemente `start/` ou `your-work/`
- Imagens guardadas nas pastas `images/` específicas da lição
- Traduções em estrutura `translations/{language-code}/`

## Construção e Implementação

### Deploy do Quiz App (Azure Static Web Apps)

O quiz-app está configurado para deploy em Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Cria a pasta dist/
# Faz o deploy através do fluxo de trabalho do GitHub Actions ao fazer push para a main
```

Configuração Azure Static Web Apps:
- **Localização da app**: `/quiz-app`
- **Localização de saída**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Geração de PDF da Documentação

```bash
npm install                    # Instalar docsify-to-pdf
npm run convert               # Gerar PDF a partir do docs
```

### Documentação Docsify

```bash
npm install -g docsify-cli    # Instalar Docsify globalmente
docsify serve                 # Servir em localhost:3000
```

### Builds Específicos por Projeto

Cada diretório de projeto pode ter seu próprio processo de build:
- Projetos Vue: `npm run build` cria bundles para produção
- Projetos estáticos: Sem etapa de build, servir ficheiros diretamente

## Diretrizes para Pull Requests

### Formato do Título

Use títulos claros e descritivos indicativos da área de alteração:
- `[Quiz-app] Adicionar novo quiz para lição X`
- `[Lesson-3] Corrigir erro tipográfico no projeto terrarium`
- `[Translation] Adicionar tradução para espanhol na lição 5`
- `[Docs] Atualizar instruções de configuração`

### Verificações Necessárias

Antes de submeter um PR:

1. **Qualidade do Código**:
   - Execute `npm run lint` nos diretórios de projeto afetados
   - Corrija todos os erros e avisos de lint

2. **Verificação do Build**:
   - Execute `npm run build` se aplicável
   - Garanta ausência de erros no build

3. **Validação de Links**:
   - Teste todos os links markdown
   - Verifique referências de imagens

4. **Revisão de Conteúdo**:
   - Revise ortografia e gramática
   - Confirme que os exemplos de código estão corretos e educativos
   - Verifique que as traduções mantêm o significado original

### Requisitos de Contribuição

- Concordar com o CLA da Microsoft (verificação automática no primeiro PR)
- Seguir o [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- Consultar [CONTRIBUTING.md](./CONTRIBUTING.md) para diretrizes detalhadas
- Referenciar números de issues na descrição do PR, se aplicável

### Processo de Revisão

- PRs revistos por mantenedores e comunidade
- Clareza educativa é prioridade
- Exemplos de código devem seguir as melhores práticas atuais
- Traduções revisadas quanto a exatidão e adequação cultural

## Sistema de Tradução

### Tradução Automática

- Usa GitHub Actions com workflow co-op-translator
- Traduz para mais de 50 idiomas automaticamente
- Ficheiros fonte nos diretórios principais
- Ficheiros traduzidos em `translations/{language-code}/`

### Adição de Melhorias Manuais de Tradução

1. Localize o ficheiro em `translations/{language-code}/`
2. Faça melhorias preservando a estrutura
3. Garanta que exemplos de código permanecem funcionais
4. Teste qualquer conteúdo de quizzes localizado

### Metadados de Tradução

Ficheiros traduzidos incluem cabeçalho de metadados:
```markdown
<!--
CO_OP_TRANSLATOR_METADATA:
{
  "original_hash": "...",
  "translation_date": "...",
  "source_file": "...",
  "language_code": "..."
}
-->
```

## Depuração e Resolução de Problemas

### Problemas Comuns

**App do Quiz não inicia**:
- Verifique a versão do Node.js (recomendado v14+)
- Apague `node_modules` e `package-lock.json`, execute `npm install` novamente
- Verifique conflitos de porta (padrão: Vite usa porta 5173)

**Servidor API não inicia**:
- Confirme que a versão do Node.js é mínima (node >=10)
- Verifique se a porta já está em uso
- Certifique-se de que todas as dependências foram instaladas com `npm install`

**Extensão de navegador não carrega**:
- Verifique se o manifest.json está formatado corretamente
- Consulte o console do navegador para erros
- Siga as instruções específicas do navegador para instalação de extensões

**Problemas no projeto de chat em Python**:
- Certifique-se de que o pacote OpenAI está instalado: `pip install openai`
- Verifique se a variável de ambiente GITHUB_TOKEN está definida
- Confirme as permissões de acesso aos GitHub Models

**Docsify não serve documentação**:
- Instale docsify-cli globalmente: `npm install -g docsify-cli`
- Execute desde o diretório raiz do repositório
- Verifique se `docs/_sidebar.md` existe

### Dicas para o Ambiente de Desenvolvimento

- Use VS Code com a extensão Live Server para projetos HTML
- Instale extensões ESLint e Prettier para formatação consistente
- Utilize DevTools do navegador para depurar JavaScript
- Para projetos Vue, instale a extensão Vue DevTools no navegador

### Considerações de Performance

- Grande quantidade de ficheiros traduzidos (50+ idiomas) torna os clones completos pesados
- Use clone superficial se trabalhar apenas com conteúdo: `git clone --depth 1`
- Exclua traduções de pesquisas ao trabalhar com conteúdo em inglês
- Processos de build podem ser lentos na primeira execução (npm install, build Vite)

## Considerações de Segurança

### Variáveis de Ambiente

- Chaves API nunca devem ser commitadas no repositório
- Use ficheiros `.env` (já listados no `.gitignore`)
- Documente as variáveis de ambiente necessárias nos READMEs dos projetos

### Projetos Python

- Utilize ambientes virtuais: `python -m venv venv`
- Mantenha dependências atualizadas
- Tokens GitHub devem ter permissões mínimas necessárias

### Acesso aos GitHub Models

- São necessários tokens de acesso pessoal (PAT) para GitHub Models
- Armazene os tokens como variáveis de ambiente
- Nunca faça commit de tokens ou credenciais

## Notas Adicionais

### Público-Alvo

- Iniciantes completos em desenvolvimento web
- Estudantes e autodidatas
- Professores que usam o currículo em sala de aula
- Conteúdo desenhado para acessibilidade e construção gradual de competências

### Filosofia Educativa

- Abordagem de aprendizagem baseada em projetos
- Verificação frequente do conhecimento (quizzes)
- Exercícios práticos de codificação
- Exemplos de aplicação real
- Foco nos fundamentos antes dos frameworks

### Manutenção do Repositório

- Comunidade ativa de aprendizes e contribuidores
- Atualizações regulares de dependências e conteúdo
- Issues e discussões monitorizadas por mantenedores
- Atualizações de tradução automatizadas via GitHub Actions

### Recursos Relacionados

- [Módulos Microsoft Learn](https://docs.microsoft.com/learn/)
- [Recursos do Student Hub](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) recomendado para aprendizes
- Cursos adicionais: AI Generativa, Ciência de Dados, ML, IoT disponíveis

### Trabalhar com Projetos Específicos

Para instruções detalhadas sobre projetos individuais, consulte os ficheiros README em:
- `quiz-app/README.md` - Aplicação de quiz Vue 3
- `7-bank-project/README.md` - Aplicação bancária com autenticação
- `5-browser-extension/README.md` - Desenvolvimento de extensão de navegador
- `6-space-game/README.md` - Desenvolvimento de jogo em canvas
- `9-chat-project/README.md` - Projeto de assistente de chat IA

### Estrutura Monorepo

Embora não seja um monorepo tradicional, este repositório contém múltiplos projetos independentes:
- Cada lição é autocontida
- Projetos não partilham dependências
- Trabalhe em projetos individuais sem afetar outros
- Clone todo o repositório para a experiência completa do currículo

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Aviso Legal**:  
Este documento foi traduzido utilizando o serviço de tradução automática [Co-op Translator](https://github.com/Azure/co-op-translator). Embora nos esforcemos pela precisão, esteja ciente de que traduções automáticas podem conter erros ou imprecisões. O documento original na sua língua nativa deve ser considerado a fonte oficial. Para informações críticas, recomenda-se tradução profissional humana. Não nos responsabilizamos por quaisquer mal-entendidos ou interpretações erradas decorrentes do uso desta tradução.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->