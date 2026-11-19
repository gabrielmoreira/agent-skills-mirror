---
name: grill-me
description: Mène une interview technique approfondie et contradictoire (grilling) pour challenger une idée, explorer les alternatives et verrouiller les choix d'architecture avant de coder.
---

# Grill-Me (Cadrage & Interview Contradictoire)

Cette compétence permet de transformer des idées floues, des intentions vagues ou des propositions de fonctionnalités en **décisions d'architecture solides et éprouvées**, grâce à un questionnement technique structuré et sans complaisance.

Elle fusionne le meilleur de l'exploration d'alternatives (Design Thinking) et de la méthode d'interview par paliers issue de [AI Hero](https://aihero.dev).

---

## Contrat de réutilisation de la méthode

La méthode contradictoire réunit les instructions d'inspection, de cadrage, d'exploration des choix, de questionnement et de synthèse. Une compétence peut la réutiliser en adaptant son interlocuteur et sa restitution, sans reprendre les suites de planification ou d'implémentation propres à `grill-me`. Pour une utilisation directe de `grill-me`, l'interview et la validation explicite par l'utilisateur restent inchangées.

La compétence [grill-agent](../grill-agent/SKILL.md), lorsqu'elle est installée, utilise la méthode actuelle avec ses propres adaptations : l'agent principal est interrogé, le relecteur reste en lecture seule et ne passe pas au mode Plan.

Lors d'une évolution de `grill-me`, conserve la possibilité d'identifier et de réutiliser cette méthode selon sa finalité, indépendamment du titre, de l'ordre ou de la numérotation des étapes. Les améliorations compatibles de la méthode doivent aussi bénéficier à ses utilisations adaptées. Si une modification rompt ce contrat, vérifie et adapte `grill-agent` dans le même changement lorsqu'il est disponible ; sinon, signale la rupture. L'absence de `grill-agent` ne bloque pas l'utilisation de `grill-me`.

---

## RÈGLE FONDAMENTALE : ZÉRO CODE SANS ALIGNEMENT VALIDÉ

Tu as l'interdiction formelle d'écrire, de modifier du code source, de lancer des commandes destructrices ou d'initialiser des composants **AVANT** d'avoir mené l'interview à son terme et obtenu la validation claire et explicite de l'utilisateur sur le design final.

---

## 1. Principes clés de l'interview (La méthode Grill-Me)

### A. Inspection préalable du code (Fact-Checking obligatoire)
Avant de poser la moindre question à l'utilisateur, **explore toujours la base de code existante** (fichiers de configuration, modèles, dépendances, architecture actuelle).
- **Règle absolue :** Ne pose JAMAIS une question dont la réponse se trouve déjà dans le code ou la documentation du projet. L'utilisateur ne doit pas perdre son temps à répéter ce que l'agent peut lire lui-même.

### B. L'arbre de conception (Design Tree)
Ne pose pas de questions au hasard. Cartographie mentalement les décisions selon leur ordre de dépendance logique :
1. *Niveau 1 :* Définition du problème métier, périmètre et contraintes strictes.
2. *Niveau 2 :* Choix de l'approche architecturale ou du patron de conception.
3. *Niveau 3 :* Modèle de données, APIs, flux d'exécution et gestion des erreurs.
4. *Niveau 4 :* Détails d'ergonomie, nommage et cas limites.

### C. Questions par "Rounds" (Paliers logiques)
- Évite les questions isolées une par une (qui ralentissent la discussion), mais n'assomme pas non plus l'utilisateur avec 15 questions d'un coup.
- Regroupe les questions par **Rounds de 2 à 4 questions maximum**, correspondant à un même niveau de l'arbre de décision.
- Présente chaque question sous forme de choix multiples clairs (A / B / C).

### D. La recommandation obligatoire (Smart Defaults)
Pour **chaque question posée**, tu DOIS impérativement fournir ta recommandation experte argumentée :
- Exemple : `Option A (Recommandé) : ... (Justification en 1 phrase)`
- **Objectif :** Permettre à l'utilisateur de valider immédiatement d'un simple *"D'accord avec tes recommandations"* ou d'ajuster uniquement le point qui lui tient à cœur.

---

## 2. Déroulement étape par étape

### Étape 1 : Assimilation du contexte & Cadrage
1. Lis les fichiers pertinents du projet pour comprendre les patterns actuels.
2. Reformule brièvement ton analyse du besoin initial.
3. Si le sujet est vaste ou aborde plusieurs sous-systèmes indépendants, propose immédiatement de découper le projet et focalise l'interview sur la première sous-partie.

### Étape 2 : Exploration d'alternatives (si le problème est ouvert)
Si plusieurs solutions architecturales ou technologiques sont envisageables :
- Présente **2 à 3 options contrastées**.
- Détaille pour chacune ses forces, ses faiblesses et ses compromis (*trade-offs*).
- Indique clairement ton option recommandée avant de passer aux détails.

### Étape 3 : Les Rounds de questions approfondies
Mène l'interview pour éliminer les angles morts :
- Cas d'erreurs et comportements aux limites (*Edge cases*).
- Impact sur les performances ou la sécurité.
- Compatibilité avec l'existant et dépendances à introduire.
- Formule toujours tes options avec leur recommandation par défaut.

### Étape 4 : Synthèse du Design & Validation finale
Une fois les décisions arrêtées :
1. Rédige un **récapitulatif concis et sans ambiguïté** :
   - Décisions d'architecture actées.
   - Modèle de données / flux retenus (ajoute un diagramme **Mermaid** si le flux ou les relations sont complexes).
   - Composants impactés et fichiers cibles identifiés.
2. Demande la validation explicite de l'utilisateur.

### Étape 5 : Suite adaptée et planification conditionnelle

Après la validation explicite du design, détermine si une mise en œuvre est souhaitée et si une planification supplémentaire apporte une réelle valeur. Propose le mode Plan lorsque la complexité, les dépendances, les risques ou le besoin de revue justifient un découpage ; explique brièvement pourquoi et laisse l'utilisateur choisir.

Ne propose pas de changer de mode pour une simple discussion, une modification évidente ou un plan existant déjà suffisant, sauf demande explicite de l'utilisateur. Si le mode Plan est déjà actif, élabore ou poursuis le plan si nécessaire, sans demander de le réactiver.

La validation du design ne vaut pas, à elle seule, demande d'implémentation. Si la réalisation a été expressément demandée, respecte cette demande et les permissions de l'environnement ; sinon, termine par la synthèse sans modifier de fichiers.

**Lorsque le mode Plan est pertinent :**
1. Identifie l'outil et son interface ; ne suppose pas que les mêmes commandes existent dans toutes les interfaces.
2. Indique uniquement les étapes correspondant à l'interface utilisée, en t'appuyant sur les indications ci-dessous. Demande de reprendre les décisions validées dans le plan.
3. Si l'interface ou la disponibilité du mode est incertaine, demande la précision nécessaire ou consulte la documentation officielle ; n'invente pas de commande. Les libellés et raccourcis peuvent varier selon la version.

| Outil et interface | Activation |
| :--- | :--- |
| **GitHub Copilot app** | Dans la session, ouvre le sélecteur de mode sous la zone de saisie et choisis **Plan**. [Documentation GitHub](https://docs.github.com/en/copilot/how-tos/github-copilot-app/agent-sessions#choosing-a-session-mode). |
| **GitHub Copilot dans un IDE compatible** | Ouvre Copilot Chat et choisis **Plan** dans le sélecteur d'agents en bas du panneau. [Documentation GitHub](https://docs.github.com/en/copilot/how-tos/copilot-in-your-ide/use-copilot-agents/use-plan-mode). |
| **GitHub Copilot CLI interactif** | Dans la zone de saisie, appuie sur **Maj+Tab** jusqu'au mode **Plan**. [Documentation GitHub](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-cli). |
| **Google Antigravity app ou IDE** | Dans le panneau de l'agent, ouvre le sélecteur de mode et choisis **Planning**. [Documentation Google](https://antigravity.google/docs/ide/agent-side-panel). |
| **Google Antigravity CLI interactif** | Dans la zone de saisie, appuie sur **Maj+Tab** jusqu'à **plan**, puis vérifie l'indicateur de mode. [Documentation Google](https://antigravity.google/docs/cli/modes). |
| **Codex app** | Dans la zone de saisie, tape `/plan` puis valide pour basculer en mode Plan. [Documentation OpenAI](https://learn.chatgpt.com/docs/reference/slash-commands). |
| **Codex CLI interactif** | Dans la zone de saisie, tape `/plan` puis valide, ou utilise **Maj+Tab** jusqu'au mode Plan. [Documentation OpenAI](https://learn.chatgpt.com/guides/best-practices). |
| **Autre interface Codex** | Vérifie si son sélecteur propose **Plan** et consulte sa documentation ; ne présume pas que les commandes de l'application ou du CLI y sont disponibles. |
| **Claude Code (CLI, VS Code ou JetBrains)** | Utilise **Maj+Tab** jusqu'au mode **Plan** ou préfixe la demande de planification par `/plan`. En CLI, une session peut aussi démarrer avec `claude --permission-mode plan`. [Documentation Anthropic](https://code.claude.com/docs/en/permission-modes). |
| **Autre interface Claude** | Ne présume pas qu'elle expose le mode de Claude Code ; vérifie son sélecteur et sa documentation officielle avant d'indiquer une méthode. |

Sous Antigravity, préviens que la politique de revue des artefacts **Always proceed** peut poursuivre automatiquement ; si une validation manuelle est nécessaire, indique l'option **Request review** dans les paramètres de l'agent, lorsqu'elle est disponible. [Documentation Google](https://antigravity.google/docs/artifact-review).
