---
name: grill-me
description: Mène une interview technique approfondie et contradictoire (grilling) pour challenger une idée, explorer les alternatives et verrouiller les choix d'architecture avant de coder.
---

# Grill-Me (Cadrage & Interview Contradictoire)

Cette compétence permet de transformer des idées floues, des intentions vagues ou des propositions de fonctionnalités en **décisions d'architecture solides et éprouvées**, grâce à un questionnement technique structuré et sans complaisance.

Elle fusionne le meilleur de l'exploration d'alternatives (Design Thinking) et de la méthode d'interview par paliers issue de [AI Hero](https://aihero.dev).

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

### Étape 5 : Transition vers le plan d'implémentation
Dès que l'utilisateur confirme son accord :
- Ne commence pas à coder à l'aveugle.
- Invite l'utilisateur à lancer le mode de Planification natif de son outil pour découper l'implémentation en sous-tâches :
  - **Sous Google Antigravity :** Propose d'enchaîner avec la commande `/plan`.
  - **Sous GitHub Copilot :** Propose de basculer en mode `Plan`.
  - **Sous OpenAI ChatGPT / Codex :** Propose d'invoquer `$plan`.
