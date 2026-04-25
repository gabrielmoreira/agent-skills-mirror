# AGENTS.md

## Visão Geral do Projeto

Este é um repositório educacional para ensinar fundamentos de desenvolvimento web a iniciantes. O currículo é um curso abrangente de 12 semanas desenvolvido pelos Microsoft Cloud Advocates, com 24 aulas práticas abordando JavaScript, CSS e HTML.

### Componentes Principais

- **Conteúdo Educacional**: 24 aulas estruturadas organizadas em módulos baseados em projetos  
- **Projetos Práticos**: Terrarium, Jogo de Digitação, Extensão de Navegador, Jogo Espacial, App Bancário, Editor de Código e Assistente de Chat de IA  
- **Quizzes Interativos**: 48 quizzes com 3 perguntas cada (avaliações pré e pós-lesson)  
- **Suporte Multilíngue**: Traduções automáticas para mais de 50 idiomas via GitHub Actions  
- **Tecnologias**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (para projetos de IA)  

### Arquitetura

- Repositório educacional com estrutura baseada em lições  
- Cada pasta de lição contém README, exemplos de código e soluções  
- Projetos independentes em diretórios separados (quiz-app, vários projetos de lição)  
- Sistema de tradução usando GitHub Actions (co-op-translator)  
- Documentação servida via Docsify e disponível em PDF  

## Comandos de Configuração

Este repositório é principalmente para consumo de conteúdo educacional. Para trabalhar com projetos específicos:

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

### Projeto API Bancária (Node.js + Express)

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

### Projeto de Chat (Backend Python)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Defina a variável de ambiente GITHUB_TOKEN
python api.py
```

## Fluxo de Desenvolvimento

### Para Contribuidores de Conteúdo

1. **Fork o repositório** para sua conta no GitHub  
2. **Clone seu fork** localmente  
3. **Crie uma nova branch** para suas alterações  
4. Faça mudanças no conteúdo das lições ou exemplos de código  
5. Teste quaisquer alterações de código nos diretórios dos projetos relevantes  
6. Envie pull requests seguindo as diretrizes de contribuição  

### Para Aprendizes

1. Faça fork ou clone do repositório  
2. Navegue sequencialmente pelos diretórios das lições  
3. Leia os arquivos README de cada lição  
4. Complete os quizzes pré-lição em https://ff-quizzes.netlify.app/web/  
5. Trabalhe nos exemplos de código nas pastas da lição  
6. Complete as tarefas e desafios  
7. Faça os quizzes pós-lição  

### Desenvolvimento ao Vivo

- **Documentação**: Rode `docsify serve` na raiz (porta 3000)  
- **Quiz App**: Rode `npm run dev` no diretório quiz-app  
- **Projetos**: Use a extensão Live Server do VS Code para projetos HTML  
- **Projetos API**: Rode `npm start` nos diretórios das APIs respectivas  

## Instruções de Teste

### Teste do Quiz App

```bash
cd quiz-app
npm run lint       # Verificar problemas de estilo de código
npm run build      # Verificar se a compilação foi bem-sucedida
```

### Teste da API Bancária

```bash
cd 7-bank-project/api
npm run lint       # Verificar problemas de estilo de código
node server.js     # Verificar se o servidor inicia sem erros
```

### Abordagem Geral de Teste

- Este é um repositório educacional sem testes automatizados abrangentes  
- Teste manual foca em:  
  - Exemplos de código executando sem erros  
  - Links na documentação funcionando corretamente  
  - Builds dos projetos completando com sucesso  
  - Exemplos seguindo as melhores práticas  

### Checagens Pré-envio

- Execute `npm run lint` em diretórios com package.json  
- Verifique se os links markdown são válidos  
- Teste exemplos de código no navegador ou Node.js  
- Verifique que as traduções mantêm a estrutura adequada  

## Diretrizes de Estilo de Código

### JavaScript

- Use sintaxe moderna ES6+  
- Siga as configurações padrão do ESLint fornecidas nos projetos  
- Use nomes significativos para variáveis e funções para clareza educacional  
- Adicione comentários explicando conceitos para os aprendizes  
- Formate usando Prettier quando configurado  

### HTML/CSS

- Elementos semânticos HTML5  
- Princípios de design responsivo  
- Convenções claras de nomenclatura de classes  
- Comentários explicando técnicas CSS para aprendizes  

### Python

- Diretrizes de estilo PEP 8  
- Exemplos de código claros e educacionais  
- Dicas de tipo onde úteis para aprendizagem  

### Documentação em Markdown

- Hierarquia clara de títulos  
- Blocos de código com especificação de linguagem  
- Links para recursos adicionais  
- Capturas de tela e imagens nas pastas `images/`  
- Texto alternativo para imagens para acessibilidade  

### Organização de Arquivos

- Lições numeradas sequencialmente (1-getting-started-lessons, 2-js-basics, etc.)  
- Cada projeto tem diretórios `solution/` e frequentemente `start/` ou `your-work/`  
- Imagens armazenadas em pastas `images/` específicas da lição  
- Traduções na estrutura `translations/{language-code}/`  

## Build e Deploy

### Deploy do Quiz App (Azure Static Web Apps)

O quiz-app está configurado para deploy no Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Cria a pasta dist/
# Implanta via workflow do GitHub Actions ao enviar para a branch main
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

### Builds específicos de projetos

Cada diretório de projeto pode ter seu próprio processo de build:  
- Projetos Vue: `npm run build` cria bundles para produção  
- Projetos estáticos: Sem etapa de build, servem arquivos diretamente  

## Diretrizes para Pull Requests

### Formato do Título

Use títulos claros e descritivos indicando a área de mudança:  
- `[Quiz-app] Add new quiz for lesson X`  
- `[Lesson-3] Fix typo in terrarium project`  
- `[Translation] Add Spanish translation for lesson 5`  
- `[Docs] Update setup instructions`  

### Checagens Necessárias

Antes de enviar um PR:

1. **Qualidade do Código**:  
   - Rode `npm run lint` nos diretórios afetados  
   - Corrija todos os erros e avisos de lint  

2. **Verificação de Build**:  
   - Rode `npm run build` se aplicável  
   - Garanta que não ocorram erros no build  

3. **Validação de Links**:  
   - Teste todos os links markdown  
   - Verifique referências a imagens  

4. **Revisão de Conteúdo**:  
   - Revise ortografia e gramática  
   - Assegure que exemplos de código estão corretos e educativos  
   - Verifique que as traduções mantêm o significado original  

### Requisitos de Contribuição

- Aceite o CLA da Microsoft (verificação automática no primeiro PR)  
- Siga o [Código de Conduta Open Source da Microsoft](https://opensource.microsoft.com/codeofconduct/)  
- Veja [CONTRIBUTING.md](./CONTRIBUTING.md) para diretrizes detalhadas  
- Referencie números de issues na descrição do PR, se aplicável  

### Processo de Revisão

- PRs são revisados por mantenedores e comunidade  
- Clareza educacional tem prioridade  
- Exemplos de código devem seguir melhores práticas atuais  
- Traduções revisadas quanto à precisão e adequação cultural  

## Sistema de Tradução

### Tradução Automatizada

- Usa GitHub Actions com workflow co-op-translator  
- Traduz para mais de 50 idiomas automaticamente  
- Arquivos originais nos diretórios principais  
- Arquivos traduzidos em `translations/{language-code}/`  

### Adicionando Melhorias Manuais nas Traduções

1. Localize o arquivo em `translations/{language-code}/`  
2. Faça melhorias preservando a estrutura  
3. Garanta que exemplos de código permanecem funcionais  
4. Teste qualquer conteúdo de quiz localizado  

### Metadados de Tradução

Arquivos traduzidos incluem cabeçalho de metadados:  
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

## Depuração e Solução de Problemas

### Problemas Comuns

**O quiz app não inicia**:  
- Verifique a versão do Node.js (recomendado v14+)  
- Apague `node_modules` e `package-lock.json`, rode `npm install` novamente  
- Verifique conflitos de portas (padrão: Vite usa porta 5173)  

**Servidor API não inicia**:  
- Confirme a versão mínima do Node.js (node >=10)  
- Verifique se a porta não está em uso  
- Garanta que todas as dependências foram instaladas com `npm install`  

**Extensão de navegador não carrega**:  
- Verifique se o manifest.json está formatado corretamente  
- Verifique erros no console do navegador  
- Siga as instruções específicas de instalação da extensão para o navegador  

**Problemas no projeto de chat Python**:  
- Certifique-se que o pacote OpenAI está instalado: `pip install openai`  
- Verifique se a variável de ambiente GITHUB_TOKEN está definida  
- Confirme as permissões de acesso ao GitHub Models  

**Docsify não serve a documentação**:  
- Instale docsify-cli globalmente: `npm install -g docsify-cli`  
- Rode a partir do diretório raiz do repositório  
- Confira se `docs/_sidebar.md` existe  

### Dicas para Ambiente de Desenvolvimento

- Use VS Code com extensão Live Server para projetos HTML  
- Instale as extensões ESLint e Prettier para formatação consistente  
- Use DevTools do navegador para depurar JavaScript  
- Para projetos Vue, instale a extensão Vue DevTools para navegador  

### Considerações de Performance

- Grande número de arquivos traduzidos (50+ idiomas) torna clones completos grandes  
- Use clone raso se estiver trabalhando apenas no conteúdo: `git clone --depth 1`  
- Exclua traduções das buscas ao trabalhar no conteúdo em inglês  
- Processos de build podem ser lentos na primeira execução (npm install, build Vite)  

## Considerações de Segurança

### Variáveis de Ambiente

- Chaves de API nunca devem ser commitadas no repositório  
- Use arquivos `.env` (já listados no `.gitignore`)  
- Documente variáveis de ambiente necessárias nos READMEs dos projetos  

### Projetos Python

- Use ambientes virtuais: `python -m venv venv`  
- Mantenha as dependências atualizadas  
- Tokens GitHub devem ter permissões mínimas necessárias  

### Acesso GitHub Models

- Tokens de Acesso Pessoal (PAT) são exigidos para GitHub Models  
- Os tokens devem ser armazenados como variáveis de ambiente  
- Nunca commit tokens ou credenciais  

## Notas Adicionais

### Público-alvo

- Iniciantes completos em desenvolvimento web  
- Estudantes e autodidatas  
- Professores utilizando o currículo em salas de aula  
- Conteúdo desenhado para acessibilidade e construção gradual de habilidades  

### Filosofia Educacional

- Abordagem de aprendizado baseada em projetos  
- Verificações frequentes de conhecimento (quizzes)  
- Exercícios práticos de codificação  
- Exemplos de aplicação no mundo real  
- Foco em fundamentos antes de frameworks  

### Manutenção do Repositório

- Comunidade ativa de aprendizes e contribuintes  
- Atualizações regulares em dependências e conteúdo  
- Issues e discussões monitoradas por mantenedores  
- Atualizações de tradução automatizadas via GitHub Actions  

### Recursos Relacionados

- [Módulos Microsoft Learn](https://docs.microsoft.com/learn/)  
- [Recursos Student Hub](https://docs.microsoft.com/learn/student-hub/)  
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) recomendado para aprendizes  
- Cursos adicionais: AI Generativa, Ciência de Dados, ML, currículos IoT disponíveis  

### Trabalhando com Projetos Específicos

Para instruções detalhadas sobre projetos individuais, consulte os arquivos README em:  
- `quiz-app/README.md` - Aplicação de quiz Vue 3  
- `7-bank-project/README.md` - Aplicação bancária com autenticação  
- `5-browser-extension/README.md` - Desenvolvimento de extensão de navegador  
- `6-space-game/README.md` - Desenvolvimento de jogo baseado em canvas  
- `9-chat-project/README.md` - Projeto assistente de chat IA  

### Estrutura Monorepo

Embora não seja um monorepo tradicional, este repositório contém múltiplos projetos independentes:  
- Cada lição é autocontida  
- Projetos não compartilham dependências  
- Trabalhe em projetos individuais sem afetar outros  
- Faça clone do repositório completo para experiência total do currículo  

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Aviso Legal**:  
Este documento foi traduzido utilizando o serviço de tradução por IA [Co-op Translator](https://github.com/Azure/co-op-translator). Embora nos esforcemos para garantir a precisão, por favor, esteja ciente de que traduções automatizadas podem conter erros ou imprecisões. O documento original em sua língua nativa deve ser considerado a fonte autorizada. Para informações críticas, recomenda-se a tradução profissional realizada por humanos. Não nos responsabilizamos por quaisquer mal-entendidos ou interpretações incorretas decorrentes do uso desta tradução.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->