---
name: "bacen-compliance-sentinel-rafael-mastronardi"
description: "Orientação completa sobre conformidade com regulamentações do Banco Central do Brasil: Resolução CMN nº 4.893/2021 (Política de Segurança Cibernética), Resolução BCB nº 85/2021 (GRSIC), Open Finance Brasil (Resoluções BCB nº 32/2020 e atualizações), e demais normas prudenciais do BACEN. Cobre elaboração e revisão de Política de Segurança Cibernética, Plano de Ação e Resposta a Incidentes (PARI), Gestão de Riscos de Serviços de Informação e Comunicação (GRSIC), consentimento e compartilhamento de dados no Open Finance, requisitos de API, gestão de terceiros (outsourcing) e sanções do BACEN. Triggers: Bacen, Banco Central, CMN 4.893, Resolução 4.893, segurança cibernética bancária, PARI, GRSIC, Open Finance, Open Banking, compartilhamento de dados financeiros, consentimento Open Finance, API financeira, outsourcing bancário, risco cibernético, incidente cibernético banco, LGPD financeira, fintech compliance, instituição financeira, DICT, Pix segurança."
metadata:
  author: "Rafael Mastronardi"
  license: "agpl-3.0"
  version: "2026-05-20"
---

# BACEN Compliance Sentinel

## Aviso Importante (exibir no início da sessão)

> **Atenção:** Esta skill fornece orientação estruturada sobre regulamentações do Banco Central do Brasil. Não constitui aconselhamento jurídico ou regulatório. Para decisões finais, consulte advogado especializado e o Diretor responsável pela área de Segurança Cibernética da instituição.

---

## Roteamento por Tarefa

Identifique a necessidade do usuário e atue conforme a tabela:

| Necessidade do Usuário | Normativo Central | Ação |
|---|---|---|
| "Política de Segurança Cibernética" / "PSC" | Res. CMN 4.893/2021 | Análise/elaboração da PSC |
| "Plano de ação" / "resposta a incidente" / "PARI" | Res. CMN 4.893/2021, Art. 6º | Estruturar o PARI |
| "GRSIC" / "serviços de TI" / "cloud" / "outsourcing" | Res. BCB 85/2021 | Avaliação de risco de terceiros |
| "Open Finance" / "Open Banking" / "compartilhamento de dados" | Res. BCB 32/2020 e atualizações | Análise de conformidade Open Finance |
| "Consentimento Open Finance" | Res. BCB 32/2020 | Requisitos de consentimento |
| "API" / "requisitos técnicos Open Finance" | Manual Open Finance Brasil | Análise de requisitos técnicos |
| "Pix segurança" / "DICT" / "fraude Pix" | Res. BCB 1/2020 + Circular 3.952 | Conformidade Pix |
| "Incidente cibernético" / "ataque" | Res. CMN 4.893/2021, Art. 6º | Roteiro de resposta e comunicação ao BACEN |
| "Sanções" / "autuação BACEN" / "multa" | Lei 4.595/1964 + Res. 4.553/2017 | Análise de exposição e mitigação |
| "Relatório anual" / "RAS" | Res. CMN 4.893/2021, Art. 9º | Estrutura do Relatório Anual de Segurança |

---

## Pontos de Precisão Regulatória

Áreas onde o modelo pode ter imprecisões — aplique sempre estas regras:

### Resolução CMN nº 4.893/2021 — Segurança Cibernética

**Escopo:** Aplica-se a todas as instituições autorizadas a funcionar pelo BACEN (bancos, cooperativas, fintechs, instituições de pagamento, administradoras de consórcio). A norma substituiu a Resolução nº 4.658/2018.

**Política de Segurança Cibernética (PSC) — Art. 4º:**
Deve ser compatível com o porte, perfil de risco e modelo de negócio da instituição. Elementos obrigatórios:
- Objetivos de segurança cibernética
- Procedimentos e controles adotados
- Controles de acesso, criptografia, prevenção e detecção de intrusões
- Rastreabilidade de informações
- Manutenção de cópias de segurança
- Mecanismos de autenticação
- Prevenção e resposta a incidentes
- Classificação de dados (Art. 4º, § 2º — dado sensível conforme LGPD recebe tratamento diferenciado)
- Monitoramento contínuo

**Atenção:** A PSC deve ser aprovada pelo Conselho de Administração (ou equivalente) e divulgada aos funcionários e prestadores de serviços.

**Diretoria Responsável — Art. 5º:**
Obrigatória para **todos** os segmentos. O Diretor pode acumular outras funções, exceto nas instituições dos Segmentos S1 e S2, onde não pode acumular com a Diretoria de Auditoria Interna. O nome do Diretor deve ser comunicado ao BACEN.

**Plano de Ação e Resposta a Incidentes (PARI) — Art. 6º:**
Deve contemplar: rotinas de resposta, mecanismos de rastreabilidade, meios para comunicação ao BACEN e ao público, plano de contingência, procedimentos para retomada de atividades. Deve ser testado anualmente (testes de penetração, simulações de incidente).

**Relatório Anual — Art. 9º:**
Obrigatório. Deve ser elaborado anualmente e aprovado pela Diretoria e Conselho de Administração. Conteúdo: iniciativas de segurança cibernética implementadas, resultados dos testes, incidentes ocorridos, pendências.

### Resolução BCB nº 85/2021 — GRSIC (Gestão de Riscos de TI)

**Escopo:** Estabelece requisitos para contratação de serviços relevantes de processamento, armazenamento e transmissão de dados (outsourcing, cloud computing).

**Serviço Relevante:** Definido como aquele cuja interrupção comprometa o funcionamento normal ou a prestação de serviços essenciais. A instituição deve fazer análise de materialidade.

**Requisitos para contratação (Art. 16 e seguintes):**
- Due diligence prévia do prestador
- Cláusulas contratuais obrigatórias (acesso pelo BACEN, continuidade de serviço, sigilo)
- Política de segurança do prestador compatível com a da instituição
- Plano de contingência e de saída (exit plan)
- Localização dos dados: **dados e processamento no exterior** são permitidos, mas a instituição permanece responsável; deve comunicar ao BACEN se dados críticos forem processados no exterior

**Cloud Computing:** Permitido sem prévia aprovação do BACEN, mas sujeito a todos os requisitos de due diligence e contratuais da Resolução BCB 85/2021.

**Atenção:** A responsabilidade pelo serviço é **intransferível**. Mesmo que o prestador falhe, a instituição responde perante o BACEN.

### Open Finance Brasil — Resoluções BCB nº 32/2020 e atualizações

**Fases do Open Finance:**
- Fase 1: Dados abertos (produtos e serviços, canais de atendimento) — sem consentimento do cliente
- Fase 2: Dados de clientes (cadastro, transações, empréstimos) — **requer consentimento**
- Fase 3: Iniciação de pagamento e propostas de crédito — **requer consentimento**
- Fase 4: Dados de câmbio, investimentos, seguros, previdência — **requer consentimento**

**Consentimento no Open Finance — requisitos obrigatórios:**
1. Propósito específico e limitado
2. Prazo de vigência máximo de **12 meses** (renovável)
3. Identificação clara da instituição receptora
4. Lista de dados a serem compartilhados
5. Confirmação ativa do cliente (não pode ser opt-out ou pré-selecionado)
6. Canal de revogação disponível a qualquer momento
7. Registro do consentimento com timestamp e identificador único

**Atenção:** A LGPD e o Open Finance são **complementares mas distintos**. O consentimento do Open Finance não equivale ao consentimento da LGPD — podem ser necessários ambos para diferentes finalidades.

**Detentores de dados (transmissores):** Devem disponibilizar APIs conforme padrões técnicos do Manual do Open Finance Brasil. Prazo de resposta da API: 99,5% das chamadas respondidas em até 1 segundo (SLA regulatório).

**Receptores de dados:** Devem ser participantes cadastrados na estrutura de governança do Open Finance. Devem usar os dados exclusivamente para a finalidade do consentimento.

**Iniciação de Pagamento (PISP):** A instituição iniciadora não toca nos recursos do cliente — apenas dispara a ordem ao banco do cliente. O consentimento é de uso único (single-use).

### Pix — Segurança e Conformidade

**DICT (Diretório de Identificadores de Transações do Cidadão):**
Gerido pelo BACEN. A instituição deve consultar o DICT antes de processar transações e reportar fraudes. Obrigações de comunicação de fraudes: prazo de **1 hora** após identificação.

**Prevenção a fraudes Pix — Resolução BCB 6/2023 (e atualizações):**
Limites de valor por período (horário noturno, novos dispositivos). Mecanismo Especial de Devolução (MED): prazo de até 7 dias para análise e até 96 horas para devolução após aprovação.

**Dados de segurança obrigatórios:** As instituições devem manter logs de transações Pix por no mínimo **5 anos** (alinhado ao prazo prescricional).

### Comunicação de Incidentes ao BACEN

**Prazo:** Incidentes relevantes devem ser comunicados ao BACEN em até **3 dias úteis** após a identificação.

**O que é incidente relevante:** Interrupção de serviços por mais de 6 horas consecutivas; acesso não autorizado a sistemas críticos; vazamento de dados de mais de 1.000 clientes; fraude envolvendo falha de segurança da instituição.

**Formulário:** Comunicado via portal do BACEN (Siscoaf/sistema específico). Deve conter: data/hora da ocorrência, sistemas afetados, clientes impactados, medidas adotadas.

**Atenção:** A comunicação ao BACEN é **independente** da comunicação à ANPD pela LGPD — ambas podem ser exigidas para o mesmo evento.

### Sanções do BACEN

**Base legal:** Lei 4.595/1964, Lei 13.506/2017 (principal marco sancionatório).

**Penalidades — Lei 13.506/2017:**
- Advertência
- Multa: até R$ 2 bilhões por infração (pessoa jurídica) ou até o dobro do valor do benefício econômico obtido
- Inabilitação temporária de administradores: até 10 anos
- Proibição de exercício de cargo: permanente em casos graves
- Cancelamento de autorização de funcionamento

**Processo administrativo:** Intimação → Defesa (15 dias) → Decisão da Diretoria do BACEN → Recurso ao CMN (para multas acima de determinado valor).

**Atenção:** A Lei 13.506/2017 permite responsabilização **pessoal dos administradores** por atos dolosos ou culposos que causem danos à instituição ou ao SFN.

---

## Fluxo de Elaboração da Política de Segurança Cibernética (PSC)

### Fase 1: Diagnóstico e Segmentação

Identificar o segmento da instituição:
- **S1:** Banco com porte > R$ 1 trilhão ou relevância sistêmica internacional
- **S2:** Banco com porte entre R$ 100 bilhões e R$ 1 trilhão
- **S3:** Instituição com porte entre R$ 15 bilhões e R$ 100 bilhões
- **S4:** Instituição com porte entre R$ 1 bilhão e R$ 15 bilhões
- **S5:** Instituição de menor porte (< R$ 1 bilhão) — pode usar PSC simplificada

O segmento determina o nível de detalhe e os requisitos adicionais da PSC.

### Fase 2: Mapeamento de Ativos e Riscos

Coletar do usuário:
- Sistemas críticos (core bancário, canais digitais, infraestrutura de pagamentos)
- Dados tratados (clientes PF, PJ, dados sensíveis, dados de pagamento)
- Prestadores de serviços relevantes (cloud, processamento, correspondentes)
- Conexões externas (Open Finance, Pix, SPB, SWIFT)
- Incidentes históricos nos últimos 3 anos

Avaliar ameaças prioritárias: phishing/engenharia social, ransomware, fraude em canais digitais, ataques a APIs, comprometimento de credenciais, insider threat.

### Fase 3: Estrutura da PSC

A PSC deve conter obrigatoriamente (Res. CMN 4.893/2021, Art. 4º):

**1. Objetivos e Escopo**
- Abrangência (sistemas, filiais, subsidiárias, correspondentes)
- Princípios de segurança cibernética adotados

**2. Controles e Procedimentos**
- Gestão de identidade e acesso (IAM): autenticação multifator, controle de privilégios mínimos
- Criptografia: em trânsito (TLS 1.2+) e em repouso para dados sensíveis
- Monitoramento e detecção: SOC/SIEM, alertas de anomalia
- Gestão de vulnerabilidades: ciclo de patching, pentest semestral
- Segurança de endpoints e redes
- Gestão de ativos de informação

**3. Classificação de Dados**
- Pública / Interna / Confidencial / Restrita
- Dados LGPD (especialmente dados sensíveis) → nível Restrito
- Dados de pagamento (Pix, cartão) → nível Restrito

**4. Gestão de Terceiros (GRSIC)**
- Critérios para classificação de serviços relevantes
- Processo de due diligence de prestadores
- Cláusulas contratuais mínimas
- Monitoramento contínuo de terceiros

**5. Plano de Ação e Resposta a Incidentes (PARI)**
- Definição de incidente (por severidade: crítico, alto, médio, baixo)
- Equipe de resposta (CSIRT interno ou terceirizado)
- Fluxo de comunicação interno e externo (BACEN, ANPD, clientes)
- Procedimentos de contenção, erradicação e recuperação
- Critérios para acionamento do Plano de Continuidade

**6. Testes e Exercícios**
- Pentest: mínimo anual (S1 e S2: semestral recomendado)
- Red team exercise: anual para S1 e S2
- Simulação de incidente (tabletop): anual
- Teste de DRP/BCP: anual

**7. Governança e Responsabilidades**
- Diretor responsável (nome e cargo)
- Comitê de Segurança (composição e periodicidade)
- Papéis e responsabilidades (RACI)

**8. Treinamento e Conscientização**
- Programa anual de conscientização
- Treinamento específico para equipes de TI e segurança
- Simulações de phishing

**9. Relatório Anual (RAS)**
- Cronograma de elaboração e aprovação

### Fase 4: Aprovação e Comunicação

Fluxo obrigatório:
1. Elaboração pela área de Segurança Cibernética / TI
2. Revisão pelo Diretor responsável
3. Validação pelo Comitê de Auditoria ou Risco (se existente)
4. **Aprovação pelo Conselho de Administração ou equivalente**
5. Divulgação a todos os funcionários e prestadores de serviços relevantes
6. Comunicação do nome do Diretor responsável ao BACEN (via Unicad)

---

## Checklist de Conformidade Open Finance

### Para Instituições Transmissoras (detentoras de dados)

- [ ] APIs disponíveis conforme padrão técnico do Manual Open Finance Brasil
- [ ] SLA de disponibilidade: 99,5% (mensal) com tempo de resposta < 1 segundo (95% das chamadas)
- [ ] Portal de desenvolvedor com documentação atualizada
- [ ] Validação de consentimento antes de cada compartilhamento
- [ ] Log de compartilhamentos com retenção mínima de 5 anos
- [ ] Canal de revogação de consentimento disponível 24/7
- [ ] Comunicação de incidentes de API ao BACEN conforme prazo

### Para Instituições Receptoras

- [ ] Cadastro ativo na estrutura de governança do Open Finance
- [ ] Coleta de consentimento conforme requisitos regulatórios
- [ ] Uso de dados restrito à finalidade do consentimento
- [ ] Política de retenção dos dados compartilhados (máximo vigência do consentimento + prazo legal)
- [ ] Canal de atendimento ao cliente para questões de Open Finance
- [ ] Auditoria de acesso aos dados compartilhados

### Para Iniciadores de Pagamento (PISP)

- [ ] Autorização específica do BACEN para iniciar pagamentos
- [ ] Consentimento de uso único por transação
- [ ] Não armazenamento de credenciais do cliente
- [ ] Confirmação explícita do cliente com dados da transação

---

## Roteiro de Resposta a Incidente Cibernético (PARI)

### Fase 1: Identificação e Classificação (0-2h)

Critérios de severidade:
- **Crítico:** Sistema indisponível > 1h; ransomware; acesso não autorizado a dados de > 1.000 clientes
- **Alto:** Sistema degradado; tentativa de acesso não autorizado contida; phishing com credenciais comprometidas
- **Médio:** Anomalia detectada, sem impacto confirmado; vulnerabilidade crítica descoberta
- **Baixo:** Evento de segurança sem impacto operacional

Acionar: Diretor de Segurança Cibernética + CSIRT + Jurídico (para incidentes Crítico/Alto).

### Fase 2: Contenção (2-6h)

- Isolar sistemas comprometidos da rede
- Preservar evidências (imagens forenses antes de qualquer ação)
- Impedir propagação (segmentação de rede, revogação de credenciais)
- Ativar sistemas de backup/contingência se necessário
- Registrar todas as ações com timestamp

### Fase 3: Comunicação Regulatória

**BACEN:** até **3 dias úteis** da identificação do incidente relevante
- Sistema de comunicação: portal do BACEN (protocolo eletrônico)
- Informações obrigatórias: data/hora, sistemas afetados, clientes impactados, medidas adotadas, previsão de normalização

**ANPD (se dados pessoais afetados):** até **72 horas** da ciência (Res. CD/ANPD nº 2/2022)
- Atenção: prazos diferentes — BACEN (3 dias úteis) vs. ANPD (72 horas corridas)

**Clientes:** comunicação direta se dados afetados, de forma clara e tempestiva
**Mídia/público:** somente após comunicação regulatória e alinhamento com Jurídico e Comunicação

### Fase 4: Erradicação e Recuperação

- Identificar e eliminar causa raiz
- Aplicar patches e correções necessárias
- Restaurar sistemas a partir de backups íntegros
- Verificar integridade dos dados restaurados
- Testes de segurança antes de retorno à produção

### Fase 5: Pós-Incidente

- Relatório de incidente completo (Root Cause Analysis — RCA)
- Atualização do PARI com lições aprendidas
- Inclusão no Relatório Anual de Segurança (RAS)
- Comunicação de encerramento ao BACEN (se aplicável)

---

## Avaliação de Due Diligence de Prestadores (GRSIC)

### Critérios de Materialidade

Um serviço é **relevante** se qualquer resposta abaixo for "Sim":
1. Sua interrupção compromete a prestação de serviços essenciais?
2. Envolve acesso a dados de clientes ou dados de pagamento?
3. Está integrado a sistemas críticos (core bancário, Pix, Open Finance)?
4. O custo de substituição seria superior a [threshold definido pela instituição]?

### Checklist de Due Diligence

**Documentação:**
- [ ] Certidões negativas (fiscal, trabalhista, previdenciária)
- [ ] Relatório de auditoria de segurança (SOC 2 Type II, ISO 27001 ou equivalente)
- [ ] Política de Segurança da Informação do prestador
- [ ] Plano de Continuidade de Negócios (BCP) do prestador
- [ ] Evidência de seguro cyber (recomendado para S1 e S2)

**Técnica:**
- [ ] Avaliação de vulnerabilidades do ambiente do prestador
- [ ] Verificação de certificações e conformidade regulatória
- [ ] Teste de penetração recente (< 12 meses)
- [ ] Arquitetura de segurança e controles de acesso

**Cláusulas Contratuais Obrigatórias (Res. BCB 85/2021):**
- [ ] Acesso do BACEN às instalações e documentação do prestador
- [ ] Continuidade do serviço mesmo em caso de insolvência do prestador
- [ ] Dever de sigilo em relação a dados de clientes
- [ ] Obrigação de comunicar incidentes à instituição contratante
- [ ] Direito de auditoria pela instituição contratante
- [ ] Plano de saída (exit plan) com prazo de transição mínimo

---

## Formatos de Saída

**PSC completa:** Documento .docx com capa, sumário executivo, todos os 9 capítulos obrigatórios, anexos (RACI, glossário, lista de sistemas críticos, tabela de prestadores relevantes).

**PARI:** Documento operacional .docx com fluxogramas de decisão, contatos de emergência, checklists por fase, árvore de comunicação.

**Relatório de Due Diligence de Prestador:** .docx com sumário executivo, achados por categoria, matriz de risco, recomendações e parecer final (Aprovado / Aprovado com condições / Reprovado).

**Relatório Anual de Segurança (RAS):** .docx estruturado conforme Res. CMN 4.893/2021, Art. 9º, com seções para iniciativas implementadas, resultados de testes, incidentes e pendências.

**Parecer de conformidade Open Finance:** Análise estruturada com checklist, gaps identificados e roadmap de adequação.

---

## Referências Normativas

- Resolução CMN nº 4.893/2021 — Política de Segurança Cibernética
- Resolução BCB nº 85/2021 — GRSIC e Serviços Relevantes de TI
- Resolução BCB nº 32/2020 e atualizações — Open Finance Brasil
- Resolução BCB nº 1/2020 — Pix (regulamento geral)
- Resolução BCB nº 6/2023 — Medidas de prevenção a fraudes no Pix
- Circular BCB nº 3.952/2019 — DICT
- Lei 13.506/2017 — Processo Administrativo Punitivo do BACEN
- Lei 4.595/1964 — Sistema Financeiro Nacional
- Manual do Open Finance Brasil (OpenFinanceBrasil.org.br)
- Guia de Segurança Cibernética BACEN (publicação orientativa)
- Resolução CMN nº 4.557/2017 — Gestão de Riscos (complementar)
- Lei 13.709/2018 (LGPD) — Interação com dados financeiros
