# Guide d'utilisation OpenLegi

## Présentation

OpenLegi est un serveur MCP (Model Context Protocol) offrant un accès direct aux bases de données officielles de Legifrance. Il constitue la **source prioritaire** de cette compétence pour tous les textes et décisions accessibles via Legifrance.

**Principe fondamental** : Toute source accédée via OpenLegi est considérée comme **fiable** (données officielles Legifrance). La vérification anti-hallucination porte alors sur l'adéquation entre le résultat et l'usage qu'on en fait, non sur la fiabilité de la source elle-même.

## Disponibilité et chargement

### Détection
Au début de chaque tâche nécessitant des recherches dans les bases officielles, charger les outils OpenLegi via `tool_search` avec une requête comme « OpenLegi legifrance ».

### Si OpenLegi est indisponible
- Basculer intégralement sur **web_search** avec les sources fiables (voir `sources-fiables.md`)
- Informer l'utilisateur : « Les outils OpenLegi ne sont pas disponibles dans cette session. La recherche s'effectue via web_search sur les sources officielles. Les résultats peuvent être moins précis. »
- **Ne jamais bloquer la tâche** : l'indisponibilité d'OpenLegi ne doit pas empêcher l'exécution de la compétence.

## Outils disponibles (12)

### 1. `OpenLegi:lister_codes_juridiques`
**Usage** : Obtenir la liste complète des 67 codes juridiques disponibles.
**Paramètres** : Aucun.
**Quand l'utiliser** : Pour identifier le nom exact d'un code avant d'utiliser `rechercher_code` (le nom doit être EXACT).

### 2. `OpenLegi:rechercher_code`
**Usage** : Rechercher des articles au sein d'un code juridique spécifique.
**Paramètres** :
- `code_name` (obligatoire) : Nom exact du code (utiliser `lister_codes_juridiques` si doute)
- `search` (obligatoire) : Termes de recherche
- `champ` : ALL (défaut), TITLE, NUM_ARTICLE, ARTICLE, TEXTE
- `page_number`, `page_size` : Pagination
- `sort` : PERTINENCE (défaut), DATE_ASC, DATE_DESC
- `type_recherche` : TOUS_LES_MOTS_DANS_UN_CHAMP (défaut), EXACTE, UN_DES_MOTS, AUCUN_DES_MOTS, AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION

**Données retournées** :
- Identifiant article (LEGIARTI), CID article
- **État juridique** (VIGUEUR, ABROGE, etc.) — **EXPLOITER SYSTÉMATIQUEMENT** pour la vérification temporelle
- **Date début vigueur**, **Date fin vigueur** — idem
- Numéro d'article, chemin complet dans le code
- Texte intégral de l'article
- Articles cités
- Lien Legifrance

**Astuce** : Pour rechercher un article par numéro exact, utiliser `champ: "NUM_ARTICLE"` et `type_recherche: "EXACTE"`.

### 3. `OpenLegi:rechercher_jurisprudence_judiciaire`
**Usage** : Rechercher dans la jurisprudence judiciaire (Cour de cassation, cours d'appel).
**Paramètres** :
- `search` (obligatoire) : Termes de recherche
- `champ` : ALL, TITLE, ABSTRACTS, TEXTE, NUM_AFFAIRE
- `juridiction_judiciaire` : Filtre par juridiction (tableau JSON)
- `publication_bulletin` : Filtre par publication au Bulletin
- `panorama` : `true` pour métadonnées uniquement (évite les textes intégraux volumineux)
- `page_number`, `page_size` : Pagination
- `sort` : PERTINENCE (défaut), DATE_ASC, DATE_DESC

**Données retournées** :
- Identifiant (JURITEXT), juridiction, formation, nature
- Numéro d'affaire, date de décision, solution
- Plan de classement, résumé, textes cités
- Texte intégral (sauf si `panorama: true`)
- Lien Legifrance

**Astuce** : Pour rechercher par numéro de pourvoi, utiliser `champ: "NUM_AFFAIRE"` et `type_recherche: "EXACTE"`.

### 4. `OpenLegi:rechercher_jurisprudence_administrative`
**Usage** : Rechercher dans la jurisprudence administrative (Conseil d'État, CAA, TA).
**Paramètres** : Similaires à jurisprudence judiciaire, avec en plus :
- `publication_recueil` : Filtre par publication au Recueil Lebon
**Données retournées** : Structure identique, avec identifiant CETATEXT.
**Tri** : PERTINENCE (défaut), DATE_ASC, DATE_DESC

### 5. `OpenLegi:rechercher_decisions_constitutionnelles`
**Usage** : Rechercher les décisions du Conseil constitutionnel.
**Paramètres** : Similaires, avec `panorama` disponible.
**Tri** : PERTINENCE, DATE_ASC, DATE_DESC

### 6. `OpenLegi:rechercher_decisions_cnil`
**Usage** : Rechercher les décisions de la CNIL.
**Paramètres** : Similaires, avec `nature_delib` pour filtrer par type de délibération.
**Tri** : PERTINENCE, DATE_ASC, DATE_DESC

### 7. `OpenLegi:rechercher_dans_texte_legal`
**Usage** : Rechercher dans la base LODA (Lois, Ordonnances, Décrets, Arrêtés).
**Paramètres** :
- `search` (obligatoire) : Termes de recherche
- `text_id` : Identifiant d'un texte spécifique pour rechercher à l'intérieur
- `champ`, `page_number`, `page_size`
- `sort` : PERTINENCE, PUBLICATION_DATE_DESC, PUBLICATION_DATE_ASC, SIGNATURE_DATE_DESC, SIGNATURE_DATE_ASC
- `type_recherche`

**⚠️ ATTENTION** : Les paramètres de tri diffèrent de ceux des codes et de la jurisprudence.

### 8. `OpenLegi:recherche_journal_officiel`
**Usage** : Rechercher dans le Journal Officiel de la République Française.
**Paramètres** :
- `search` (obligatoire) : Termes de recherche
- `max_results` : Nombre maximum de résultats
- `text_types` : Filtre par type de texte (tableau JSON, ex : `["LOI", "DECRET"]`). Voir `lister_natures_textes_jorf`
- `emetteurs`, `ministeres` : Filtres par émetteur/ministère
- `date_publication` : Filtre par date
- `sort` : PERTINENCE, SIGNATURE_DATE_DESC, SIGNATURE_DATE_ASC, PUBLI_DATE_DESC, PUBLI_DATE_ASC
- `champ`, `type_recherche`

**ATTENTION CRITIQUE** : Appliquer systématiquement la Règle 5 du SKILL.md (qualification des sources JORF). Vérifier la nature de chaque document et qualifier sa portée juridique.

### 9. `OpenLegi:dernier_journal_officiel`
**Usage** : Obtenir les derniers Journaux Officiels publiés.
**Paramètres** :
- `nb_jo` : Nombre de JO à retourner
- `llm_formatter` : Formatage optimisé pour LLM

### 10. `OpenLegi:lister_natures_textes_jorf`
**Usage** : Lister les 86 natures de textes disponibles au JORF.
**Quand l'utiliser** : Pour identifier les valeurs valides du paramètre `text_types` de `recherche_journal_officiel`.

### 11. `OpenLegi:lister_emetteurs_jorf`
**Usage** : Lister les émetteurs/autorités disponibles pour les recherches JORF.
**Quand l'utiliser** : Pour filtrer les recherches JORF par émetteur spécifique.

### 12. `OpenLegi:rechercher_conventions_collectives`
**Usage** : Rechercher dans les conventions collectives (base KALI).
**Paramètres** : Similaires à `rechercher_dans_texte_legal`, avec `panorama` disponible.
**Tri** : PERTINENCE, DATE_ASC, DATE_DESC

## Paramètres de tri — Récapitulatif

| Base | Tris disponibles |
|------|-----------------|
| Codes (`rechercher_code`) | PERTINENCE, DATE_ASC, DATE_DESC |
| Jurisprudence judiciaire | PERTINENCE, DATE_ASC, DATE_DESC |
| Jurisprudence administrative | PERTINENCE, DATE_ASC, DATE_DESC |
| Décisions constitutionnelles | PERTINENCE, DATE_ASC, DATE_DESC |
| Décisions CNIL | PERTINENCE, DATE_ASC, DATE_DESC |
| LODA (`rechercher_dans_texte_legal`) | PERTINENCE, PUBLICATION_DATE_DESC/ASC, SIGNATURE_DATE_DESC/ASC |
| JORF (`recherche_journal_officiel`) | PERTINENCE, SIGNATURE_DATE_DESC/ASC, PUBLI_DATE_DESC/ASC |
| Conventions collectives | PERTINENCE, DATE_ASC, DATE_DESC |

**⚠️** Utiliser un tri invalide provoque une erreur explicite. En cas de doute, utiliser PERTINENCE (toujours valide).

## Stratégies de recherche optimales

### Recherche d'un article de code précis
1. `rechercher_code` avec `code_name` exact + `search` = numéro d'article + `champ: "NUM_ARTICLE"` + `type_recherche: "EXACTE"`
2. Vérifier l'état juridique (VIGUEUR/ABROGE) et les dates dans les métadonnées
3. Si article introuvable dans un code : vérifier le nom exact du code via `lister_codes_juridiques`

### Recherche jurisprudentielle thématique
1. `rechercher_jurisprudence_judiciaire` (ou `_administrative`) avec mots-clés thématiques + `sort: "DATE_DESC"` pour les décisions récentes
2. Pour une recherche de volume : utiliser `panorama: true` pour obtenir les métadonnées sans les textes intégraux
3. Compléter avec `web_search` sur Judilibre ou Arianeweb pour les décisions non trouvées

### Recherche d'un arrêt précis par numéro
1. `rechercher_jurisprudence_judiciaire` avec `champ: "NUM_AFFAIRE"` + `type_recherche: "EXACTE"` + `search` = numéro de pourvoi
2. Si introuvable : tenter web_search sur Judilibre ou Legifrance

### Veille juridique sur le JORF
1. `recherche_journal_officiel` avec termes de recherche + `sort: "PUBLI_DATE_DESC"` + filtre `text_types` selon les besoins
2. Pour les textes normatifs uniquement : `text_types: ["LOI", "DECRET", "ORDONNANCE", "ARRETE"]`
3. **Toujours qualifier la nature** du document retourné (Règle 5 du SKILL.md)

### Recherche de textes légaux (LODA)
1. `rechercher_dans_texte_legal` avec termes + `sort: "PUBLICATION_DATE_DESC"` pour les plus récents
2. Si identifiant texte connu : utiliser `text_id` pour rechercher à l'intérieur d'un texte spécifique

## Gestion des erreurs

### Erreurs de tri
Si message d'erreur « Tri 'X' invalide » : vérifier le tableau des tris ci-dessus et utiliser le tri correct pour la base concernée.

### Erreurs de nom de code
Si message d'erreur sur le nom du code : utiliser `lister_codes_juridiques` pour obtenir le nom exact.

### Résultats vides
- Vérifier l'orthographe et les termes de recherche
- Essayer avec `type_recherche: "UN_DES_MOTS"` (plus permissif)
- Élargir le champ de recherche (`champ: "ALL"`)
- Basculer sur web_search en complément

### Erreur de connexion
Si OpenLegi est totalement inaccessible :
- Signaler à l'utilisateur
- Basculer sur web_search + sources fiables
- Ne pas bloquer l'exécution de la tâche

## Intégration avec les règles de la compétence

### Anti-hallucination
- Les résultats OpenLegi proviennent directement de Legifrance : **source fiable**
- La vérification porte sur l'**adéquation** (est-ce le bon texte pour le bon usage ?) et le **statut temporel** (le texte est-il en vigueur ?)
- L'interdiction d'inventer des références reste absolue : utiliser OpenLegi pour trouver, pas pour « confirmer » une référence imaginée

### Applicabilité temporelle (Règle 4 du SKILL.md)
- **Exploiter systématiquement** les métadonnées « État juridique », « Date début vigueur », « Date fin vigueur » retournées par OpenLegi
- Ne jamais citer un article sans avoir vérifié ces champs

### Qualification JORF (Règle 5 du SKILL.md)
- **Vérifier systématiquement** la nature du document dans les résultats de `recherche_journal_officiel`
- Qualifier la portée juridique dans la citation (normatif vs travaux parlementaires vs administratif)
