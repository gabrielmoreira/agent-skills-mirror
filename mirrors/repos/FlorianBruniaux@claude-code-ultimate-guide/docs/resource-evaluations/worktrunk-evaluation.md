# Evaluation: Worktrunk (worktrunk.dev)

**Date:** 2026-01-25 (Updated after deep-dive analysis)
**Evaluator:** Claude (Sonnet 4.5)
**Status:** ⚠️ Conditionally recommended (see updated conclusion)

## 📄 Résumé du contenu

- **Worktrunk** est un CLI Rust pour simplifier la gestion des git worktrees, créé par max-sixty (créateur de PRQL, 10K stars)
- Réduit la syntaxe de `git worktree add -b feat ../repo.feat && cd ../repo.feat` à `wt switch -c feat`
- 3 commandes core: `switch`, `remove`, `list` + hooks personnalisables + commit messages LLM
- **GitHub: 1.6K stars, 54 forks, 15 contributeurs, v0.18.2 (Jan 2026), 64 releases actives**
- Conçu spécifiquement pour les workflows multi-agents IA (Claude Code mentionné explicitement dans le README)

## 🎯 Score de pertinence (1-5)

| Score | Signification |
|-------|---------------|
| 5 | Essentiel - Gap majeur dans le guide |
| 4 | Très pertinent - Amélioration significative |
| 3 | Pertinent - Complément utile |
| 2 | Marginal - Info secondaire |
| 1 | Hors scope - Non pertinent |

**Score initial:** 2/5
**Score révisé après deep-dive:** 3/5

**Justification révisée:**

**Points conservés de l'évaluation initiale:**
- Le guide couvre déjà exhaustivement les git worktrees (Section 9.17, `/git-worktree` command)
- Worktrunk est un wrapper, pas une fonctionnalité fondamentale

**Nouvelles découvertes qui augmentent le score:**
1. **Besoin prouvé**: Multiples équipes ont créé des wrappers indépendants:
   - incident.io → custom bash wrapper `w` (blog post officiel)
   - Issue #1052 → Fish shell functions complètes
   - Worktrunk → Solution Rust mature (1.6K stars)
2. **Features uniques absentes de git vanilla:**
   - Project-level hooks pour automation
   - LLM-powered commit messages via `llm` tool
   - CI status tracking intégré
   - PR link generation
   - Path templates configurables
3. **Adoption significative**: 1.6K stars + 64 releases + multi-platform (Homebrew, Cargo, Winget, AUR)
4. **Pattern validé**: Le concept "wrapper worktree" est réinventé indépendamment par plusieurs équipes pro

## ⚖️ Comparatif détaillé

| Aspect | Worktrunk | Git vanilla + Notre guide | Wrappers custom (incident.io, #1052) |
|--------|-----------|----------------------------|---------------------------------------|
| Worktree basics | ✅ Simplifié (`wt switch`) | ✅ Complet (`git worktree add`) | ✅ Custom bash/fish functions |
| Safety (.gitignore) | ❌ Non mentionné | ✅ Vérification automatique | ⚠️ Dépend de l'implémentation |
| DB branching | ❌ Non couvert | ✅ Neon, PlanetScale, local | ❌ Non couvert |
| Hooks setup | ✅ Hooks intégrés | ✅ Auto-detect (Node, Rust, Python, Go) | ⚠️ Manuel |
| Cleanup | ✅ `wt remove` | ✅ Procédure complète + prune | ✅ Custom cleanup functions |
| LLM commits | ✅ Intégré via `llm` tool | ❌ Hors scope (orthogonal à CC) | ✅ Custom via LLM APIs |
| CI status tracking | ✅ Built-in | ❌ Non couvert | ❌ Non couvert |
| PR link generation | ✅ Built-in | ❌ Non couvert | ❌ Non couvert |
| Multi-agent context | ✅ Conçu pour | ✅ Section 9.17 couvre le workflow | ✅ Oui (incident.io use case) |
| Maintenance | ✅ 64 releases, actif | ✅ Git core (stable) | ❌ Custom code à maintenir |
| Installation | ✅ Multi-platform (Homebrew, Cargo, etc.) | ✅ Git déjà installé | ❌ Copy-paste scripts |

## 🔍 Deep-dive: Analyse des 4 sources

### Source 1: Worktrunk GitHub (github.com/max-sixty/worktrunk)

**Features validées:**
- Path templates configurables (réduit typing répétitif)
- Hooks project-level pour automation
- LLM integration via `llm` tool
- CI status + PR link generation
- Interactive worktree selection
- Shell integration (change directory capability)

**Adoption metrics:**
- 1.6K stars, 64 releases, 15+ contributeurs
- Multi-platform: macOS (Homebrew), Linux (Cargo/AUR), Windows (Winget)
- Créateur: max-sixty (PRQL 10K stars, Xarray maintainer)

### Source 2: incident.io blog (shipping-faster-with-claude-code-and-git-worktrees)

**Découvertes clés:**
- ❌ **N'utilise PAS Worktrunk** - ont créé leur propre wrapper bash `w`
- ✅ **Validation du pattern**: Git worktrees résout les "branch management friction"
- ✅ **ROI mesuré**: 18% improvement (30s) sur API generation time
- ✅ **Scale**: Multiple Claude instances en parallèle sans contention
- **Custom setup**: `w myproject new-feature claude` → auto-launch Claude in isolated branch

**Citation:**
> "Rather than constantly switching branches in a single repository, they maintain separate working directories for each feature branch—all connected to the same Git database."

### Source 3: Anthropic best practices (anthropic.com/engineering/claude-code-best-practices)

**Découvertes critiques:**
- ❌ **AUCUNE mention de Worktrunk** (contrairement à ce que j'avais suggéré initialement)
- ✅ **Git worktrees recommandés** comme approche officielle Anthropic:
  > "Git worktrees allow you to check out multiple branches from the same repository into separate directories."
- ✅ **3 approches recommandées**:
  1. Multiple checkouts (3-4 git clones)
  2. Git worktrees (focus de la recommandation)
  3. Custom harness + headless mode (`claude -p`)

**Best practices Anthropic:**
- Context isolation via `/clear`
- Specialized tool separation (coding vs review instances)
- CLAUDE.md inheritance across worktrees
- Conservative permissions approach

### Source 4: GitHub issue #1052 (claude-code repo)

**Découvertes:**
- ❌ **N'utilise PAS Worktrunk** - workflow Fish shell custom
- ✅ **Pattern workflow complet** avec 8 functions git custom:
  - `git worktree-llm` → create + start Claude
  - `git worktree-merge` → finish + rebase + merge
  - `git commit-llm` → LLM-generated commits
  - `git llm-message` → structured diff→commit via LLM
- ✅ **Issue status**: CLOSED as `NOT_PLANNED` (doc sharing, not feature request)
- ✅ **Author quote**: *"I now use it for basically all my development where I can use claude code"*

**Workflow pattern:**
```bash
git worktree-llm feature-name    # Start feature
# ... work with Claude ...
git worktree-merge                # Finish, commit, rebase, merge
```

## 🧩 Pattern émergent: "Wrapper Worktree" validé par 3 équipes indépendantes

| Équipe | Solution | Langage | Features clés |
|--------|----------|---------|---------------|
| incident.io | Custom `w` function | Bash | Auto-completion, auto-organize ~/projects/worktrees/ |
| Issue #1052 author | Fish functions | Fish shell | LLM commits, rebase automation, cleanup |
| Worktrunk (max-sixty) | CLI mature | Rust | Hooks, CI status, PR links, multi-platform |

**Conclusion**: Le besoin existe (3 réinventions indépendantes). Worktrunk est la solution la plus mature et feature-rich.

## 📍 Recommandations mises à jour

**Action: Intégration conditionnelle recommandée**

### Option 1: Section "Advanced Tooling" (Recommandée)

**Emplacement:** Section 9.17 (Multi-Instance Workflows) ou `/git-worktree` command

**Contenu proposé:**
```markdown
## Advanced Tooling (Optional)

While this guide teaches git worktree fundamentals, several teams have built wrappers for daily productivity:

### Worktrunk (Recommended wrapper)
- **What**: Rust CLI simplifying worktree management (1.6K stars, 64 releases)
- **Why**: Reduces `git worktree add -b feat ../repo.feat && cd ../repo.feat` to `wt switch -c feat`
- **Unique features**: Project hooks, LLM commits, CI status, PR links
- **Install**: `brew install worktrunk` (macOS/Linux) or `cargo install worktrunk`
- **Trade-off**: Learn git fundamentals first, add wrapper for speed later

### DIY Alternative
Teams like incident.io and others built custom bash/fish wrappers. See:
- [incident.io blog](https://incident.io/blog/shipping-faster-with-claude-code-and-git-worktrees)
- [GitHub issue #1052](https://github.com/anthropics/claude-code/issues/1052) (Fish shell functions)

**Philosophy**: Master `git worktree` concepts via this guide, then choose your productivity layer.
```

### Option 2: Simple "See Also" mention

**Emplacement:** Fin de `/git-worktree` command

**Contenu minimal:**
```markdown
## See Also
- [Worktrunk](https://github.com/max-sixty/worktrunk) - Productivity wrapper (1.6K stars)
- [incident.io workflow](https://incident.io/blog/shipping-faster-with-claude-code-and-git-worktrees) - Custom bash wrapper
```

## 🔥 Challenge (technical-writer) - Réponse mise à jour

**Score initial:** 2/5
**Score après deep-dive:** 3/5 ⬆️

**Éléments manqués dans l'évaluation initiale:**

1. **Pattern validation**: 3 équipes indépendantes ont créé des wrappers (incident.io, issue #1052, Worktrunk) → besoin réel
2. **Features uniques**: CI status, PR links, path templates, project hooks → pas disponibles en git vanilla
3. **Adoption sous-estimée**: 1.6K stars + 64 releases + multi-platform = mature, pas "marginal"
4. **Use case principal**: Daily productivity pour power users, pas "learning tool" (le guide couvre le learning)

**Risques de non-intégration mis à jour:**

| Risque | Probabilité | Impact | Mitigation recommandée |
|--------|-------------|--------|-------------------------|
| Users reinvent the wheel | **Medium** | Medium | Mentionner Worktrunk + DIY alternatives |
| Guide appears pedagogical only | **Medium** | Low | Ajouter section "Advanced Tooling" |
| Missing productivity gap | **High** | Medium | Guide enseigne patterns, Worktrunk booste workflow |
| Community expectation mismatch | Low | Low | Pattern validé par Anthropic (worktrees officiels) |

**Nouvelles découvertes qui augmentent la pertinence:**
- ✅ Anthropic recommande officiellement git worktrees (pas Worktrunk, mais le pattern)
- ✅ incident.io (blog officiel) démontre ROI mesurable (18% improvement)
- ✅ Multiple réinventions indépendantes prouvent le besoin
- ✅ Worktrunk est la solution la plus mature et cross-platform

## ✅ Fact-Check mis à jour

| Affirmation | Statut | Source | Corrections |
|-------------|--------|--------|-------------|
| 1.6K GitHub stars | ✅ Confirmé | GitHub repo (jan 2026) | - |
| Créé par max-sixty (PRQL author) | ✅ Confirmé | GitHub profile | - |
| v0.18.2 release (Jan 2026) | ✅ Confirmé | GitHub releases | - |
| Mentionné dans Anthropic best practices | ❌ **FAUX** | anthropic.com/engineering | **Correction**: Worktrunk n'est PAS mentionné. Seul git worktrees vanilla est recommandé. |
| 64 releases actives | ✅ Confirmé | GitHub releases | Découverte deep-dive |
| Multi-platform (Homebrew, Cargo, Winget, AUR) | ✅ Confirmé | GitHub README | Découverte deep-dive |
| incident.io utilise Worktrunk | ❌ **FAUX** | incident.io blog | **Correction**: Ils utilisent un wrapper bash custom `w`, pas Worktrunk |
| Issue #1052 concerne Worktrunk | ❌ **FAUX** | GitHub issue #1052 | **Correction**: Fish shell functions custom, pas Worktrunk |

**Corrections majeures apportées:**
1. ❌ **Anthropic best practices ne mentionnent PAS Worktrunk** (seul git worktrees vanilla)
2. ❌ **incident.io n'utilise PAS Worktrunk** (custom bash wrapper)
3. ❌ **Issue #1052 n'est PAS sur Worktrunk** (Fish shell workflow)
4. ✅ **Pattern validé**: 3 équipes ont créé des wrappers indépendamment → besoin réel existe

**Découvertes additionnelles:**
- Git Worktree Toolbox (MCP server, 3 stars) existe mais adoption trop faible
- Le pattern "wrapper worktree" est réinventé systématiquement par les power users
- Anthropic recommande officiellement les worktrees mais reste agnostique sur les wrappers

## 🎯 Décision finale mise à jour

**Score final:** 3/5 ⬆️ (pertinent - complément utile)

**Action:** Intégration conditionnelle recommandée (Option 1: Section "Advanced Tooling")

**Confiance:** Haute (fact-check approfondi, 4 sources analysées, corrections appliquées)

**Raisonnement révisé:**

**Pour l'intégration:**
1. **Besoin validé**: 3 équipes indépendantes ont créé des wrappers (pattern émergent)
2. **Solution mature**: Worktrunk est la plus feature-rich et cross-platform (1.6K stars, 64 releases)
3. **Gap pédagogique**: Guide enseigne fundamentals, users cherchent ensuite productivity boost
4. **Alignement philosophique**: "Learn patterns first, add tools for speed later" (teaching + tooling)
5. **ROI démontré**: incident.io a mesuré 18% improvement avec worktrees

**Contre l'intégration:**
1. ❌ Pas officiellement recommandé par Anthropic (seul vanilla worktrees l'est)
2. ✅ Guide couvre déjà exhaustivement les patterns git worktree
3. ✅ Philosophie "patterns > tools" doit rester prioritaire

**Compromis optimal:** Section "Advanced Tooling" qui:
- Enseigne d'abord les patterns git worktree (priority #1)
- Mentionne ensuite les wrappers mature (Worktrunk) + DIY alternatives
- Préserve la philosophie "learn fundamentals first"
- Offre un choix éclairé aux power users

---

## 📋 Implementation Recommendations

**Changes proposés:** Ajout section "Advanced Tooling (Optional)"

**Files à modifier:**

### Option A: Section 9.17 (Multi-Instance Workflows)
- **Fichier**: `guide/ultimate-guide.md`
- **Ligne**: ~10700 (après "Database Branch Workflow")
- **Contenu**: Section complète "Advanced Tooling" (voir Option 1 ci-dessus)
- **Impact**: ~15 lignes ajoutées

### Option B: `/git-worktree` command
- **Fichier**: `examples/commands/git-worktree.md`
- **Ligne**: ~210 (fin du document)
- **Contenu**: Section "See Also" minimale (voir Option 2 ci-dessus)
- **Impact**: ~3 lignes ajoutées

**Recommandation finale:** **Option A** (Section 9.17) car:
- Plus contextualisée (workflows multi-instance = use case principal)
- Permet d'expliquer le pattern "learn fundamentals → add productivity layer"
- Cohérent avec la découverte "3 équipes ont réinventé des wrappers"
- N'impacte pas la pédagogie du `/git-worktree` command (reste fundamentals-focused)

**Prochaines étapes:**
1. Validation user de l'approche (Option A vs Option B vs ignorer)
2. Rédaction du contenu final
3. Update de `machine-readable/reference.yaml` si Section 9.17 modifiée
4. Commit: `docs: add advanced worktree tooling section (Worktrunk + DIY alternatives)`
