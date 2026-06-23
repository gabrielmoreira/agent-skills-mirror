# Guide Themia — Données jurimétriques (dommage corporel et droit du travail)

## Déclenchement

Consulter ce guide dès qu'une question appelle des données statistiques, des montants d'indemnisation, ou des pratiques juridictionnelles quantifiées en dommage corporel ou en droit du travail.

| Signal | Module |
|---|---|
| Préjudice corporel, Dintilhac, DFP, souffrances endurées, DFT, ATP, barème capitalisation, victime, montant d'indemnisation corporelle | **Dommage corporel (DC)** |
| Licenciement, rupture, prud'hommes, faute grave, inaptitude, ancienneté, barème Macron, salarié protégé, indemnités prud'homales | **Droit du travail (Travail)** |
| « combien », « quel montant », « en moyenne », « médiane », « pratique des juridictions » | **Selon contexte DC ou Travail** |

Si ambiguïté sur le module : demander explicitement à l'utilisateur.

## Si Themia est indisponible

Informer l'utilisateur **une seule fois** que des données jurimétriques enrichies seraient disponibles via Themia (themia.pro), puis poursuivre avec les outils disponibles (OpenLegi, HAL, web_search). Ne jamais bloquer l'exécution.

## Périmètre Themia

Statistiques agrégées uniquement — pas de décisions individuelles (orienter vers OpenLegi), pas de barèmes normatifs. Les données décrivent ce qui a été accordé, pas ce qui doit l'être.

---

# MODULE 1 — DOMMAGE CORPOREL

## Outils DC

| Outil | Fonction |
|---|---|
| `Themia:compter_decisions_dommage_corporel` | Compter les décisions (vérifier N avant analyse) |
| `Themia:analyser_insights_dommage_corporel` | Outil principal d'analyse |
| `Themia:recherche_options_dommage_corporel` | Explorer valeurs et hiérarchie des postes/atteintes |

## Questions préalables DC

Regrouper en une seule interaction :

**Périmètre géographique** (si ville mentionnée) : [Ville] uniquement | National | [Ville] vs National.

**Filtres contextuels** :
- Fait générateur : `ACCIDENT_CIRCULATION`, `ACCIDENT_MEDICAL_ET_INFECTION_NOSOCOMIALE`, `ACCIDENT_TRAVAIL_ET_MALADIE_PROFESSIONNELLE`, `INFRACTION_PENALE`, `TERRORISME`, `AUTRE`
- Période, sexe de la victime, fourchette de DFP

Ne pas sur-filtrer. Vérifier N avec `compter_decisions`. Si N < 20, signaler et proposer l'élargissement.

## Clés composites DC — Postes fréquents

### Victime directe — extra-patrimoniaux temporaires
| Poste | Clé composite |
|---|---|
| D.F.T. | `direct_victim_indemnity_events-extra_patrimoniaux_temporaires-DEFICIT_FONCTIONNEL_TEMPORAIRE` |
| S.E. | `direct_victim_indemnity_events-extra_patrimoniaux_temporaires-SOUFFRANCES_ENDUREES` |
| P.E.T. | `direct_victim_indemnity_events-extra_patrimoniaux_temporaires-PREJUDICE_ESTHETIQUE_TEMPORAIRE` |

### Victime directe — extra-patrimoniaux permanents
| Poste | Clé composite |
|---|---|
| D.F.P. | `direct_victim_indemnity_events-extra_patrimoniaux_permanents-DEFICIT_FONCTIONNEL_PERMANENT` |
| P.E.P. | `direct_victim_indemnity_events-extra_patrimoniaux_permanents-PREJUDICE_ESTHETIQUE_PERMANENT` |
| P.A. | `direct_victim_indemnity_events-extra_patrimoniaux_permanents-PREJUDICE_AGREMENT` |
| P.S. | `direct_victim_indemnity_events-extra_patrimoniaux_permanents-PREJUDICE_SEXUEL` |
| P.E. | `direct_victim_indemnity_events-extra_patrimoniaux_permanents-PREJUDICE_ETABLISSEMENT` |
| P.P.E. | `direct_victim_indemnity_events-extra_patrimoniaux_permanents-PREJUDICE_PERMANENT_EXCEPTIONNEL` |

### Victime directe — patrimoniaux permanents
| Poste | Clé composite |
|---|---|
| D.S.F. | `direct_victim_indemnity_events-patrimoniaux_permanents-DEPENSES_SANTE_FUTURES` |
| F.L.A. | `direct_victim_indemnity_events-patrimoniaux_permanents-FRAIS_LOGEMENT_ADAPTES` |
| F.V.A. | `direct_victim_indemnity_events-patrimoniaux_permanents-FRAIS_VEHICULE_ADAPTE` |
| I.P. | `direct_victim_indemnity_events-patrimoniaux_permanents-INCIDENCE_PROFESSIONNELLE` |
| P.G.P.F. | `direct_victim_indemnity_events-patrimoniaux_permanents-PERTE_GAINS_PROFESSIONNELS_FUTURS` |

### Victime directe — patrimoniaux temporaires
| Poste | Clé composite |
|---|---|
| P.G.P.A. | `direct_victim_indemnity_events-patrimoniaux_temporaires-PERTE_GAINS_PROFESSIONNELS_ACTUELS` |

### A.T.P.
| Poste | Clé composite |
|---|---|
| A.T.P. temporaire | `atp_indemnity_events-patrimoniaux_temporaires-ASSISTANCE_TIERCE_PERSONNE_TEMPORAIRE` |
| A.T.P. permanente | `atp_indemnity_events-patrimoniaux_permanents-ASSISTANCE_TIERCE_PERSONNE_PERMANENTE` |

### Victimes indirectes
| Poste | Clé composite |
|---|---|
| Préjudice d'affection | `indirect_victim_indemnity_events-extra_patrimoniaux_indirectes-PREJUDICE_AFFECTION` |

Si poste absent : `recherche_options_dommage_corporel` (navigation 3 niveaux : `field="indemnity"` → `parent="direct_victim_indemnity_events"` → `parent="[catégorie]"`).

## Champs DC

**Catégoriels** : `jurisdiction`, `city`, `regimes` (tags), `victim_sex`, `is_deceased`, `is_aggravation`, `bareme_capitalisation_claim/offer/decision`, `incidence_professionnelle_components` (tags), `atteintes` (tags hiérarchiques), `sieges_blessures` (tags hiérarchiques).

**Numériques** : `dfp_percentage` (0–100), `souffrances_endurees_cotation` (0–7, pas 0.5), `prejudice_esthetique_temporaire_cotation` (0–7), `prejudice_esthetique_permanent_cotation` (0–7), `age_dommage`, `victim_age_at_decision`, `age_consolidated`, `age_deceased`, `fault_percentage_victim` (0–100), `loss_of_chance_percentage` (0–100).

**Date** : `date` — filtre `{"from": "...", "to": "..."}` et `date_histogram_field` pour trends.

---

# MODULE 2 — DROIT DU TRAVAIL

## Outils Travail

| Outil | Fonction |
|---|---|
| `Themia:compter_decisions_travail` | Compter les décisions |
| `Themia:analyser_insights_travail` | Outil principal d'analyse |
| `Themia:recherche_options_travail` | Explorer valeurs et hiérarchie des postes |

## Corpus Travail

~13 000 décisions. Juridiction unique : cour d'appel. Profondeur temporelle : essentiellement 2024–2026.

## Questions préalables Travail

**Périmètre géographique** (villes principales N>200) : Paris, Aix-en-Provence, Douai, Versailles, Montpellier, Lyon, Bordeaux, Nîmes, Toulouse, Rouen, Rennes, Orléans, Reims, Colmar, Grenoble, Dijon, Besançon, Chambéry.

**Filtres contextuels** :
- Type de rupture : `motif_personnel` | `motif_economique` | `requalification_du_contrat_de_travail` | `resiliation_ou_resolution_judiciaire` | `demande_de_prise_d_acte`
- Issue : `justified` | `nullite_sans_cause` | `nullite`
- Statut salarié : `cadre` | `cadre_dir` | `cadre_int` | `employe` | `ouvrier` | `technicien` | `agent_maitrise`
- Taille entreprise : `moins_de_11` | `moins_de_50` | `moins_de_500` | `moins_de_1000` | `plus_de_1000`
- CDI/CDD (`is_cdi`), salarié protégé (`is_protected_employee`)
- Fourchettes : salaire brut mensuel, ancienneté (**en mois**)

## Clés composites Travail — Postes d'indemnisation

### Indemnités de rupture
| Poste | Clé |
|---|---|
| Ind. licenciement (légale/conv.) | `indemnity_events-indemnites_rupture-licenciement_legale` |
| Ind. compensatrice de préavis | `indemnity_events-indemnites_rupture-preavis` |
| Ind. compensatrice congés payés | `indemnity_events-indemnites_rupture-conges_payes` |
| Ind. clause non-concurrence | `indemnity_events-indemnites_rupture-non_concurrence` |

### Dommages-intérêts
| Poste | Clé |
|---|---|
| D-I LSCRS | `indemnity_events-dommages_interets-licenciement_sans_cause` |
| D-I irrégulier (vice procédure) | `indemnity_events-dommages_interets-licenciement_vice_procedure` |
| D-I vexatoire | `indemnity_events-dommages_interets-licenciement_vexatoire` |
| D-I nul | `indemnity_events-dommages_interets-licenciement_nul` |
| D-I statut protecteur | `indemnity_events-dommages_interets-statut_protege` |
| D-I harcèlement | `indemnity_events-dommages_interets-harcelement` |
| D-I discrimination | `indemnity_events-dommages_interets-discrimination` |
| D-I obligation sécurité | `indemnity_events-dommages_interets-obligation_securite` |
| D-I obligation adaptation | `indemnity_events-dommages_interets-obligation_adaptation` |

### Rappels de salaires
| Poste | Clé |
|---|---|
| Rappel salaire impayé | `indemnity_events-rappels_remuneration-rappel_salaire` |
| Rappel heures sup | `indemnity_events-rappels_remuneration-heures_sup` |
| Rappel primes/bonus | `indemnity_events-rappels_remuneration-primes_bonus` |

### Licenciement économique
| Poste | Clé |
|---|---|
| Ind. supra-légale PSE | `indemnity_events-licenciement_economique-supra_legale` |
| D-I critères d'ordre | `indemnity_events-licenciement_economique-criteres_ordre` |
| D-I priorité réembauche | `indemnity_events-licenciement_economique-priorite_reembauche` |

### Inaptitude
| Poste | Clé |
|---|---|
| Ind. spéciale inaptitude pro | `indemnity_events-inaptitude-speciale_pro` |
| D-I défaut reclassement | `indemnity_events-inaptitude-defaut_reclassement` |

### CDD/intérim
| Poste | Clé |
|---|---|
| Ind. précarité | `indemnity_events-cdd_interim-prime_precarite` |
| Ind. requalification CDD→CDI | `indemnity_events-cdd_interim-requalification` |

### Autres
| Poste | Clé |
|---|---|
| D-I non-remise documents | `indemnity_events-autres-docs_fin_contrat` |
| Art. 700 CPC | `indemnity_events-autres-frais_irrepetibles` |
| Ind. forfaitaire travail dissimulé | `indemnity_events-travail_dissimule-forfait_6_mois` |

Si poste absent : `recherche_options_travail` (`field="indemnity"` → `parent="indemnity_events"` → `parent="indemnity_events/[head]"`).

## Champs Travail

**Catégoriels** : `type_de_rupture`, `motifs_de_licenciement_personnels` (multi, ~61% complétude), `nullity_dismissal`, `employee_role`, `employer_kind`, `company_size` (~58%), `employee_sex`, `city`, `jurisdiction`.

**Numériques** : `gross_monthly_salary` (médiane 2 384 €, 73% renseigné), `employee_tenure` (**en mois**, médiane 78 mois, 96%), `employee_age` (**en mois**, 51%).

⚠ **CONVERSION OBLIGATOIRE** : `employee_tenure` et `employee_age` en mois → convertir en années dans les rapports.

⚠ **LIMITATION** : `gross_monthly_salary` ne peut pas être utilisé en `breakdown_field`. Contournement : filtres successifs par fourchettes.

**Booléens** : `is_cdi`, `is_full_time`, `is_protected_employee`, `is_disabled_employee`, `is_pregnant_employee`, `has_children`, `has_employee_disciplinary_dossier`.

---

# SECTIONS COMMUNES

## Types d'insight

| Type | Usage | Paramètres requis |
|---|---|---|
| `metric` | Valeur agrégée globale | `breakdown_field` **INTERDIT** |
| `distribution` | Répartition catégorielle | `breakdown_field` obligatoire |
| `comparison` | Stats ventilées | `breakdown_field` obligatoire |
| `trend` | Évolution temporelle | `date_histogram_field` + `date_histogram_interval` |
| `correlation` | Croisement deux dimensions | `breakdown_field` + `secondary_breakdown_field` |

Agrégation recommandée : `series_aggregation: "stats"` (count, avg, min, max, P25, P50, P75, P90, P95, σ).

## Séquences-types

**Comparaison inter-juridictions** : compter → metric national → comparison par city.

**Distribution** : compter → distribution par variable.

**[Ville] vs National** : metric sans filtre → metric avec filtre city → tableau comparatif (P25/P50/P75/N/σ) → écart relatif.

**Profil salarié (Travail)** : compter → metric salaire → metric ancienneté (convertir mois→années) → distribution statut → distribution issue.

**Indemnisation (Travail)** : compter → metric poste → comparison par city → comparison par ancienneté (interval=24) → comparison par statut → trend si pertinent.

## Interprétation

- Médiane (P50) : indicateur central le plus robuste
- IQR (P25-P75) : zone de convergence centrale
- Écart-type élevé : hétérogénéité marquée — signaler
- Données `"redacted": true` : ne pas exploiter, signaler
- Valeur `__missing__` : exclure, signaler taux de complétude si significatif
- Valeur `-1` (cotations DC) : non renseigné — exclure

## Seuils d'alerte

| N | Conduite |
|---|---|
| < 5 | Ne pas exploiter |
| 5–20 | Exploitable avec mise en garde — proposer élargissement |
| 20–50 | Exploitable avec prudence |
| > 50 | Résultats robustes |

## Structure du rapport jurimétrique

1. Périmètre et corpus (N, filtres, précautions)
2. Analyses (résultats commentés, tableaux)
3. Observations synthétiques (enseignements, limites)

Mentionner le caractère descriptif (non normatif) des données dans l'en-tête. Ne pas le répéter dans le corps. Écrire le rapport en Word dans le dossier de travail.
