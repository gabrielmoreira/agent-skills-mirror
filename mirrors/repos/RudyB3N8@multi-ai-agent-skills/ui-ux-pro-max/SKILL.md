---
name: ui-ux-pro-max
description: Génère des systèmes de design intelligents et recommande des styles UI, palettes de couleurs et typographies adaptés à chaque projet.
---

# UI UX Pro Max

## Objectif global
Cette compétence fournit une intelligence de conception (design intelligence) pour construire des interfaces UI/UX professionnelles sur de multiples plateformes. Elle génère des systèmes de design sur mesure, recommande des palettes de couleurs, des polices et des styles UI selon la nature du projet (ex: SaaS, E-commerce, Finance, Santé, etc.).

## Quand l'utiliser
Active cette compétence dès que l'utilisateur te demande de :
- Créer ou concevoir une interface utilisateur (ex: "Crée une landing page pour mon SaaS").
- Créer un tableau de bord (dashboard) ou une application mobile.
- Améliorer ou évaluer le design d'une interface existante.
- Obtenir des recommandations de couleurs, typographie ou style visuel.

## Instructions étape par étape

La compétence repose sur un moteur de recherche et de génération écrit en Python. **Tu ne dois pas lire ou analyser le code source Python**. Utilise-le simplement comme un script via ton outil d'exécution de commandes (`run_command`), en appelant le point d'entrée suivant :
[search.py](./scripts/search.py)

### 1. Générer un système de design complet (Recommandé)
Pour obtenir un système de design complet (Pattern, Style, Couleurs, Typographie) basé sur la demande de l'utilisateur, exécute la commande suivante en adaptant la `<requête>` et le `<nom_projet>` :
```bash
python3 ~/.gemini/config/skills/ui-ux-pro-max/scripts/search.py "<requête>" --design-system -p "<nom_projet>" -f markdown
```
*Exemple : `python3 ~/.gemini/config/skills/ui-ux-pro-max/scripts/search.py "fintech banking" --design-system -p "MaBanque" -f markdown`*

### 2. Recherche spécifique par domaine (Optionnel)
Si l'utilisateur pose une question très précise (ex: uniquement sur la typographie), tu peux chercher dans un domaine ciblé :
```bash
python3 ~/.gemini/config/skills/ui-ux-pro-max/scripts/search.py "<requête>" --domain <domaine>
```
**Domaines disponibles :**
- `product` : Recommandations contextuelles selon le type de produit.
- `style` : Styles UI associés (ex: glassmorphism, minimalism).
- `typography` : Recommandations et associations de polices (Google Fonts).
- `color` : Palettes de couleurs harmonieuses pour le secteur.
- `landing` : Structure recommandée pour les pages d'atterrissage.
- `chart` : Choix de graphiques pour des tableaux de bord Analytics.
- `ux` : Bonnes pratiques UX et anti-patterns à éviter.

### 3. Recherche spécifique par framework/stack (Optionnel)
```bash
python3 ~/.gemini/config/skills/ui-ux-pro-max/scripts/search.py "<requête>" --stack <stack>
```
**Stacks supportées :** `html-tailwind` (par défaut), `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, etc.

## Arbre de décision
- **Si l'utilisateur demande une interface complète ou structurée (ex: Landing page, application entière) :** Génère un système de design (`--design-system -f markdown`). Analyse le Markdown généré, et sers-t'en comme source de vérité (couleurs, bordures, ombres, polices) pour écrire ou refactoriser le code demandé.
- **Si l'utilisateur demande une simple amélioration ou un avis sur une maquette :** Utilise les options `--domain style` ou `--domain ux` pour chercher des best practices appropriées au contexte, puis rends un rapport constructif.

## Bonnes Pratiques et Alternatives
- **Fidélité stricte :** Utilise scrupuleusement les couleurs exactes (codes HEX) et les styles retournés par l'outil, ne les invente pas toi-même.
- **Pédagogie et Alternatives :** Si la demande de l'utilisateur contient des anti-patterns évidents pour un secteur (ex: "Je veux du vert néon pour une interface de soins palliatifs"), signale l'écart subtilement, mais propose immédiatement des palettes plus professionnelles retournées par la commande Python. Sois constructif et toujours centré sur la qualité de l'expérience utilisateur finale.
