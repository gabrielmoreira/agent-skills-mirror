# Principes cardinaux — Anti-hallucination et vérification

## Règle fondamentale

Il est **strictement interdit** de générer, créer ou inventer une référence juridique. Toute référence citée doit avoir été préalablement trouvée par une recherche effective (OpenLegi, HAL, web_search).

## Processus obligatoire en 3 étapes

L'ordre est impératif et ne souffre aucune exception :

1. **CHERCHER** : Lancer une recherche (OpenLegi en priorité, HAL pour la doctrine, web_search en complément)
2. **TROUVER** : Identifier un résultat correspondant, vérifier ses métadonnées (existence, date, juridiction, numéro, statut temporel)
3. **CITER** : Citer avec le lien hypertexte vers la source

## Ce qui est interdit

- Créer une référence puis la vérifier (inversion du processus)
- Citer de mémoire sans recherche préalable, même si la certitude subjective est élevée
- Inventer des références pour atteindre un nombre demandé par l'utilisateur
- Générer un numéro de pourvoi, un numéro RG, un numéro de requête, un numéro de décision
- Attribuer une date, une formation, ou un résumé à une décision sans l'avoir consultée

## Gestion du manque de références

Si le nombre de références trouvées est inférieur au nombre souhaité :
1. Citer uniquement les références effectivement trouvées et vérifiées
2. Indiquer le nombre réel : « J'ai trouvé N références sur ce point. »
3. Proposer d'élargir les recherches (autre période, autres juridictions, termes connexes)
4. Ne jamais inventer pour compléter

## Terminologie

- **Référence vérifiée** : trouvée par recherche, métadonnées concordantes
- **Référence non trouvée** : non localisée après recherches (≠ fausse, ≠ inexistante)
- Ne jamais qualifier une référence de « fausse », « incorrecte » ou « erronée » — seulement « non trouvée » ou « non vérifiée »

## Sources et outils

**OpenLegi (prioritaire)** — Toute source accédée via OpenLegi est fiable (données officielles Legifrance).
- Textes : `rechercher_code`, `rechercher_dans_texte_legal`, `recherche_journal_officiel`
- Jurisprudence judiciaire : `rechercher_jurisprudence_judiciaire`
- Jurisprudence administrative : `rechercher_jurisprudence_administrative`
- Conseil constitutionnel : `rechercher_decisions_constitutionnelles`
- CNIL : `rechercher_decisions_cnil`
- Conventions collectives : `rechercher_conventions_collectives`

**HAL (doctrine)** — Métadonnées fiables (dépôts vérifiés). Utiliser via `scripts/hal_search.py`.

**web_search (complément)** — Sources fiables uniquement (voir `references/sources-fiables.md`). Indispensable pour : doctrine non déposée sur HAL, CEDH, CJUE, actualité juridique.

## Vérification temporelle (rappel condensé)

Chaque texte cité doit être qualifié temporellement (en vigueur, abrogé, futur). Exploiter les métadonnées OpenLegi (état juridique, date début/fin vigueur). Voir le §7 du SKILL.md pour le détail.

## Qualification des sources JORF

Le Journal officiel contient des documents de nature diverse. Qualifier systématiquement :
- **Normatif** (loi, ordonnance, décret, arrêté) : citable comme droit positif
- **Travaux parlementaires** (questions écrites, rapports, avis) : citable uniquement comme élément d'interprétation
- **Documents administratifs** (circulaires, communiqués) : qualifier au cas par cas

Ne jamais citer « selon le Journal officiel » sans préciser la nature du document.
