---
name: aura-build-assistant
description: Assiste l'utilisateur dans la conception de prompts optimisés pour l'IA d'Aura.build et dans l'importation propre du code généré (HTML, Tailwind CSS, JS) dans un dossier de staging local, avec option d'extraction SCSS.
---

# Assistant Aura.build AI

Cette compétence permet à l'agent d'aider l'utilisateur à exploiter au maximum l'IA d'Aura.build pour concevoir des sites web et des composants d'interface, puis d'importer le code de manière propre et structurée.

## Objectif global

Assister l'utilisateur à chaque étape du cycle de développement avec Aura.build :
1. Préparer des prompts optimisés respectant la charte graphique existante (utilisation de `DESIGN.md` et référencement contextuel `@`).
2. Générer des maquettes locales pour la fonctionnalité Image-to-HTML d'Aura.build.
3. Extraire, nettoyer et structurer le code HTML/CSS généré par Aura.build dans un dossier de transition (Staging) `./aura-imports/output/` en mode Tailwind CSS ou SCSS classique.

## Quand l'utiliser (Déclencheurs)

Cette compétence doit être activée lorsque l'utilisateur mentionne :
- La création ou la modification de composants via le site web **Aura.build** ou **Aura Editor**.
- Le besoin de générer un prompt de design pour Aura.build.
- Le besoin d'importer un fichier `.html` ou `.zip` téléchargé depuis Aura.build.
- Le besoin de traduire un design issu d'Aura.build de Tailwind vers SCSS classique.

---

## Instructions étape par étape

### Étape 1 : Analyser le projet local pour la cohérence graphique
Avant de générer un prompt pour Aura.build, examinez le style actuel du projet :
1. Recherchez les fichiers de configuration CSS/SCSS (ex: `index.css`, `tailwind.config.js`, `variables.scss`).
2. S'il n'existe pas de fichier `DESIGN.md` à la racine, proposez à l'utilisateur d'en générer un contenant l'ADN visuel du projet (couleurs primaires/secondaires, polices, espacements).
3. Indiquez à l'utilisateur qu'il pourra charger ou coller ce fichier `DESIGN.md` dans Aura.build et y faire référence avec `@DESIGN.md` dans son prompt pour forcer l'IA d'Aura à respecter la charte locale.

### Étape 2 : Aider au Prompting (Mode Compose & Image-to-HTML)
Selon le besoin de l'utilisateur :
- **Si l'utilisateur souhaite créer un nouveau composant à partir d'une idée visuelle :** Proposez de générer une maquette d'illustration au format image avec l'outil local de génération d'images. Donnez l'instruction à l'utilisateur d'importer cette image dans le convertisseur **Image-to-HTML** d'Aura.build.
- **Si l'utilisateur souhaite modifier un composant existant :** Préparez un prompt structuré incluant le code existant local et expliquez-lui comment le référencer en utilisant le symbole `@` dans Aura Editor.

### Étape 3 : Guider l'importation du code généré
Lorsque l'utilisateur est prêt à intégrer le code d'Aura.build :
1. Demandez-lui d'exporter le code depuis Aura.build (soit sous forme de fichier `.html` unique, soit sous forme de package `.zip`).
2. Demandez-lui de renommer le fichier avec le nom du composant ou de la page (ex: `pricing.html` ou `hero.zip`) et de le placer dans le dossier `./aura-imports/` à la racine de son espace de travail.
3. Demandez-lui s'il souhaite que le composant importé conserve le format **Tailwind CSS** natif d'Aura.build ou s'il souhaite extraire les styles en **SCSS classique**.
4. Exécutez le script d'importation automatique en lançant le script python :
   `python3 ~/.gemini/config/skills/aura-build-assistant/scripts/import-code.py --file <nom_du_fichier> --mode <tailwind/scss>`
   *(Le script est accessible ici : [import-code.py](./scripts/import-code.py))*
5. Montrez à l'utilisateur les fichiers propres générés dans `./aura-imports/output/<nom-du-composant>/` et expliquez-lui comment les intégrer.
   *Remarque : Si l'intégration du code importé dans le projet principal est complexe (nombreux fichiers modifiés, styles globaux), basculez d'abord en phase de Planification pour rédiger les artefacts de planification natifs (`implementation_plan.md` et `task.md`) avant de faire l'intégration.*

---

## Arbres de Décision

- **SI** le projet local utilise déjà Tailwind CSS :
  - **ALORS** recommandez d'importer en mode `tailwind`. Le HTML nettoyé sera directement exploitable.
- **SI** le projet local utilise SCSS ou du CSS classique :
  - **ALORS** recommandez d'importer en mode `scss`. Le script va mapper les classes, extraire les styles en ligne et générer un fichier `.scss` propre en plus du HTML sémantique.
- **SI** le fichier importé contient des scripts Spline ou des animations Matter.js :
  - **ALORS** signalez-le explicitement à l'utilisateur lors du rapport d'intégration afin de s'assurer que les bibliothèques JS sont correctement chargées localement.

---

## Bonnes Pratiques

- **Respecter la règle des 90/10** : Rappelez à l'utilisateur que le code importé d'Aura représente 90% du travail d'intégration (la structure et la réactivité responsive) et que les 10% restants (finitions, intégration logique, formulaires réels) doivent être finalisés manuellement ou avec l'aide d'Antigravity.
- **Nettoyage automatique** : Assurez-vous que le script d'importation supprime le fichier source temporaire du dossier `./aura-imports/` après un import réussi pour maintenir l'espace de travail propre.
