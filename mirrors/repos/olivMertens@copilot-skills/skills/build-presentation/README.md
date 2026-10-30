# Build Presentation

Un skill pour GitHub Copilot et Claude Code : préparer une présentation HTML,
ajuster son rendu dans le navigateur, puis produire un PowerPoint éditable.
Il peut aussi créer directement un PowerPoint.

Style : composition 16:9, diagrammes arrondis, typographie claire et
apparitions progressives. L'identité visuelle est résolue pour chaque deck ;
le blanc, le bleu et l'ambre constituent uniquement le repli neutre fourni.

Le skill conserve l'orthographe Unicode de la langue demandée. En français,
les accents, cédilles, ligatures et capitales accentuées restent présents dans
les slides, les contrôles et les notes : « accès », « façade », « cœur »,
« décision », « ÉTAPE ». Les icônes génériques suivent un style contour cohérent
de type Lucide ; les services Microsoft/Azure utilisent leurs icônes officielles
et les marques utilisent uniquement des actifs approuvés.

Le skill détermine une identité cohérente à partir d'une marque, d'un modèle ou
d'actifs explicitement approuvés. Avant de produire les slides, il résout la
marque ou le client visé, la source qui fait foi, la couleur dominante et la
politique d'icônes. Si ces informations sont absentes ou ambiguës, il pose une
question groupée au lieu de deviner une palette depuis un logo ou le nom du
dépôt. Les éléments non spécifiés utilisent le style Build uniquement après
acceptation de ce repli. Une fois la politique d'icônes validée, le skill choisit
lui-même les pictogrammes selon leur sens et conserve une seule famille visuelle.

## Icônes Lucide

Le skill utilise les **icônes Lucide** (licence ISC, libre, 5000+ pictogrammes) pour les concepts
génériques (Database, Workflow, Bot, ShieldCheck, etc.) et les icônes officielles Microsoft/Azure
pour les services nommés.

- **Source:** <https://lucide.dev> (copiez les chemins SVG)
- **Référence rapide:** Voir [`references/lucide-icons-reference.md`](references/lucide-icons-reference.md) 
  pour 30+ icônes communes prêtes à coller
- **Intégration:** Copiez-collez le chemin SVG inline, sans CDN (mode offline)
- **Exemple:** 
  ```html
  <svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
    <ellipse cx="12" cy="5" rx="9" ry="3"/>
    <path d="M3 5v14a9 3 0 0 0 18 0V5"/>
  </svg>
  ```

FontAwesome et autres n'offrent pas la même liberté d'intégration offline ; Lucide est préféré.

Référence visuelle publique :
<https://ozgurkarahan.com/agentic-platform/>

Ce paquet ne dépend d'aucun wiki privé. Il contient une méthode et un modèle,
pas un convertisseur universel ni un moteur IA. La création nécessite votre
propre environnement d'agent et les outils adaptés au format demandé.

## 1. Installer le skill

Décompressez le ZIP, puis copiez le dossier **build-presentation** entier
dans l'un des emplacements suivants. `~` désigne votre dossier utilisateur.

| Environnement | Emplacement |
|---|---|
| GitHub Copilot CLI ou app, tous vos projets | `~\.copilot\skills\build-presentation\` |
| GitHub Copilot, dans un seul projet | `<projet>\.github\skills\build-presentation\` |
| Claude Code, tous vos projets | `~\.claude\skills\build-presentation\` |
| Claude Code, dans un seul projet | `<projet>\.claude\skills\build-presentation\` |

Ces exemples utilisent la notation Windows. Sur macOS/Linux, utilisez les
mêmes dossiers avec les séparateurs de votre système.

Vérifiez que `SKILL.md` est directement dans ce dossier, sans un second
sous-dossier `build-presentation`. Si une version existe déjà, sauvegardez-la
et comparez-la avant de la remplacer.

Ouvrez une nouvelle session de l'agent dans le dossier de votre présentation.
Demandez-lui d'utiliser `build-presentation`. Dans Claude Code, vous pouvez
aussi saisir `/build-presentation`.

Si le skill n'est pas détecté, donnez à l'agent le chemin de `SKILL.md` et
demandez-lui de suivre ce fichier. Ne donnez pas seulement le modèle HTML :
les instructions et la charte font partie du skill.

Documentation des emplacements :
- <https://docs.github.com/en/copilot/concepts/agents/about-agent-skills>
- <https://code.claude.com/docs/en/skills>

## 2. Essayer le modèle sans agent

Ouvrez `assets\starter.html` dans un navigateur moderne. Les quatre slides
illustrent une carte conceptuelle, sa déclinaison concrète, un cycle de travail
et un zoom problème/réponse.

Utilisez les boutons, les flèches, PageUp/PageDown ou Home/End. Le bouton
**Static mode** désactive les apparitions. L'impression affiche toutes les
slides. Sans JavaScript, elles restent toutes accessibles.

Le modèle n'utilise ni CDN, ni compte, ni clé API et ne charge pas de ressources
distantes. Le lien vers la référence publique ne s'ouvre que si vous le suivez.
Les textes sont fictifs et doivent être remplacés pour une vraie présentation.

## 3. Créer une présentation HTML

Exemple à copier dans votre agent :

```text
Utilise build-presentation pour préparer une présentation de 15 minutes
sur [sujet], en français, destinée à [public].

Objectif : [ce que le public doit comprendre ou décider].
Sources autorisées : [documents ou liens publics].
Livrable : une présentation HTML autonome dans ce dossier.
Identité : [marque/client ou "neutre"], [charte/template faisant foi].
Dominante : [couleur exacte ou "propose avec validation"].
Icônes : [famille officielle, pictogrammes contour génériques, ou combinaison].

Propose d'abord le plan, avec un message et un diagramme par slide.
Attends ma validation du plan, puis génère l'HTML.
Vérifie le rendu de chaque slide et applique l'identité résolue ci-dessus.
N'invente ni chiffres, ni promesses produit, ni références clients.
```

Le nombre de slides doit servir le temps de parole et le message, pas remplir
un quota. Les sources de préparation restent séparées des textes projetés.

## 4. Produire le PowerPoint après validation de l'HTML

Dans la même session, après avoir validé l'HTML :

```text
Reprends la version HTML que je viens de valider et produis un fichier .pptx
éditable. Utilise le skill pptx si disponible, un canevas PowerPoint natif
ou un outil compatible avec des objets éditables.

Conserve les positions, couleurs et diagrammes du modèle.
Utilise de vrais textes, formes et connecteurs, pas une capture par slide.
Ajoute les notes orateur et les liens de sources.
Préfère des apparitions simples lorsque les animations HTML ne se transposent
pas fidèlement. Signale les substitutions de polices et les effets non repris.
Compare le rendu de chaque slide avec l'HTML avant livraison.
```

**Prérequis PowerPoint séparé :** votre agent doit disposer d'un outil de
création de `.pptx` éditables. Un skill `pptx`, un canevas natif ou une
bibliothèque comme PptxGenJS/python-pptx peuvent fournir cette capacité ;
leurs dépendances et méthodes de vérification dépendent de votre environnement.
Un skill est une instruction, pas une installation automatique de ces outils.

Le paquet ne redistribue pas le skill `pptx` tiers, ses scripts, les applications
Office ou les bibliothèques. Obtenez ces outils depuis leurs sources autorisées
et respectez leurs licences et les règles de votre organisation.

Références publiques possibles pour l'outillage, à choisir avec votre agent :
- <https://gitbrent.github.io/PptxGenJS/>
- <https://python-pptx.readthedocs.io/>

Sans cet outillage, l'agent doit signaler le blocage plutôt que livrer des images
en prétendant qu'il s'agit d'un PowerPoint éditable.

## 5. Polices, confidentialité et limites

- Polices prévues : Bricolage Grotesque, Instrument Sans et IBM Plex Mono.
  Les fichiers de polices ne sont pas inclus. Le modèle dispose de polices de
  remplacement. Une fidélité exacte nécessite les polices compatibles et les
  droits d'installation, de redistribution et d'incorporation appropriés.
- Aucun document client, lien privé, secret, identifiant de tenant ou historique
  de travail n'est inclus. Les nouveaux contenus restent sous votre contrôle.
- Les animations CSS ne sont pas toutes reproductibles dans PowerPoint.
  Des effets natifs simples ou un résultat statique lisible sont préférables
  à une fausse promesse de conversion identique.
- Le contrôle doit porter sur le rendu réel, les débordements, la lisibilité,
  l'éditabilité et les faits. Un fichier généré sans erreur n'est pas suffisant.
- La référence publique est une inspiration visuelle, pas une source à jour
  sur les produits, leur disponibilité, leurs prix ou leurs performances.
- Ce paquet n'est pas une annonce produit ni un modèle officiel Microsoft.
  Aucune publication, aucun envoi et aucune installation ne sont automatiques.

## Contenu

| Fichier | Rôle |
|---|---|
| `SKILL.md` | Point d'entrée de l'agent |
| `references\workflow.md` | Méthode, étapes et critères de livraison |
| `references\design-system.md` | Couleurs, polices, géométrie et diagrammes |
| `references\html-to-pptx.md` | Guide de reconstruction native HTML vers PPTX |
| `assets\starter.html` | Modèle autonome de quatre slides |
| `README.md` | Installation et prompts d'exemple |
