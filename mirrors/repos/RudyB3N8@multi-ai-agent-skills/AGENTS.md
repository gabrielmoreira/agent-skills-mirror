# Instructions du dépôt pour les agents IA

## Contexte
- Dépôt de compétences portables pour agents IA de développement.
- Chaque compétence est principalement documentée dans son `SKILL.md`.
- Les compétences peuvent contenir des ressources optionnelles (`references/`, `resources/`, `scripts/`, `examples/`) et un `README.md`.
- Le README racine présente le catalogue et les méthodes d'installation par plateforme.

## Structure
- `agents-md-generator/` : création et maintenance d'instructions `AGENTS.md`.
- `aura-build-assistant/` : prompts Aura.build et import de code généré.
- `createur-de-competences/` : conception de compétences multi-IA.
- `grill-agent/` : revue contradictoire de l'analyse par un sous-agent.
- `grill-me/` : interview et cadrage contradictoires.
- `ui-ux-pro-max/` : recommandations de design d'interface.
- Consulter le `SKILL.md` concerné avant de modifier une compétence.

## Commandes et validation
- Aucun manifeste de dépendances, commande de build, test ou linter global n'est configuré.
- Ne pas inventer ni exécuter de commande de validation non documentée.
- Pour les changements Markdown, vérifier le diff, les liens relatifs et la cohérence avec la structure réelle.
- Pour les scripts, inspecter les dépendances et instructions propres à la compétence concernée.
- Ne pas lancer un script de génération/synchronisation sans besoin explicite et compréhension de ses effets.

## Conventions de contenu
- Conserver le frontmatter YAML existant des fichiers `SKILL.md` (notamment `name` et `description`).
- Garder le dossier de chaque compétence et le champ `name` cohérents.
- Traiter `SKILL.md` comme point d'entrée ; réserver les détails complémentaires aux ressources liées.
- Écrire des instructions factuelles, concises, non ambiguës et portables entre plateformes.
- Utiliser des chemins relatifs dans la documentation du dépôt.
- Maintenir les liens vers les ressources locales valides après tout déplacement ou renommage.
- Faire apparaître dans le README racine toute nouvelle compétence destinée au catalogue, avec un lien vers son `SKILL.md` et un résumé fidèle.
- Réutiliser les méthodes communes via des liens et contrats explicites plutôt que de maintenir des copies divergentes.
- Lorsqu'une méthode partagée évolue, vérifier ses compétences consommatrices et maintenir leur compatibilité.
- En particulier, toute évolution du contrat de `grill-me` doit être vérifiée par rapport à `grill-agent`.
- Respecter la langue et le style du fichier modifié.

## Garde-fous
- Préserver les changements préexistants de l'utilisateur ; ne pas les écraser ni les annuler.
- Ne pas ajouter de secrets, clés, données privées ou fichiers de configuration sensibles.
- Limiter les modifications à la demande ; conserver les ressources et le comportement des compétences sans changement intentionnel.
- Ne pas prétendre qu'un test, un lint ou un build a réussi s'il n'est pas configuré ou exécuté.

## Définition de terminé
- Les descriptions du README correspondent aux compétences présentes et leurs liens sont valides.
- Les fichiers `SKILL.md` conservent une structure et des références cohérentes.
- Le diff final ne contient que les changements demandés et les vérifications disponibles sont rapportées.
