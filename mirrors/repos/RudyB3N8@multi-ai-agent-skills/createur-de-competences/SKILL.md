---
name: createur-de-competences
description: Compétence universelle pour concevoir, structurer et générer de nouvelles compétences (skills) multi-IA compatibles avec Google Antigravity, GitHub Copilot et ChatGPT/Codex selon le standard Open Agent Skills.
---

# Créateur de compétences universel multi-IA

Tu dois utiliser cette compétence à chaque fois que l'utilisateur te demande de concevoir, créer, structurer ou modifier une compétence (`skill`).

L'objectif est de concevoir des compétences modulaires, propres et directement exploitables par les agents de codage modernes. Par défaut, toute compétence créée doit être **universelle** et respecter le standard [Open Agent Skills](https://agentskills.io), afin de fonctionner de manière transparente sur **Google Antigravity**, **GitHub Copilot** et **OpenAI ChatGPT / Codex**.

---

## 1. Protocole de cadrage interactif par Rounds (OBLIGATOIRE AVANT DE CODER)

Avant de commencer la rédaction du moindre fichier ou de générer l'arborescence, tu dois obligatoirement cadrer le besoin pour lever les zones d'ombre. Ne fixe aucun quota artificiel de questions ; applique la **Definition of Ready** basée sur les 4 piliers indispensables :

### Les 4 Piliers indispensables :
1. **Déclencheurs & Rôle :** Quel est l'objectif exact et les mots-clés de déclenchement (*front-loading* pour la description) ?
2. **Contrat d'Entrée / Sortie :** Quelles données/fichiers l'agent reçoit-il et quels résultats concrets produit-il ?
3. **Outillage & Emplacement :** Faut-il des scripts (`scripts/`), des templates (`resources/`) ou des fiches de référence ? Où stocker la compétence (Projet dans `.agents/skills` ou Global) ?
4. **Robustesse & Cas limites :** Comment l'agent réagit-il aux erreurs, dépendances manquantes ou comportements inattendus ?

### Règles de l'interview par Rounds :
- **Anti-redondance :** Analyse d'abord le prompt initial et la base de code. Ne pose JAMAIS de questions sur les éléments déjà explicites ou déductibles.
- **Rounds calibrés (2 à 4 questions max par message) :** Regroupe les questions restantes par niveau logique pour ne jamais submerger l'utilisateur d'un coup.
- **Smart Defaults (Recommandation systématique) :** Chaque question DOIT comporter une option recommandée clairement identifiée (ex: `Option A (Recommandé) : ...`), permettant à l'utilisateur de valider d'un simple accord global.
- **Condition d'arrêt naturelle :** Dès que les 4 piliers sont verrouillés (souvent en 1 seul round pour un besoin clair, 2 à 3 rounds pour un besoin complexe), l'interview s'arrête et tu passes à la génération.
- **Clause Fast-Forward :** Si l'utilisateur répond *"Passe à la génération avec tes recommandations"*, arrête immédiatement l'interview et génère la compétence avec tes choix recommandés.

> **Important :** Ne commence l'implémentation qu'après avoir reçu et validé les réponses de l'utilisateur.

---

## 2. Règle linguistique

- **RÈGLE PAR DÉFAUT :** L'intégralité du contenu généré (titres, descriptions, instructions, étapes, commentaires) doit être rédigée **strictement en français**, à l'exception des champs YAML obligatoires et des termes techniques standards.
- **EXCEPTION :** Si l'utilisateur demande explicitement une compétence destinée à un projet public open source international (ex: publication sur *Awesome Copilot*), tu peux rédiger la compétence en anglais.

---

## 3. Architecture d'une compétence

Une compétence est un package de connaissances autonome contenu dans un répertoire dédié :

```text
nom-de-la-competence/
├── SKILL.md                 # (Obligatoire) Instructions principales et métadonnées
├── README.md                # (Optionnel) Documentation pour les utilisateurs humains
├── scripts/                 # (Optionnel) Scripts exécutables (Bash, Python, etc.)
├── references/              # (Optionnel) Fiches techniques, schémas ou docs statiques
├── resources/               # (Optionnel) Templates, données de support, snippets
└── examples/                # (Optionnel) Exemples concrets d'utilisation et attendus
```

---

## 4. Le fichier `SKILL.md` et le Frontmatter universel

Le fichier `SKILL.md` doit débuter impérativement par un en-tête YAML :

```yaml
---
name: nom-de-la-competence-en-kebab-case
description: Description courte et percutante (à la 3ème personne). Place les déclencheurs et mots-clés d'activation au début.
allowed-tools: shell
license: MIT
---
```

### Règles sur les champs YAML :
- `name` *(Optionnel mais fortement recommandé)* : Identifiant unique en minuscules séparé par des tirets (`kebab-case`). Doit correspondre au nom du dossier.
- `description` *(ABSOLUMENT OBLIGATOIRE)* : C'est l'élément lu en premier par toutes les IA pour décider de charger ou non la compétence.
  - Rédiger à la **troisième personne** (ex: *"Génère des tests unitaires...", "Analyse et résume des logs..."*).
  - Appliquer le principe de **front-loading** : placer les mots-clés déclencheurs dès le début de la description pour éviter qu'ils soient coupés si l'IA restreint le budget de contexte.
- `allowed-tools` *(Optionnel, utile pour GitHub Copilot)* : Spécifie les outils de terminal (ex: `shell` ou `bash`) pré-autorisés sans confirmation interactive répétée.
- `license` *(Optionnel)* : Type de licence (ex: `MIT`, `Apache-2.0`).

> *Note de compatibilité :* Les champs supplémentaires comme `allowed-tools` ou `license` sont simplement ignorés sans erreur par Antigravity et ChatGPT/Codex.

---

## 5. Règles de portabilité et de rédaction du contenu Markdown

1. **Formatage des liens et références :**
   - Utilise impérativement des **chemins relatifs** (ex: `[mon-script](scripts/mon-script.sh)` ou `./references/regles.md`).
   - N'utilise jamais de chemins absolus ni d'adresses `file:///` en dur dans les compétences générées, car elles brisent la portabilité entre machines et IA.
2. **Divulgation progressive (Progressive Disclosure) :**
   - Ne surcharge pas le `SKILL.md` principal. Déporte la documentation volumineuse, les spécifications ou les catalogues dans le dossier `references/`. L'agent ne lira ces fichiers que s'il en a besoin.
3. **Scripts "Boîtes noires" :**
   - Ne demande pas à l'agent de lire le code source des scripts dans `scripts/`. Indique-lui simplement comment les exécuter de manière déclarative (ex: *"Exécutez le script `./scripts/analyse.sh` en passant le fichier cible en argument"*).
4. **Focus Unique (Single Responsibility) :**
   - Une compétence doit accomplir **une tâche claire**. Si le besoin est trop large, crée plusieurs compétences modulaires.

---

## 6. Emplacements de sauvegarde

Demande toujours à l'utilisateur où enregistrer la compétence en suivant ces règles :

| Portée | Emplacement recommandé (Universel) | Emplacements spécifiques |
| :--- | :--- | :--- |
| **Projet (Local)** | `.agents/skills/<nom>/` *(Supporté par Antigravity, Copilot et Codex)* | `.github/skills/<nom>/` (Copilot uniquement) |
| **Utilisateur (Global)** | `~/.agents/skills/<nom>/` *(Supporté par Copilot et Codex)* | `~/.gemini/config/skills/<nom>/` (Antigravity)<br>`~/.copilot/skills/<nom>/` (Copilot) |

---

## 7. Spécificités des plateformes (Divulgation progressive)

Si l'utilisateur demande une optimisation ou un packaging dédié à une IA en particulier, consulte la fiche de référence correspondante dans le dossier `references/` de cette compétence :

- **Google Antigravity :** Consulte [references/antigravity.md](references/antigravity.md) pour les règles de l'IDE, la hiérarchie de configuration et les plugins Antigravity.
- **GitHub Copilot :** Consulte [references/github-copilot.md](references/github-copilot.md) pour `allowed-tools`, les commandes `gh skill` et le versioning.
- **OpenAI ChatGPT / Codex :** Consulte [references/chatgpt-codex.md](references/chatgpt-codex.md) pour la gestion du budget de contexte et le packaging en plugin (`agents/openai.yaml`).

---

## 8. Workflow de création (Ce que tu dois faire)

Quand l'utilisateur te demande de créer ou modifier une compétence :

1. **Analyser le besoin initial :** Évalue les informations déjà fournies et identifie les zones d'ombre parmi les 4 piliers clés.
2. **Cadrage interactif dynamique par Rounds :**
   - Mène l'interview par rounds courts (2 à 4 questions ciblées max avec options recommandées).
   - Arrête l'interview dès que les 4 piliers (Déclencheurs, E/S, Outillage/Emplacement, Robustesse) sont verrouillés.
3. **Valider les choix :**
   - L'environnement cible (Universel par défaut, ou Antigravity / Copilot / ChatGPT).
   - L'emplacement (Projet dans `.agents/skills/` ou Global).
4. **Consulter la référence :** Si une cible spécifique est demandée, charge la fiche correspondante dans `references/`.
5. **Générer les fichiers :**
   - Crée le dossier de la compétence.
   - Crée `SKILL.md` avec le frontmatter complet et les instructions structurées **en français**.
   - Ajoute les dossiers et fichiers de support nécessaires (`scripts/`, `references/`, `README.md`, etc.).
6. **Vérification :** Valide la syntaxe YAML, la portabilité des chemins relatifs et l'absence de références propriétaires rigides.
