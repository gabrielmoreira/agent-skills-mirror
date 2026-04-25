# AGENTS.md

## Présentation du projet

Il s'agit d'un référentiel de programme éducatif pour enseigner les fondamentaux du développement web aux débutants. Le programme est un cours complet de 12 semaines développé par les Microsoft Cloud Advocates, comprenant 24 leçons pratiques couvrant JavaScript, CSS et HTML.

### Composants clés

- **Contenu éducatif** : 24 leçons structurées organisées en modules basés sur des projets  
- **Projets pratiques** : Terrarium, Jeu de frappe, Extension de navigateur, Jeu spatial, Application bancaire, Éditeur de code, et Assistant de chat IA  
- **Quiz interactifs** : 48 quiz avec 3 questions chacun (évaluations pré/post- leçon)  
- **Support multilingue** : Traductions automatiques en 50+ langues via GitHub Actions  
- **Technologies** : HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (pour projets IA)  

### Architecture

- Référentiel éducatif avec structure basée sur les leçons  
- Chaque dossier de leçon contient README, exemples de code, et solutions  
- Projets indépendants dans des répertoires séparés (quiz-app, divers projets de leçons)  
- Système de traduction utilisant GitHub Actions (co-op-translator)  
- Documentation servie via Docsify et disponible en PDF  

## Commandes d'installation

Ce référentiel est principalement destiné à la consommation de contenu éducatif. Pour travailler avec des projets spécifiques :

### Installation du référentiel principal

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Installation de l'application Quiz (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Démarrer le serveur de développement
npm run build      # Construire pour la production
npm run lint       # Exécuter ESLint
```

### API du projet bancaire (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Démarrer le serveur API
npm run lint       # Exécuter ESLint
npm run format     # Formater avec Prettier
```

### Projets d'extension de navigateur

```bash
cd 5-browser-extension/solution
npm install
# Suivez les instructions spécifiques au navigateur pour le chargement des extensions
```

### Projets de jeu spatial

```bash
cd 6-space-game/solution
npm install
# Ouvrez index.html dans un navigateur ou utilisez Live Server
```

### Projet de chat (Backend Python)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Définir la variable d'environnement GITHUB_TOKEN
python api.py
```

## Flux de développement

### Pour les contributeurs de contenu

1. **Forkez le référentiel** vers votre compte GitHub  
2. **Clonez votre fork** localement  
3. **Créez une nouvelle branche** pour vos modifications  
4. Modifiez le contenu des leçons ou les exemples de code  
5. Testez les modifications de code dans les répertoires de projets concernés  
6. Soumettez des pull requests en suivant les consignes de contribution  

### Pour les apprenants

1. Forkez ou clonez le référentiel  
2. Naviguez dans les dossiers de leçons dans l'ordre  
3. Lisez les fichiers README pour chaque leçon  
4. Complétez les quiz pré-leçon sur https://ff-quizzes.netlify.app/web/  
5. Travaillez les exemples de code dans les dossiers de leçons  
6. Réalisez les devoirs et défis  
7. Passez les quiz post-leçon  

### Développement en direct

- **Documentation** : Lancez `docsify serve` à la racine (port 3000)  
- **Application Quiz** : Lancez `npm run dev` dans le répertoire quiz-app  
- **Projets** : Utilisez l’extension Live Server de VS Code pour les projets HTML  
- **Projets API** : Lancez `npm start` dans les répertoires API concernés  

## Instructions de test

### Test de l'application Quiz

```bash
cd quiz-app
npm run lint       # Vérifier les problèmes de style de code
npm run build      # Vérifier que la compilation réussit
```

### Test de l'API bancaire

```bash
cd 7-bank-project/api
npm run lint       # Vérifiez les problèmes de style de code
node server.js     # Vérifiez que le serveur démarre sans erreurs
```

### Approche générale des tests

- Il s'agit d'un référentiel éducatif sans tests automatisés exhaustifs  
- Les tests manuels portent sur :  
  - Exécution des exemples de code sans erreurs  
  - Fonctionnement correct des liens dans la documentation  
  - Compilation réussie des projets  
  - Respect des bonnes pratiques dans les exemples  

### Vérifications avant soumission

- Lancez `npm run lint` dans les dossiers contenant package.json  
- Vérifiez la validité des liens markdown  
- Testez les exemples de code dans le navigateur ou Node.js  
- Vérifiez que les traductions conservent la structure appropriée  

## Directives de style de code

### JavaScript

- Utilisez la syntaxe moderne ES6+  
- Respectez les configurations ESLint standard fournies dans les projets  
- Utilisez des noms de variables et fonctions significatifs pour la clarté pédagogique  
- Ajoutez des commentaires expliquant les concepts pour les apprenants  
- Formatez avec Prettier si configuré  

### HTML/CSS

- Utilisez des éléments HTML5 sémantiques  
- Appliquez des principes de design responsive  
- Nommez clairement les classes  
- Ajoutez des commentaires expliquant les techniques CSS pour les apprenants  

### Python

- Suivez les directives de style PEP 8  
- Exemples de code clairs et pédagogiques  
- Indications de type lorsque cela aide l'apprentissage  

### Documentation Markdown

- Hiérarchie claire des titres  
- Blocs de code avec spécification du langage  
- Liens vers des ressources complémentaires  
- Captures d’écran et images dans les dossiers `images/`  
- Texte alternatif pour les images pour l’accessibilité  

### Organisation des fichiers

- Leçons numérotées séquentiellement (1-getting-started-lessons, 2-js-basics, etc.)  
- Chaque projet a les dossiers `solution/` et souvent `start/` ou `your-work/`  
- Images stockées dans des dossiers `images/` spécifiques aux leçons  
- Traductions dans la structure `translations/{code-langue}/`  

## Compilation et déploiement

### Déploiement de l'application Quiz (Azure Static Web Apps)

L'application quiz-app est configurée pour le déploiement avec Azure Static Web Apps :

```bash
cd quiz-app
npm run build      # Crée le dossier dist/
# Déploie via le workflow GitHub Actions lors d'un push sur main
```

Configuration Azure Static Web Apps :  
- **Emplacement de l'application** : `/quiz-app`  
- **Emplacement de sortie** : `dist`  
- **Workflow** : `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`  

### Génération du PDF de documentation

```bash
npm install                    # Installer docsify-to-pdf
npm run convert               # Générer un PDF à partir de docs
```

### Documentation Docsify

```bash
npm install -g docsify-cli    # Installer Docsify globalement
docsify serve                 # Servir sur localhost:3000
```

### Builds spécifiques aux projets

Chaque répertoire de projet peut avoir son propre processus de build :  
- Projets Vue : `npm run build` crée des bundles de production  
- Projets statiques : Pas d'étape de build, fichiers servis directement  

## Directives pour les pull requests

### Format du titre

Utilisez des titres clairs et descriptifs indiquant la zone modifiée :  
- `[Quiz-app] Ajout d’un nouveau quiz pour la leçon X`  
- `[Lesson-3] Correction d’une faute dans le projet terrarium`  
- `[Translation] Ajout de la traduction espagnole pour la leçon 5`  
- `[Docs] Mise à jour des instructions d’installation`  

### Vérifications requises

Avant de soumettre une PR :  

1. **Qualité du code** :  
   - Lancez `npm run lint` dans les répertoires de projet concernés  
   - Corrigez toutes les erreurs et avertissements de lint  

2. **Vérification de build** :  
   - Lancez `npm run build` si applicable  
   - Assurez-vous qu’aucune erreur de build ne survient  

3. **Validation des liens** :  
   - Testez tous les liens markdown  
   - Vérifiez le bon fonctionnement des références aux images  

4. **Relecture du contenu** :  
   - Corrigez l’orthographe et la grammaire  
   - Assurez-vous que les exemples de code sont corrects et pédagogiques  
   - Vérifiez que les traductions conservent le sens original  

### Exigences de contribution

- Acceptez la CLA Microsoft (vérification automatique à la première PR)  
- Respectez le [Code de conduite open source Microsoft](https://opensource.microsoft.com/codeofconduct/)  
- Consultez le [CONTRIBUTING.md](./CONTRIBUTING.md) pour les détails  
- Référencez les numéros d’issues dans la description de la PR si applicable  

### Processus de relecture

- Les PR sont revues par les mainteneurs et la communauté  
- La clarté pédagogique est priorisée  
- Les exemples de code doivent suivre les bonnes pratiques actuelles  
- Les traductions sont revues pour précision et adéquation culturelle  

## Système de traduction

### Traduction automatisée

- Utilise GitHub Actions avec le workflow co-op-translator  
- Traduit automatiquement en 50+ langues  
- Fichiers source dans les répertoires principaux  
- Fichiers traduits dans `translations/{code-langue}/`  

### Ajout d’améliorations manuelles aux traductions

1. Localisez le fichier dans `translations/{code-langue}/`  
2. Apportez des améliorations tout en préservant la structure  
3. Assurez-vous que les exemples de code restent fonctionnels  
4. Testez tout contenu de quiz localisé  

### Métadonnées des traductions

Les fichiers traduits incluent un en-tête de métadonnées :  
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

## Débogage et résolution de problèmes

### Problèmes courants

**L’application quiz ne démarre pas** :  
- Vérifiez la version de Node.js (v14+ recommandé)  
- Supprimez `node_modules` et `package-lock.json`, puis lancez `npm install` à nouveau  
- Vérifiez les conflits de ports (par défaut : Vite utilise le port 5173)  

**Le serveur API ne démarre pas** :  
- Vérifiez que Node.js est à la version minimale (node >=10)  
- Vérifiez si le port est déjà utilisé  
- Assurez-vous que toutes les dépendances sont installées via `npm install`  

**L’extension navigateur ne charge pas** :  
- Vérifiez que manifest.json est bien formatté  
- Consultez la console du navigateur pour les erreurs  
- Suivez les instructions d’installation spécifiques au navigateur  

**Problèmes du projet chat Python** :  
- Assurez-vous que le package OpenAI est installé : `pip install openai`  
- Vérifiez que la variable d’environnement GITHUB_TOKEN est définie  
- Vérifiez les autorisations d’accès aux modèles GitHub  

**Docsify ne sert pas la documentation** :  
- Installez docsify-cli globalement : `npm install -g docsify-cli`  
- Lancez depuis le répertoire racine du dépôt  
- Vérifiez que `docs/_sidebar.md` existe  

### Conseils pour l’environnement de développement

- Utilisez VS Code avec l’extension Live Server pour les projets HTML  
- Installez les extensions ESLint et Prettier pour un formatage cohérent  
- Utilisez les DevTools du navigateur pour déboguer JavaScript  
- Pour les projets Vue, installez l’extension Vue DevTools pour navigateur  

### Considérations de performance

- Le grand nombre de fichiers traduits (50+ langues) rend les clones complets volumineux  
- Utilisez un clone superficiel si vous travaillez uniquement sur le contenu : `git clone --depth 1`  
- Excluez les traductions des recherches quand vous travaillez sur le contenu anglais  
- Les processus de build peuvent être lents lors de la première exécution (npm install, build Vite)  

## Considérations de sécurité

### Variables d’environnement

- Les clés API ne doivent jamais être commises dans le référentiel  
- Utilisez des fichiers `.env` (déjà dans `.gitignore`)  
- Documentez les variables d’environnement requises dans les README projets  

### Projets Python

- Utilisez des environnements virtuels : `python -m venv venv`  
- Gardez les dépendances à jour  
- Les tokens GitHub doivent avoir les permissions minimales nécessaires  

### Accès aux modèles GitHub

- Tokens d’accès personnel (PAT) requis pour les modèles GitHub  
- Les tokens doivent être stockés en variables d’environnement  
- Ne jamais commettre de tokens ou d’identifiants  

## Notes supplémentaires

### Public cible

- Débutants complets au développement web  
- Étudiants et autodidactes  
- Enseignants utilisant le programme en classe  
- Contenu conçu pour l’accessibilité et le développement progressif des compétences  

### Philosophie éducative

- Approche par projets  
- Vérifications fréquentes des connaissances (quiz)  
- Exercices pratiques de programmation  
- Exemples d’applications réelles  
- Focus sur les fondamentaux avant les frameworks  

### Maintenance du référentiel

- Communauté active d’apprenants et contributeurs  
- Mises à jour régulières des dépendances et du contenu  
- Surveillance des issues et discussions par les mainteneurs  
- Mises à jour de traductions automatisées via GitHub Actions  

### Ressources associées

- [Modules Microsoft Learn](https://docs.microsoft.com/learn/)  
- [Ressources du Student Hub](https://docs.microsoft.com/learn/student-hub/)  
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) recommandé pour les apprenants  
- Cours additionnels : IA générative, Data Science, ML, IoT disponibles  

### Travailler avec des projets spécifiques

Pour des instructions détaillées sur les projets individuels, consultez les fichiers README dans :  
- `quiz-app/README.md` - application quiz Vue 3  
- `7-bank-project/README.md` - application bancaire avec authentification  
- `5-browser-extension/README.md` - développement d’extension navigateur  
- `6-space-game/README.md` - développement de jeu Canvas  
- `9-chat-project/README.md` - projet assistant chat IA  

### Structure Monorepo

Bien que ce ne soit pas un monorepo traditionnel, ce référentiel contient plusieurs projets indépendants :  
- Chaque leçon est autonome  
- Les projets ne partagent pas de dépendances  
- Travaillez sur des projets individuels sans impacter les autres  
- Clonez le référentiel complet pour l’expérience complète du programme

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Avertissement** :  
Ce document a été traduit à l’aide du service de traduction automatique [Co-op Translator](https://github.com/Azure/co-op-translator). Bien que nous nous efforcions d’assurer l’exactitude, veuillez noter que les traductions automatisées peuvent contenir des erreurs ou des inexactitudes. Le document original dans sa langue d’origine doit être considéré comme la source faisant autorité. Pour les informations critiques, une traduction professionnelle humaine est recommandée. Nous déclinons toute responsabilité en cas de malentendus ou d’interprétations erronées résultant de l’utilisation de cette traduction.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->