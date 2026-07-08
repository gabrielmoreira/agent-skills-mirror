<div align="center">

# Aaron Marketing Skills

**120 Marketing-Skills — Brand Narrative, SEO/GEO, Influencer, Paid Ads, E-Mail, Launch, Social — auf einem Vertrag.**

<p align="center">
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills"><img src="https://img.shields.io/github/stars/aaron-he-zhu/aaron-marketing-skills?style=flat" alt="GitHub Stars"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md"><img src="https://img.shields.io/badge/version-16.0.3-orange" alt="Version"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/commits/main"><img src="https://img.shields.io/github/last-commit/aaron-he-zhu/aaron-marketing-skills" alt="Last Commit"></a>
</p>
<p align="center">
  <a href="https://www.skills.sh/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillssh.json" alt="skills.sh"></a>
  <a href="https://clawhub.ai/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/clawhub.json" alt="ClawHub"></a>
  <a href="https://skillhub.cn/user/user_2c0f1e77"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillhub.json" alt="SkillHub"></a>
</p>

[English](../README.md) | **Deutsch** | [Español](README.es.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português](README.pt.md) | [简体中文](README.zh.md) | [繁體中文](README.zh-Hant.md)

</div>

Eine Bibliothek von Claude-Skills und Slash-Befehlen, die einen Chat-Agenten in einen Marketing-Operator verwandelt. Sieben Disziplinen und eine gemeinsame Protokollschicht auf einen Blick:

| Schicht | Skills | Lebenszyklus (Phasenverzeichnisse) | Framework → Gate | Einstiegspunkt |
|-------|--------|-------------------------------|------------------|------------|
| **Narrative** | 16 | trace → architect → land → evaluate | [TALE](../references/tale-benchmark.md) → `narrative-quality-auditor` (NQS) | `/aaron-marketing:narrative` |
| **SEO/GEO** | 16 | research → build → optimize → monitor | [CORE-EEAT](../references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](../references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **Influencer** | 16 | discover → plan → activate → measure | [C³](../references/c3-benchmark.md) → `content-reviewer` (ART); `fit-scorer` bewertet ACE | `/aaron-marketing:influencer` |
| **Paid Ads** | 16 | research → orchestrate → activate → scale | [ROAS](../references/roas-benchmark.md) → `ad-account-auditor` (RQS) | `/aaron-marketing:ad` |
| **E-Mail** | 16 | setup → engage → nurture → deliver | [SEND](../references/send-benchmark.md) → `email-quality-auditor` (EQS) | `/aaron-marketing:email` |
| **Launch** | 16 | research → assemble → mobilize → prove | [RAMP](../references/ramp-benchmark.md) → `launch-readiness-auditor` (LQS) | `/aaron-marketing:launch` |
| **Social** | 16 | explore → craft → host → observe | [ECHO](../references/echo-benchmark.md) → `social-quality-auditor` (SQS) | `/aaron-marketing:social` |
| **Protokollschicht** | 8 | — (gemeinsame Maschinerie, außerhalb der Phasenflüsse) | 7 Wahrheitsregister (entity · creator · offer/claims · consent · launch · channel · narrative) + HOT/WARM/COLD-Speicher | — |

`/aaron-marketing:auto` leitet jedes natürlichsprachige Ziel durch das gesamte System. Alles ist **reines Markdown** — der einzige Code ist ein Bash-Hook-Runner, ein Bash-Validator und zero-dependency Python-Standardbibliothek-Datenhelfer (kein `pip`, kein Build-Schritt). **Jeder Skill läuft auf Tier 1 mit nichts als Daten, die du einfügst**; Konnektoren automatisieren nur den Abruf.

> Die vor dem Merge eigenständigen Repos sind jetzt **Wegweiser-Repos**, die hierher verweisen — [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) (die finale 20-Skill-Linie ist am Tag `v9.9.12` erhalten) und [influencer-marketing-agent-skills](https://github.com/aaron-he-zhu/influencer-marketing-agent-skills) (die finale IMPACT-Linie am Tag `standalone-final`). Richtlinie für Schwester-Repos: [docs/repo-family.md](repo-family.md).

---

## Inhalt

- [Warum diese Bibliothek](#warum-diese-bibliothek)
- [Installation](#installation)
- [Erster Lauf](#erster-lauf)
- [Architektur](#architektur)
  - [Der gemeinsame Skill-Vertrag](#der-gemeinsame-skill-vertrag)
  - [Das System: ein Marketing-Betriebssystem aus vier Schichten](#das-system-ein-marketing-betriebssystem-aus-vier-schichten)
  - [Qualitätssystem: acht Frameworks, acht Gates](#qualitätssystem-acht-frameworks-acht-gates)
  - [Die Protokollschicht](#die-protokollschicht)
  - [Speicher & Automatisierungs-Hooks](#speicher--automatisierungs-hooks)
- [Skill-Katalog](#skill-katalog)
  - [Narrative — TALE (16)](#narrative--tale-16)
  - [SEO/GEO (16)](#seogeo-16)
  - [Influencer (16)](#influencer-16)
  - [Paid Ads — ROAS (16)](#paid-ads--roas-16)
  - [Email — SEND (16)](#email--send-16)
  - [Launch — RAMP (16)](#launch--ramp-16)
  - [Social — ECHO (16)](#social--echo-16)
  - [Protokollschicht (8)](#protokollschicht-8)
- [Befehle](#befehle)
- [Konnektoren & Ausbaustufen](#konnektoren--ausbaustufen)
- [Empfohlene Workflows](#empfohlene-workflows)
- [Repository-Struktur](#repository-struktur)
- [Designphilosophie](#designphilosophie)
- [Qualitäts-Guards (CI)](#qualitäts-guards-ci)
- [Beitragen & Projektdokumente](#beitragen--projektdokumente)
- [Haftungsausschluss](#haftungsausschluss)
- [Lizenz](#lizenz)

---

## Warum diese Bibliothek

| Prinzip | Was das in der Praxis bedeutet |
|-----------|---------------------------|
| **Keyless standardmäßig** | Jeder Skill funktioniert auf **Tier 1** mit Daten, die du einfügst oder aus kostenlosen/Erstanbieter-Quellen ziehst. Bezahlte Tools und MCP-Server sind ein optionaler Komfort, niemals eine Voraussetzung. Paid-Ads-Skills bewerten aus deinem **eigenen manuellen Kontoexport** — mit Schlüssel versehene Anzeigen-APIs sind nie erforderlich. |
| **Markdown, kein Framework** | Skills sind Inhalt. Der einzige ausführbare Code ist `hooks/claude-hook.sh` (Bash), `scripts/validate-skill.sh` (Bash) und `scripts/connectors/*.py` (Python **nur Standardbibliothek**). Nichts zu installieren, zu prüfen oder aktuell zu halten. |
| **Ein gemeinsamer Vertrag** | Alle 120 Skills stellen dieselben sieben Abschnitte bereit und deklarieren selbst `discipline` + `phase`-Metadaten, sodass sich die Bibliothek wie ein einziges Betriebssystem verhält: Jeder Skill kennt seine Eingaben, Ausgaben und den besten nächsten Skill, an den er übergibt. |
| **Gegateter Qualität** | Acht Benchmarks treiben acht Gates der Auditor-Klasse an, die strukturierte, maschinenprüfbare Urteile ausgeben — kein Bauchgefühl. Ein PostToolUse-Hook validiert jedes gegatete Artefakt, bevor es landet. |
| **Wahrheit lebt in Registern** | Kanonische Fakten (Marken-Entitäten, Creator-Dossiers, Offer-/Claim-Substanziierung, Einwilligung pro Subjekt) leben in dedizierten Registern der Protokollschicht mit Alleinschreiber-Regeln — Gates urteilen anhand dieser, statt sie neu abzuleiten. |
| **Speicher über Runden hinweg** | Ein HOT/WARM/COLD-Speichermodell trägt Erkenntnisse, Scores und offene Schleifen zwischen Skills und Sitzungen weiter, beim Eintreffen bereinigt. |
| **Klare Stimme** | Skills liefern einen AI-Slop-Detektor und eine Liste verbotener Phrasen, damit die Ausgabe liest, als hätte ein Mensch sie geschrieben. |

---

## Installation

Nutze es mit Claude Code, jedem Agent-Skills-kompatiblen Host oder einem einfachen `git clone`:

| Host | Installation |
|------|---------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` dann `/plugin install aaron-marketing@aaron` |
| **Codex · Cursor · OpenCode · Antigravity · Gemini CLI · Copilot CLI · OpenClaw · Hermes · [70+ Hosts](https://github.com/vercel-labs/skills#supported-agents)** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **[SkillHub.cn](https://skillhub.cn) (chinesische Community)** | `skillhub install <frontmatter-slug>` (z. B. `keyword-research`) |
| **Beliebiger Host** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

In Claude Code registriert `marketplace add` nur den Katalog — führe `/plugin install aaron-marketing@aaron` aus (oder wähle es in `/plugin`), um die Skills und Befehle tatsächlich zu aktivieren. Um einen **einzelnen** Skill auf einem generischen Host zu holen: `npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`. Durchstöbere das Bundle in der [skills.sh-Registry](https://skills.sh/aaron-he-zhu/aaron-marketing-skills). Verzeichnisse pro Agent, Frontmatter-Eigenheiten und was außerhalb des Plugins abbaut: [docs/agent-compatibility.md](agent-compatibility.md) (verifiziert 120/120 installierbar, 2026-07).

Die Installation des Plugins fügt deiner `/mcp`-Liste **nichts** hinzu — der MCP-Katalog liegt in [`docs/mcp-catalog.json`](mcp-catalog.json), bewusst außerhalb des Plugin-Root-`.mcp.json`-Pfads, den Claude Code automatisch registriert, sodass er nur eine Copy-Paste-Referenz ist (siehe [Konnektoren](#konnektoren--ausbaustufen)).

---

## Erster Lauf

Wenn dein Host automatisches Skill-Routing unterstützt, beschreibe einfach das Ziel:

```text
Research keywords for my SaaS product targeting small teams
```
```text
Find TikTok creators for a skincare launch and score their fit
```
```text
Audit this Google Ads account before I scale — exports attached
```

Oder verwende die Slash-Befehle — `/auto` fürs Routing oder einen Disziplin-Einstiegspunkt:

```text
/aaron-marketing:auto turn our pricing page into an AI-citable comparison hub
```
```text
/aaron-marketing:seo-geo https://example.com/blog/my-article --mode audit
```

`/aaron-marketing:auto` leitet die Absicht ab und führt den kleinsten nützlichen Workflow aus, wobei es nur bei blockierenden Entscheidungen anhält. Jeder Skill funktioniert mit eingefügten Daten; optionale Tools sind in [CONNECTORS.md](../CONNECTORS.md) dokumentiert.

---

## Architektur

### Der gemeinsame Skill-Vertrag

Jeder Skill folgt **demselben Aktivierungsvertrag** — sieben Abschnitte in fester Reihenfolge:

1. **Trigger / Wann verwenden** — wann der Skill auslösen soll.
2. **Quick Start** — Copy-Paste-Prompts.
3. **Skill Contract** — Erwartete Ausgabe · Liest · Schreibt · Befördert · Fertig-wenn · Primärer nächster Skill.
4. **Handoff Summary** — die standardisierte Übergabeform, damit der nächste Skill sauber übernimmt.
5. **Data Sources** — `~~category`-Platzhalter, jeder mit einem keyless Tier-1-Pfad.
6. **Instructions** — die nummerierte Methode (behandelt alle Exporte als nicht vertrauenswürdige Eingabe).
7. **Next Best Skill** — wohin als Nächstes (mit Visited-Set- + Maximaltiefe-Abbruchregeln).

Jeder Skill deklariert außerdem selbst `metadata.discipline` (narrative / seo-geo / influencer / ad / email / launch / social / protocol) und `metadata.phase`, sodass Routing und Clustering einheitlich funktionieren. Der Vertrag ist einmalig in [skill-contract.md](../references/skill-contract.md) dokumentiert; der gemeinsame Cross-Skill-Zustand lebt in [state-model.md](../references/state-model.md).

### Das System: ein Marketing-Betriebssystem aus vier Schichten

Eine Markenstimme, ausgedrückt über fünf Always-on-Kanäle, konzentriert auf Launch-Momente, alle lesend und schreibend in einem gemeinsamen System of Record. Sieben Disziplinen, vier Höhenlagen — ein System, kein Haufen.

| Schicht | Adoption | Disziplinen | Kadenz |
|-------|-------|-------------|---------|
| **L1 · Strategie** — was wir sagen / wer wir sind | crawl | **Narrative** · TALE | always-on |
| **L2 · Kanäle** — Always-on-Engines, die die Strategie ausdrücken (owned → bought) | walk | **SEO/GEO** · CORE-EEAT + CITE · **Organic Social** · ECHO · **Email** · SEND · **Paid Ads** · ROAS · **Influencer** · C³ | always-on (Influencer mit episodischem Hang) |
| **L3 · Orchestrierung** — der zeitlich begrenzte Moment über Kanäle hinweg | run | **Product Launch** · RAMP | episodisch |
| **L4 · Protokoll** — das gemeinsame System of Record | — | 8 Wahrheitsregister + Speicher · 8 Auditor-Gates · ein Skill-Vertrag | — |

Narrative ist die Botschaft; die Kanäle sind die Medien, die sie ausdrücken — entferne einen beliebigen Kanal und der Datensatz bleibt intakt; entferne Narrative und jeder Kanal spricht eine quellenlose, ungeregelte Botschaft. Jeder Kanal erbt Stimme und Claims von L1 auf dieselbe Weise, wie jeder Creative Builder heute schon das Claims-Ledger liest. Die 4-Phasen-Schleife jeder Disziplin lebt innerhalb ihrer Schicht (Narrative = Trace → Architect → Land → Evaluate).

Alle sieben nutzen Phasen-**verzeichnisse** (`narrative/trace/`…, `seo-geo/research/`…, `influencer/discover/`…, `ad/research/`…, `email/setup/`…, `launch/research/`…, `social/explore/`…). Beachte: „activate" bedeutet bei Influencer die Creator-Ansprache, bei Paid Ads jedoch das Konto-Gating — dasselbe Wort, disziplinspezifischer Umfang.

### Qualitätssystem: acht Frameworks, acht Gates

Acht Benchmarks machen „gut" messbar. Jedes definiert Dimensionen, eine Aggregationsmethode und eine kleine Menge von **Veto-Items** (harte Fehlschläge, die einen Score unabhängig vom Rest deckeln oder blockieren):

| Framework | Bewertet | Items / Dimensionen | Aggregation | Veto-Items |
|-----------|--------|--------------------|--------|------------|
| **[TALE](../references/tale-benchmark.md)** | Brand narrative Truth / Architecture / Landing / Evidence | T / A / L / E | **NQS = floor(zielgewichtetes Mittel)** (arithmetisch) | `T1`/`A1`/`L1`/`E1` |
| **[CORE-EEAT](../references/core-eeat-benchmark.md)** | Inhaltsqualität (GEO = CORE-Mittelwert, SEO = EEAT-Mittelwert) | 80 Items / 8 Dimensionen | Mittelwerte pro Dimension | `T04`, `C01`, `R10` |
| **[CITE](../references/cite-domain-rating.md)** | Domain-Autorität & Zitationsvertrauen | 40 Items / 4 Dimensionen | arithmetisches gewichtetes Mittel | `T03`, `T05`, `T09` |
| **[C³](../references/c3-benchmark.md)** | Influencer Creator / Content / Campaign | ACE / ART / ROI · 9 Dimensionen | **CVI = (ACE × ART × ROI)^⅓** (geometrisch) | ACE `A2`/`C1`/`E2`, ART `T1`/`T2` |
| **[ROAS](../references/roas-benchmark.md)** | Paid Ads Return / Offer / Audience / Spend-Effizienz | R / O / A / S | **RQS = floor(zielgewichtetes Mittel)** (arithmetisch) | `R1`/`R2`/`O1`/`O2`/`A1` |
| **[SEND](../references/send-benchmark.md)** | E-Mail-Marketing Sender-Integrität / Engagement / Nurture / Direct-Response | S / E / N / D | **EQS = floor(zielgewichtetes Mittel)** (arithmetisch) | `S1`/`S2`/`N1`/`D1` |
| **[RAMP](../references/ramp-benchmark.md)** | Produkt-Launch Readiness / Assets / Momentum / Proof | R / A / M / P · 40 Items | **LQS = floor(zielgewichtetes Mittel)** (arithmetisch) | `R1`/`A1`/`M1`/`P1` (framework-qualifiziert — verschieden von ROAS `R1`/`A1`) |
| **[ECHO](../references/echo-benchmark.md)** | Organic Social Embeddedness / Craft / Hosting / Observability | E / C / H / O | **SQS = floor(zielgewichtetes Mittel)** (arithmetisch) | `E1`/`C1`/`C2`/`H1`/`H2`/`O1` (framework-qualifiziert — verschieden von ROAS `O1`/`O2`) |

Jedes Framework wird von einem **Gate der Auditor-Klasse** durchgesetzt — einem Skill, der ein gegatetes Artefakt (`class: auditor-output`) schreibt, das vom PostToolUse-Hook validiert wird. Gates sind Workflow-Schritte, daher lebt jedes in seiner Disziplin und wird dort gezählt:

| Gate | Framework | Lebt in | Urteil |
|------|-----------|----------|---------|
| [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md) | TALE NQS | `narrative/evaluate/` (Narrative) | SHIP / FIX / BLOCK, bevor die Narrative adoptiert wird |
| [content-quality-auditor](../seo-geo/optimize/content-quality-auditor/SKILL.md) | CORE-EEAT | `seo-geo/optimize/` (SEO/GEO) | SHIP / FIX / BLOCK vor der Veröffentlichung |
| [domain-authority-auditor](../seo-geo/monitor/domain-authority-auditor/SKILL.md) | CITE | `seo-geo/monitor/` (SEO/GEO) | TRUSTED / CAUTIOUS / UNTRUSTED |
| [content-reviewer](../influencer/activate/content-reviewer/SKILL.md) | C³ ART | `influencer/activate/` (Influencer) | APPROVED / REVISIONS / REJECTED, bevor ein Creator-Post veröffentlicht wird |
| [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md) | ROAS RQS | `ad/activate/` (Paid) | SHIP / FIX / BLOCK vor dem Skalieren von Budgets |
| [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md) | SEND EQS | `email/deliver/` (E-Mail) | SHIP / FIX / BLOCK vor dem Versand |
| [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md) | RAMP LQS | `launch/mobilize/` (Launch) | SHIP / FIX / BLOCK, bevor der Launch-Moment festgelegt wird |
| [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md) | ECHO SQS | `social/host/` (Social) | SHIP / FIX / BLOCK vor der Veröffentlichung |

**Gemeinsames Cap-Chassis:** Ein einzelnes Veto deckelt die betroffene Dimension und die Gesamtwertung auf `min(raw, 60)`; **zwei oder mehr Vetos → `BLOCKED`** (kein Endscore). Urteile werden in Klartext übersetzt (keine Item-IDs in nutzerseitigen Berichten). Gate-Mechanik — Handoff-Schema, Cap-Arithmetik, Artifact-Gate-Checkliste — ist einmalig in [auditor-runbook.md](../references/auditor-runbook.md) spezifiziert, und die Arithmetik aller acht Frameworks ist durch einen deterministischen Golden-Test fixiert (siehe [Qualitäts-Guards](#qualitäts-guards-ci)).

### Die Protokollschicht

Das `protocol/`-Verzeichnis enthält die **gemeinsame Wahrheits- & Speicher-Maschinerie**, die außerhalb der Disziplin-Phasenflüsse sitzt — 8 Skills, separat gezählt:

| Skill | Aufgabe | Verankert an | Kanonischer Speicher |
|-------|-----|-------------|-----------------|
| [entity-optimizer](../protocol/entity-optimizer/SKILL.md) | Kanonisches Marken-/Entitätsprofil (Knowledge Graph, Wikidata, AI-Disambiguierung) | SEO/GEO | `memory/entities/` |
| [creator-registry](../protocol/creator-registry/SKILL.md) | Kanonisches Creator-Roster/-Dossier — deduplizierte Handles, herkunftsgekennzeichnete Audience-Statistiken, Raten, Compliance-Historie | Influencer | `memory/creators/` |
| [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md) | Offer- & Claim-Substanziierungsbuch — der Datensatz, gegen den die O1/T2-Claim-Prüfungen beurteilt werden | Paid | `memory/claims/` |
| [consent-registry](../protocol/consent-registry/SKILL.md) | Kanonischer Einwilligungs-/Unterdrückungsdatensatz pro Subjekt — die S2/N1-Vetos urteilen dagegen | E-Mail | `memory/consent/` |
| [launch-registry](../protocol/launch-registry/SKILL.md) | Kanonisches Launch-Dossier/-Kalender — Tier, Einweg-Lebenszyklusstufe, maßgebliche Daten/Embargo, Kanal-Einreichungsbuch; die Launch-Wahrheits-SSOT, gegen die das R1-Stufen-Wahrheits-Veto urteilt | Launch | `memory/launch-registry/` |
| [channel-registry](../protocol/channel-registry/SKILL.md) | Kanonischer Datensatz pro Kanal — Handles, Eigentum/Autorisierung, Plattformnormen, Disclosure-Defaults; die Kanal-Wahrheits-SSOT, gegen die das ECHO-E1-Kanal-Wahrheits-Veto urteilt | Social | `memory/channels/` |
| [narrative-registry](../protocol/narrative-registry/SKILL.md) | Kanonischer Brand-Narrative-Kanon — genehmigte strategische Narrative, Message-System, Sprache/Lexikon, Proof-Points; die Brand-Kanon-SSOT, gegen die das TALE-T1-Wahrheits-Veto urteilt | Narrative | `memory/narrative-registry/` |
| [memory-management](../protocol/memory-management/SKILL.md) | HOT/WARM/COLD-Speicher-Lebenszyklus (Erfassen · Befördern · Herabstufen · Archivieren · Abfragen) | alle Disziplinen | `memory/` |

Die Register folgen einer **Alleinschreiber-Regel** (andere Skills reichen über `candidates.md` ein), und sie *kuratieren* — die Gates *urteilen*. Die wirklich horizontale Schicht unter allem sind die `references/`-Protokolle ([auditor-runbook](../references/auditor-runbook.md), [state-model](../references/state-model.md), [skill-contract](../references/skill-contract.md), [humanizer-slop](../references/humanizer-slop.md), [measurement-protocol](../references/measurement-protocol.md)) — bewusst als Dokumente geteilt, nicht als Skills.

### Speicher & Automatisierungs-Hooks

**Der Speicher** ist temperaturgestuft, sodass Kontext über Skills und Sitzungen hinweg überlebt, ohne den Prompt aufzublähen:

| Stufe | Ort | Verhalten |
|------|----------|----------|
| **HOT** | `memory/hot-cache.md` | Bei jeder Sitzung automatisch geladen; gedeckelt auf **80 Zeilen UND 25 KB** (was zuerst greift). |
| **WARM** | `memory/<subdir>/` | Arbeitszustand pro Skill, gegatete Audit-Artefakte (`memory/audits/`) und die kanonischen Speicher der Register (`memory/entities\|creators\|claims/`). |
| **COLD** | `memory/archive/` | Herabgestufte/ältere Datensätze, für den Rückruf aufbewahrt. |

**Hooks** (`hooks/hooks.json`, Runner `hooks/claude-hook.sh`) verdrahten vier Claude-Code-Ereignisse:

| Ereignis | Matcher | Was es tut |
|-------|---------|--------------|
| `SessionStart` | `startup\|resume\|clear\|compact` | Injiziert den **bereinigten** Hot-Cache + einen Open-Loops-Zeiger (Prompt-Injection-Zeilen werden geschwärzt; symlinkte Caches werden abgelehnt). |
| `UserPromptSubmit` | (alle) | Leichtgewichtiger Kontext-Hook pro Prompt. |
| `PostToolUse` | `Write\|Edit` | Hot-Cache-Größenwarnung **+ das Artifact Gate**: Jede Datei unter `memory/audits/`, die `class: auditor-output` deklariert, wird gegen das Handoff-Schema und die Cap-Felder validiert, oder der Schreibvorgang wird blockiert. Die acht Gates der Auditor-Klasse müssen diese Markierung vertraglich deklarieren; nicht markierte Dateien sind keine Auditor-Artefakte und werden durchgelassen. |
| `Stop` | (alle) | No-op (beendet still). |

Das Artifact Gate ist **framework-agnostisch** — derselbe Hook validiert TALE-, CORE-EEAT-, CITE-, C³-, ROAS-, SEND-, RAMP- und ECHO-Artefakte ohne framework-spezifischen Code.

---

## Skill-Katalog

Skill-Links öffnen die jeweilige `SKILL.md`. Klappe die **Details** unter jeder Disziplin für einen Einzeiler-Zweck pro Skill auf. Die Katalogreihenfolge folgt den [vier Schichten der Strata](#das-system-ein-marketing-betriebssystem-aus-vier-schichten) — Narrative (L1 · Strategie) zuerst, die fünf Always-on-Kanäle als Nächstes, Launch (L3 · Orchestrierung) und dann die Protokollschicht.

### Narrative — TALE (16)

Vier Phasenverzeichnisse unter `narrative/` (je 4 Skills) folgen der TALE-Schleife (Trace → Architect → Land → Evaluate); das Gate (⛩ narrative-quality-auditor) sitzt in Evaluate. Nur das Gate berechnet die zielgewichtete NQS — jeder andere Skill bedient einen Hebel und übergibt. Narrative ist die L1 · Strategie-Schicht: eine Markenstimme, die die fünf Always-on-Kanäle erben. Sie absorbiert das Positioning — `positioning-mapper` bleibt physisch in `launch/`, liest sich aber logisch als der Anfang von TALE Trace.

| Phase | Skills |
|-------|--------|
| **Trace** | [narrative-baseline-mapper](../narrative/trace/narrative-baseline-mapper/SKILL.md), [category-narrative-mapper](../narrative/trace/category-narrative-mapper/SKILL.md), [audience-belief-mapper](../narrative/trace/audience-belief-mapper/SKILL.md), [positioning-truth-tracer](../narrative/trace/positioning-truth-tracer/SKILL.md) |
| **Architect** | [strategic-narrative-designer](../narrative/architect/strategic-narrative-designer/SKILL.md), [message-system-architect](../narrative/architect/message-system-architect/SKILL.md), [brand-language-codifier](../narrative/architect/brand-language-codifier/SKILL.md), [story-bank-builder](../narrative/architect/story-bank-builder/SKILL.md) |
| **Land** | [narrative-cascade-planner](../narrative/land/narrative-cascade-planner/SKILL.md), [pitch-narrative-builder](../narrative/land/pitch-narrative-builder/SKILL.md), [narrative-enablement-kit](../narrative/land/narrative-enablement-kit/SKILL.md), [proof-point-packager](../narrative/land/proof-point-packager/SKILL.md) |
| **Evaluate** | ⛩ [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md), [message-test-designer](../narrative/evaluate/message-test-designer/SKILL.md), [narrative-resonance-monitor](../narrative/evaluate/narrative-resonance-monitor/SKILL.md), [narrative-drift-monitor](../narrative/evaluate/narrative-drift-monitor/SKILL.md) |

<details><summary><b>Zweck pro Skill (Narrative)</b></summary>

| Skill | TALE-Hebel | Was er tut |
|-------|-----------|--------------|
| narrative-baseline-mapper | T | Erfasst die aktuelle, tatsächliche Markengeschichte, wie sie über eigene Flächen hinweg lebt — der ehrliche Ausgangspunkt vor jedem Redesign. |
| category-narrative-mapper | T | Kartiert die dominanten Narrative der Kategorie und die benannten Alternativen, damit die Marke eine verteidigbare, differenzierte Position beanspruchen kann. |
| audience-belief-mapper | T | Bringt an die Oberfläche, was die Zielgruppe bereits glaubt, bezweifelt und was ihr wichtig ist — die Überzeugungen, die die Narrative bewegen muss. |
| positioning-truth-tracer | T | Verfolgt jeden Positioning-Claim zurück zur Substanziierung und mustert alles Unbelegte aus (vorgelagert zum T1-Wahrheits-Veto). |
| strategic-narrative-designer | A | Entwirft die zentrale strategische Narrative — den Change-in-the-World-Handlungsbogen, die Einsätze und die Auflösung, mit denen die Marke führt. |
| message-system-architect | A | Architektiert das Message-System — Tagline, Pillars, Proof-Points und Winkel pro Zielgruppe als eine kohärente Struktur. |
| brand-language-codifier | A | Kodifiziert Stimme, Ton, Lexikon und Do/Don't-Sprache, damit jeder Kanal wie eine einzige Marke klingt. |
| story-bank-builder | A | Baut eine wiederverwendbare Bank aus Proof-Stories, Kundennarrativen und Analogien, aus der Kanäle schöpfen können. |
| narrative-cascade-planner | L | Plant, wie die Narrative ohne Verwässerung oder Drift in jeden Kanal und Moment kaskadiert. |
| pitch-narrative-builder | L | Bringt die Narrative in Pitch-Form — Deck-Rückgrat, Demo-Story und Investor-/Presse-Framing. |
| narrative-enablement-kit | L | Enablement-Kit, das jedem Team ermöglicht, die Geschichte konsistent zu erzählen — Talk-Track, FAQ und Message-Map. |
| proof-point-packager | L | Verpackt Proof-Points in kanalfertige, Claims-Ledger-bewusste Assets. |
| ⛩ narrative-quality-auditor | T+A+L+E (NQS) | TALE-Gate der Auditor-Klasse: bewertet NQS, erzwingt T1/A1/L1/E1, gibt SHIP/FIX/BLOCK aus; trägt einen **Narrative-Adoption-Go/No-Go**-Modus. |
| message-test-designer | E | Entwirft Message-Tests — Varianten-Matrix, Audience-Zellen und Resonanz-Auswertung für die strategische Narrative. |
| narrative-resonance-monitor | E | Verfolgt, wie die Narrative über die Kanäle hinweg landet, aus keyless Quellen (Proxy-Daten gekennzeichnet). |
| narrative-drift-monitor | E | Wacht über Narrative-Drift — wo Kanäle vom genehmigten Kanon abgewichen sind — und markiert Korrekturen. |

**Disziplinübergreifend wiederverwendet** (in ihren Heimatphasen gezählt, nicht dupliziert): [positioning-mapper](../launch/research/positioning-mapper/SKILL.md) (logisch der Anfang von Trace, physisch in `launch/`), [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), `audience-mapper`, `share-of-voice-tracker` (Resonanz-Nenner). **Kein neuer Konnektor** — die Narrative-Resonanz verwendet `bluesky.py` / `gdelt.py` / `tavily.py` / `wayback.py` wieder — siehe [tale-benchmark.md](../references/tale-benchmark.md).

</details>

### SEO/GEO (16)

Vier Phasenverzeichnisse (je 4 Skills) plus die beiden Qualitäts-Gates der Disziplin (markiert mit ⛩).

| Phase | Skills |
|-------|--------|
| **Research** | [keyword-research](../seo-geo/research/keyword-research/SKILL.md), [competitor-analysis](../seo-geo/research/competitor-analysis/SKILL.md), [serp-analysis](../seo-geo/research/serp-analysis/SKILL.md), [content-gap-analysis](../seo-geo/research/content-gap-analysis/SKILL.md) |
| **Build** | [content-writer](../seo-geo/build/content-writer/SKILL.md), [geo-content-optimizer](../seo-geo/build/geo-content-optimizer/SKILL.md), [serp-markup-builder](../seo-geo/build/serp-markup-builder/SKILL.md), [page-play-builder](../seo-geo/build/page-play-builder/SKILL.md) |
| **Optimize** | ⛩ [content-quality-auditor](../seo-geo/optimize/content-quality-auditor/SKILL.md), [technical-seo-checker](../seo-geo/optimize/technical-seo-checker/SKILL.md), [on-page-seo-auditor](../seo-geo/optimize/on-page-seo-auditor/SKILL.md), [site-structure-optimizer](../seo-geo/optimize/site-structure-optimizer/SKILL.md) |
| **Monitor** | ⛩ [domain-authority-auditor](../seo-geo/monitor/domain-authority-auditor/SKILL.md), [rank-tracker](../seo-geo/monitor/rank-tracker/SKILL.md), [performance-monitor](../seo-geo/monitor/performance-monitor/SKILL.md), [offsite-signal-analyzer](../seo-geo/monitor/offsite-signal-analyzer/SKILL.md) |

<details><summary><b>Zweck pro Skill (SEO/GEO)</b></summary>

| Skill | Was er tut |
|-------|--------------|
| keyword-research | Startet die Keyword-Arbeit für eine Seite/ein Thema/eine Kampagne — Intent, Nachfrage und Striking-Distance-Chancen. |
| competitor-analysis | Analysiert die SEO-Strategie eines Wettbewerbers, vergleicht Domains, deckt dessen Keywords und Lücken auf. |
| serp-analysis | Liest eine SERP — Features, Snippets, People Also Ask, Ranking-Muster für eine Abfrage. |
| content-gap-analysis | Findet fehlende Themen und Abdeckungslücken gegenüber Wettbewerbern. |
| content-writer | *(Merge: seo-content-writer + content-refresher)* Schreibt und aktualisiert SEO-optimierte Artikel, Landingpages und Produkttexte. |
| geo-content-optimizer | Optimiert Inhalte für AI-Engines (ChatGPT, Perplexity, AI Overviews, Gemini, Claude, Copilot). |
| serp-markup-builder | *(Merge: meta-tags-optimizer + schema-markup-generator)* Title/Meta/OG/Twitter-Tags plus JSON-LD / Schema.org strukturierte Daten. |
| page-play-builder | *(Merge: programmatic + parasite + comparison + local SEO, 4 Modi)* Vorlagengetriebene Page-Plays — programmatische Seiten, Parasite-Plattformen, Vergleichsseiten, local/GBP. |
| ⛩ content-quality-auditor | 80-Item-CORE-EEAT-Gate für Publish-Bereitschaft (SHIP/FIX/BLOCK). |
| technical-seo-checker | Seitengeschwindigkeit, Core Web Vitals, Indexierung, Crawlbarkeit, robots. |
| on-page-seo-auditor | Auditiert die On-Page-Gesundheit auf Seitenebene — Überschriften, Keyword-Platzierung, Bilder, Qualitätssignale. |
| site-structure-optimizer | *(Merge: internal-linking-optimizer + site-architecture)* Interne Links, Ankertext, verwaiste Seiten, Seitenhierarchie, URL-Taxonomie, Hub/Spoke-Cluster. |
| ⛩ domain-authority-auditor | 40-Item-CITE-Gate für Domain-Vertrauen (TRUSTED/CAUTIOUS/UNTRUSTED). |
| rank-tracker | Verfolgt Keyword-Rankings, Positionsänderungen und Abstürze. |
| performance-monitor | *(Merge: performance-reporter + alert-manager)* Multi-Metrik-SEO/GEO-Berichte, Dashboards und Schwellenwert-Alerts. |
| offsite-signal-analyzer | *(Merge: backlink-analyzer + ai-traffic)* Backlink-Profil + Linkqualität, plus Referral-Traffic von AI-Assistenten in deinem eigenen GA4/GSC/Logs. |

</details>

### Influencer (16)

Vier Phasenverzeichnisse (je 4 Skills); das Gate der Disziplin (⛩ content-reviewer) sitzt in Activate.

| Phase | Skills |
|-------|--------|
| **Discover** | [audience-mapper](../influencer/discover/audience-mapper/SKILL.md), [trend-spotter](../influencer/discover/trend-spotter/SKILL.md), [influencer-discovery](../influencer/discover/influencer-discovery/SKILL.md), [fit-scorer](../influencer/discover/fit-scorer/SKILL.md) |
| **Plan** | [competitor-tracker](../influencer/plan/competitor-tracker/SKILL.md), [campaign-planner](../influencer/plan/campaign-planner/SKILL.md), [brief-generator](../influencer/plan/brief-generator/SKILL.md), [budget-optimizer](../influencer/plan/budget-optimizer/SKILL.md) |
| **Activate** | [outreach-manager](../influencer/activate/outreach-manager/SKILL.md), ⛩ [content-reviewer](../influencer/activate/content-reviewer/SKILL.md), [contract-helper](../influencer/activate/contract-helper/SKILL.md), [content-amplifier](../influencer/activate/content-amplifier/SKILL.md) |
| **Measure** | [landing-optimizer](../influencer/measure/landing-optimizer/SKILL.md), [performance-analyzer](../influencer/measure/performance-analyzer/SKILL.md), [roi-calculator](../influencer/measure/roi-calculator/SKILL.md), [report-generator](../influencer/measure/report-generator/SKILL.md) |

<details><summary><b>Zweck pro Skill (Influencer)</b></summary>

| Skill | Was er tut |
|-------|--------------|
| audience-mapper | *(Merge: audience-analyzer + niche-researcher)* Profiliert die Zielgruppe und kartiert ihre Subkultur / Mikro-Community, bevor mit Creatorn zusammengearbeitet wird. |
| trend-spotter | Kampagnen-Timing und -Themen — trendende Hashtags, Sounds, Formate, kulturelle Momente. |
| influencer-discovery | Baut ein Creator-Roster von Grund auf, expandiert auf eine neue Plattform, sourct Nano/Micro im großen Maßstab. |
| fit-scorer | Objektiver, gewichteter Fit-Score für eine Shortlist (bewertet auf C³ ACE). |
| competitor-tracker | Die Creator, Kampagnen, Formate, geschätzte Reichweite/Ausgaben und Lücken eines Wettbewerbers. |
| campaign-planner | Plant eine Kampagne, einen Produkt-Launch, ein Tentpole oder ein Always-on-Creator-Programm. |
| brief-generator | Standardisierte Influencer-Briefs und wiederverwendbare Team-Vorlagen. |
| budget-optimizer | Verteilt Ausgaben über Tiers/Plattformen, projiziert ROI, modelliert Szenarien (dient auch Paid-Ads-Ausgaben + Bid-Pacing). |
| outreach-manager | Pitch, Follow-up-Kadenz, Reaktivierung, Ratenverhandlung, Statusverfolgung. |
| ⛩ content-reviewer | Vorab-Publish-Gate-Entscheidung zu einer Creator-Einreichung (C³ ART: FTC-Offenlegung T1, Claim-Integrität T2). |
| contract-helper | Entwirft/prüft Creator-Vereinbarungen — Nutzungsrechte, Exklusivität, Standardklauseln. |
| content-amplifier | *(Merge: content-amplifier + ugc-repurposer)* Erweitert organische Creator-Inhalte mit bezahlten Ausgaben und verwertet UGC über Paid, Web, E-Mail und Organic hinweg neu. |
| landing-optimizer | Landingpages für Creator-/Paid-Traffic — Message-Match, Mobile, A/B (dient auch Paid Post-Click). |
| performance-analyzer | Bewertet Creator-Ergebnisse, vergleicht Creator, Sentiment, Conversions (auch die Paid-Cross-Channel-Scorecard). |
| roi-calculator | Misst/projiziert ROI, verteidigt Budgets, bewertet Creator/Tiers (gemeinsame Return-Math-Engine, inkl. Paid). |
| report-generator | Schriftliche Stakeholder-Berichte nach einem Zeitraum (auch Paid-Ads-Berichte). |

</details>

### Paid Ads — ROAS (16)

Vier Phasenverzeichnisse unter `ad/` (je 4 Skills) folgen der ROAS-Schleife; das Gate (⛩ ad-account-auditor) sitzt in Activate. Nur das Gate berechnet die zielgewichtete RQS — jeder andere Skill bedient einen Hebel und übergibt.

| Phase | Skills |
|-------|--------|
| **Research** | [campaign-architect](../ad/research/campaign-architect/SKILL.md), [audience-segment-builder](../ad/research/audience-segment-builder/SKILL.md), [search-term-miner](../ad/research/search-term-miner/SKILL.md), [product-feed-optimizer](../ad/research/product-feed-optimizer/SKILL.md) |
| **Orchestrate** | [ad-creative-builder](../ad/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](../ad/orchestrate/ad-test-designer/SKILL.md), [bid-strategy-planner](../ad/orchestrate/bid-strategy-planner/SKILL.md), [landing-experience-checker](../ad/orchestrate/landing-experience-checker/SKILL.md) |
| **Activate** | ⛩ [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](../ad/activate/conversion-signal-qa/SKILL.md), [placement-exclusion-manager](../ad/activate/placement-exclusion-manager/SKILL.md), [conversion-value-mapper](../ad/activate/conversion-value-mapper/SKILL.md) |
| **Scale** | [paid-measurement-loop](../ad/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](../ad/scale/attribution-reconciler/SKILL.md), [budget-pacing-monitor](../ad/scale/budget-pacing-monitor/SKILL.md), [fatigue-frequency-manager](../ad/scale/fatigue-frequency-manager/SKILL.md) |

<details><summary><b>Zweck pro Skill (Paid Ads)</b></summary>

| Skill | ROAS-Hebel | Was er tut |
|-------|-----------|--------------|
| campaign-architect | A + Struktur | Konto-/Kampagnenstruktur, Kampagnentyp-Fit, Match-Types, Negatives/Ausschlüsse, Paid↔Organic-Kannibalisierung; trägt einen wiederkehrenden **Search-Term-Mining**-Modus. |
| audience-segment-builder | A | Verwandelt deinen eigenen Kunden-/CRM-/GA4-Export in Seed-Audiences, Lookalike-Seeds, Ausschluss-Segmente und eine Funnel-Stage-Targeting-Karte. |
| search-term-miner | A | *(NEU)* Durchsucht den Suchbegriffsbericht nach Negatives, neuen Keyword-Kandidaten und Match-Type-Verfeinerungen. |
| product-feed-optimizer | O | *(NEU)* Shopping/PMax-Feed-Hygiene — Titel, Attribute, GTINs, Kategorie-Mapping und Ablehnungs-Fixes. |
| ad-creative-builder | O | RSA-Headlines/-Descriptions, Hooks und eine Winkel-Matrix, message-matched zur Ziel-Seite. |
| ad-test-designer | O (+S) | Entwirft A/B/n- & Inkrementalitäts-Tests (Hypothese, Varianten-Matrix, Stichprobengröße/Power) und liest Signifikanz aus → Promote/Kill. |
| bid-strategy-planner | S | *(NEU)* Wählt und konfiguriert die Bidding-Strategie je Ziel (tCPA/tROAS/Max-Conversions), setzt Ziele, plant Lernphasen-Übergänge. |
| landing-experience-checker | O | *(NEU)* Post-Click-Page-QA auf Anzeigenrelevanz, Ladegeschwindigkeit, Mobile und Policy — die Ad↔Page-Message-Match-Prüfung. |
| ⛩ ad-account-auditor | R+O+A+S (RQS) | ROAS-Gate der Auditor-Klasse: bewertet RQS, erzwingt R1/R2/O1/O2/A1, gibt SHIP/FIX/BLOCK aus; trägt einen **Launch-Go/No-Go**-Modus. |
| conversion-signal-qa | R | Pre-Launch-Tracking-QA (Event-Auslösung, UTM-Hygiene, Dedup-Gate, Fenster-Ausrichtung, iOS-ATT-Flags) — die R1/R2-Voraussetzung (baut das Signal auf; das Gate bewertet es). |
| placement-exclusion-manager | A | *(NEU)* Placement-/Audience-Ausschlusslisten — Brand-Safety-Blocks, Junk-Placement-Pruning, Wasted-Spend-Unterdrückung. |
| conversion-value-mapper | R | *(NEU)* Ordnet Conversion-Aktionen Werten/Gewichten und Wertregeln zu, damit tROAS auf echte Marge bietet, nicht auf rohe Zählungen. |
| paid-measurement-loop | R (+S) | Liest eine ausgelieferte Änderung gegen eine Kontrolle über ein Fenster zurück → Promote / Keep-testing / Rollback / Unproven. |
| attribution-reconciler | R | Ständiges Order-ID-Dedup gegen das GA4-/E-Commerce-Wahrheitsset, Fenster-/Währungsnormalisierung, Modellvergleich, Inkrementalität. |
| budget-pacing-monitor | S | *(NEU)* Verfolgt das Ausgabentempo gegen das Budget über den Flight, markiert Unter-/Überauslieferung und empfiehlt Pacing-Korrekturen. |
| fatigue-frequency-manager | O | *(NEU)* Beobachtet Frequenz- und Creative-Decay-Signale, markiert ermüdete Anzeigen und plant Refresh/Rotation. |

**Disziplinübergreifend wiederverwendet** (in ihren Heimatphasen gezählt, nicht dupliziert): [budget-optimizer](../influencer/plan/budget-optimizer/SKILL.md) (Ausgaben + Bid-Pacing/Lernphasen-Modus), [landing-optimizer](../influencer/measure/landing-optimizer/SKILL.md) (Post-Click), [roi-calculator](../influencer/measure/roi-calculator/SKILL.md) (Return-Math), [report-generator](../influencer/measure/report-generator/SKILL.md), [performance-analyzer](../influencer/measure/performance-analyzer/SKILL.md).

</details>

### Email — SEND (16)

Vier Phasenverzeichnisse unter `email/` (je 4 Skills) folgen der SEND-Schleife; das Gate (⛩ email-quality-auditor) sitzt in Deliver. Nur das Gate berechnet die zielgewichtete EQS — jeder andere Skill bedient einen Hebel und übergibt. Use-Case-agnostisch (B2C-Lifecycle / B2B-Cold-Outbound / Newsletter-Creator); die Zielgewicht-Spalte wählt den Schwerpunkt.

| Phase | Skills |
|-------|--------|
| **Setup** | [deliverability-qa](../email/setup/deliverability-qa/SKILL.md), [list-segment-builder](../email/setup/list-segment-builder/SKILL.md), [list-growth-designer](../email/setup/list-growth-designer/SKILL.md), [list-hygiene-monitor](../email/setup/list-hygiene-monitor/SKILL.md) |
| **Engage** | [email-creative-builder](../email/engage/email-creative-builder/SKILL.md), [subject-line-lab](../email/engage/subject-line-lab/SKILL.md), [email-render-builder](../email/engage/email-render-builder/SKILL.md), [dynamic-content-personalizer](../email/engage/dynamic-content-personalizer/SKILL.md) |
| **Nurture** | [email-sequence-designer](../email/nurture/email-sequence-designer/SKILL.md), [newsletter-monetization-planner](../email/nurture/newsletter-monetization-planner/SKILL.md), [preference-frequency-manager](../email/nurture/preference-frequency-manager/SKILL.md), [reactivation-specialist](../email/nurture/reactivation-specialist/SKILL.md) |
| **Deliver** | ⛩ [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md), [send-experiment-designer](../email/deliver/send-experiment-designer/SKILL.md), [inbox-placement-monitor](../email/deliver/inbox-placement-monitor/SKILL.md), [cold-outbound-sequencer](../email/deliver/cold-outbound-sequencer/SKILL.md) |

<details><summary><b>Zweck pro Skill (E-Mail)</b></summary>

| Skill | SEND-Hebel | Was er tut |
|-------|-----------|--------------|
| deliverability-qa | S | Pre-Flight-SPF/DKIM/DMARC/BIMI-Auth, Reputation, Inbox-Placement, Spam-Content und Listenhygiene (die S1-Prüfung). |
| list-segment-builder | E | Verhaltens- + Lifecycle-Stage-Segmente und Unterdrückungsregeln aus deinem eigenen Listen-/CRM-/GA4-Export. |
| list-growth-designer | S (+N) | Listen-Wachstumsstrategie — Akquisitionskanäle, Lead-Magnet-Konzepte, eine konforme Opt-in-Capture-Flow-Spec und Referral-Loop-Mechaniken; speist die bei der Akquise erfasste S-Consent-Qualität. |
| list-hygiene-monitor | S | *(NEU)* Laufende Listengesundheit — Bounce-/Complaint-Pruning, Sunset-Richtlinien, Re-Permission und Inaktiv-Segment-Unterdrückung. |
| email-creative-builder | E (+D) | Betreff/Preheader/Body/CTA, message-matched zur Landingpage, Claims-Ledger-bewusst. |
| subject-line-lab | E | *(NEU)* Betreff-/Preheader-Ideenfindung und -Scoring — Länge, Spam-Trigger, Neugier/Klarheit-Balance, Variantensätze zum Testen. |
| email-render-builder | E | *(NEU)* HTML-E-Mail-Build/QA — Client-Kompatibilität, Dark-Mode, Barrierefreiheit, Plain-Text-Alt und Render-Test-Checkliste. |
| dynamic-content-personalizer | E | *(NEU)* Merge-Tag-/Liquid-Personalisierungsblöcke, bedingte Content-Regeln und Fallback-Wert-Sicherheit. |
| email-sequence-designer | N | Lifecycle-/Automatisierungs-Flows (Welcome, Cart, Post-Purchase, Win-back) + Frequenz-Governance. |
| newsletter-monetization-planner | D | Paid-Sub, Sponsorship-Inventar + Rate Card und Referral-Growth-Loop-Ökonomie. |
| preference-frequency-manager | N | *(NEU)* Preference-Center-Design und Sendefrequenz-Governance zur Reduzierung von Fatigue und Abmeldungen. |
| reactivation-specialist | N | *(NEU)* Win-back-/Re-Engagement-Flows für ruhende Abonnenten mit Sunset-oder-Recover-Entscheidungsregeln. |
| ⛩ email-quality-auditor | S+E+N+D (EQS) | SEND-Gate der Auditor-Klasse: bewertet EQS, erzwingt S1/S2/N1/D1, gibt SHIP/FIX/BLOCK aus; trägt einen **Pre-Send-Go/No-Go**-Modus. |
| send-experiment-designer | E | A/B- / Send-Time- / Hold-out-Design mit Stichprobengröße + Signifikanz-Auswertung (Promote/Kill). |
| inbox-placement-monitor | S | *(NEU)* Laufende Inbox-vs-Spam-Placement-Verfolgung über Seed-Listen und Provider-Signale, mit Reputations-Drift-Alerts. |
| cold-outbound-sequencer | D | *(NEU)* Konforme B2B-Cold-Outbound-Kadenzen — deliverability-sicherer Ramp, Personalisierungs-Tokens und Reply-Handling-Schritte. |

**Disziplinübergreifend wiederverwendet** (in ihren Heimatphasen gezählt, nicht dupliziert): [audience-mapper](../influencer/discover/audience-mapper/SKILL.md), [landing-optimizer](../influencer/measure/landing-optimizer/SKILL.md), [roi-calculator](../influencer/measure/roi-calculator/SKILL.md), [report-generator](../influencer/measure/report-generator/SKILL.md), [performance-analyzer](../influencer/measure/performance-analyzer/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md).

</details>

### Launch — RAMP (16)

Vier Phasenverzeichnisse unter `launch/` (je 4 Skills) folgen der RAMP-Schleife; das Gate (⛩ launch-readiness-auditor) sitzt in Mobilize. Nur das Gate berechnet die zielgewichtete LQS — jeder andere Skill bedient einen Hebel und übergibt. Use-Case-agnostisch (B2B-SaaS-Sales-led / Dev-Tool-Community-Launch / Mobile-App-Store-Launch); die Zielgewicht-Spalte wählt den Schwerpunkt.

| Phase | Skills |
|-------|--------|
| **Research** | [positioning-mapper](../launch/research/positioning-mapper/SKILL.md), [launch-tier-planner](../launch/research/launch-tier-planner/SKILL.md), [launch-window-planner](../launch/research/launch-window-planner/SKILL.md), [early-access-designer](../launch/research/early-access-designer/SKILL.md) |
| **Assemble** | [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), [launch-asset-packager](../launch/assemble/launch-asset-packager/SKILL.md), [pricing-packaging-planner](../launch/assemble/pricing-packaging-planner/SKILL.md), [sales-enablement-kit](../launch/assemble/sales-enablement-kit/SKILL.md) |
| **Mobilize** | ⛩ [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md), [launch-day-conductor](../launch/mobilize/launch-day-conductor/SKILL.md), [community-launch-runner](../launch/mobilize/community-launch-runner/SKILL.md), [press-media-relations](../launch/mobilize/press-media-relations/SKILL.md) |
| **Prove** | [launch-monitor](../launch/prove/launch-monitor/SKILL.md), [launch-feedback-synthesizer](../launch/prove/launch-feedback-synthesizer/SKILL.md), [launch-retro-analyzer](../launch/prove/launch-retro-analyzer/SKILL.md), [momentum-planner](../launch/prove/momentum-planner/SKILL.md) |

<details><summary><b>Zweck pro Skill (Launch)</b></summary>

| Skill | RAMP-Hebel | Was er tut |
|-------|-----------|--------------|
| positioning-mapper | R | Positioning-Canvas im Dunford-Stil — benannte konkurrierende Alternativen, einzigartige Attribute, Value-Themen, Beachhead-Segment, Onlyness-Statement. |
| launch-tier-planner | R | Tier-Entscheidung (Tier 1 Flagship / Tier 2 Targeted / Tier 3 Changelog-Level), Launch-Typ-Deklaration, KPI-Ziele, Risikoregister mit Kill-Kriterien. |
| launch-window-planner | R | Kandidaten-Fenster-Vergleich (Konflikte / Rückenwinde / Risiko), Launch-Week-vs-Rolling-Release-Entscheidung, Store-Review-Puffer, Embargo-Fenster-Definition. |
| early-access-designer | R | Waitlist→Concept→Alpha→Beta→GA-Stufenleiter mit Graduierungskriterien, Cohort-Gating, Feedback-Loop, Referral-Mechaniken (vorgelagert zum R1-Stufen-Wahrheits-Veto). |
| message-house-builder | A | Message House (Tagline, One-Liner, Value-Pillars, Proof-Points) + Working-Backwards-PR-FAQ-Rückgrat + Angle-Packs pro Kanal (vorgelagert zu A1). |
| launch-asset-packager | A | Tier-skoptes Launch-Asset-Manifest — Press-Kit-Spec, Demo-/Screenshot-Specs, Launch-FAQ, Store-Listing-Metadaten, technische Go-Live-Checkliste. |
| pricing-packaging-planner | A | Launch-Pricing & -Packaging — Tier-Struktur, Value-to-Price-Map, Launch-Offer-Leiter, Beta-Pricing mit Graduierungspfad, Garantiebedingungen. |
| sales-enablement-kit | A | Internes Enablement — Battle Cards, Sales-Talk-Track, Objection-Handling-Tabelle, interne FAQ + CS-Makros, embargo-disziplinierte interne Ankündigung. |
| ⛩ launch-readiness-auditor | R+A+M+P (LQS) | RAMP-Gate der Auditor-Klasse: bewertet LQS, erzwingt R1/A1/M1/P1, gibt SHIP/FIX/BLOCK aus; trägt einen **T-1-Go/No-Go**-Modus. |
| launch-day-conductor | M | Stundengeblocktes Launch-Day-Runbook — Vorbedingungs-Gate-Check, Beobachtungsfenster-Urteile nach irreversiblen Pushes, P0–P3-Incident-Leiter + Rollback-Playbooks. |
| community-launch-runner | M | Einreichungspakete pro Plattform (Product Hunt, Show HN, Subreddits, Directory-Wellen, regionale/chinesische Kanäle) unter einem Plattform-Red-Line-Check. |
| press-media-relations | M | Dreistufige Medien-/Analysten-Liste, Embargo-Pitch-Timing, Pressemitteilungs-Entwurf in Standardstruktur, Analyst-Briefing-Gliederung. |
| launch-monitor | P | T-0→T+30-Fensterüberwachung — Instrumentierungsverifikation (vorgelagert zu P1), Rank-/Review-/News-Polling, D0/W1/M1-KPI-Snapshots, Spike-vs-Sustain-Auswertungen. |
| launch-feedback-synthesizer | P | Feedback-Themen-Digest, Open→Shipped-Status-Loop („you asked, we shipped"), konforme Social-Proof-Ernte. |
| launch-retro-analyzer | P | D1/W1/M1-Retro — Actual-vs-Target pro Kanal, 5-Whys zum größten Miss, Keep/Kill/Change-Entscheidungen, Outcome-Snapshot ins Register. |
| momentum-planner | P | T+1→T+30-Momentum-Plan — Launch-Moment-Kalender, Announcement-Tier-Routing, Relaunch-Legitimitäts-Entscheidung, nächster Tier-1-Moment. |

**Disziplinübergreifend wiederverwendet** (in ihren Heimatphasen gezählt, nicht dupliziert): `audience-mapper`, `trend-spotter`, `budget-optimizer`, `landing-optimizer`, `campaign-planner`, `outreach-manager`, `content-amplifier`, `email-creative-builder` / `email-sequence-designer` / `cold-outbound-sequencer`, `campaign-architect` / `ad-creative-builder`, `page-play-builder` / `content-writer`, `technical-seo-checker` / `serp-markup-builder`, `performance-monitor`, `keyword-research`, `entity-optimizer`, `offer-claims-registry`, `consent-registry`, `list-growth-designer`, `roi-calculator` / `performance-analyzer` / `report-generator` — siehe [ramp-benchmark.md](../references/ramp-benchmark.md).

</details>

### Social — ECHO (16)

Vier Phasenverzeichnisse unter `social/` (je 4 Skills) folgen der ECHO-Schleife; das Gate (⛩ social-quality-auditor) sitzt in Host. Nur das Gate berechnet die zielgewichtete SQS — jeder andere Skill bedient einen Hebel und übergibt. Use-Case-agnostisch (Community/Dev-Tool / B2C-Marke / B2B-Founder-led); die Zielgewicht-Spalte wählt den Schwerpunkt. Die Disziplin liefert **keine** Posting-, Engagement- oder DM-Automatisierung jeglicher Art.

| Phase | Skills |
|-------|--------|
| **Explore** | [channel-portfolio-planner](../social/explore/channel-portfolio-planner/SKILL.md), [voice-dossier-builder](../social/explore/voice-dossier-builder/SKILL.md), [platform-norm-profiler](../social/explore/platform-norm-profiler/SKILL.md), [participation-warmup-planner](../social/explore/participation-warmup-planner/SKILL.md) |
| **Craft** | [social-calendar-builder](../social/craft/social-calendar-builder/SKILL.md), [social-creative-builder](../social/craft/social-creative-builder/SKILL.md), [short-video-scripter](../social/craft/short-video-scripter/SKILL.md), [advocacy-program-designer](../social/craft/advocacy-program-designer/SKILL.md) |
| **Host** | ⛩ [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md), [engagement-inbox-manager](../social/host/engagement-inbox-manager/SKILL.md), [social-selling-planner](../social/host/social-selling-planner/SKILL.md), [crisis-response-planner](../social/host/crisis-response-planner/SKILL.md) |
| **Observe** | [social-pulse-monitor](../social/observe/social-pulse-monitor/SKILL.md), [share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md), [dark-social-attributor](../social/observe/dark-social-attributor/SKILL.md), [social-measurement-loop](../social/observe/social-measurement-loop/SKILL.md) |

<details><summary><b>Zweck pro Skill (Social)</b></summary>

| Skill | ECHO-Hebel | Was er tut |
|-------|-----------|--------------|
| channel-portfolio-planner | E | Wählt den Plattform-Mix und die Rolle/Kadenz pro Kanal von dort, wo die Zielgruppe tatsächlich ist (registriert Kanäle im Register). |
| voice-dossier-builder | E | Markenstimme, Ton, Persona und Do/Don't-Lexikon für eine konsistente, menschlich klingende Präsenz. |
| platform-norm-profiler | E | Normen, Formate, Ranking-Signale und Red-Line-Regeln pro Plattform, bevor du dort postest. |
| participation-warmup-planner | E | Nicht-promotionaler Community-Warm-up-Plan — wo man auftaucht und Wert stiftet, bevor man verkauft. |
| social-calendar-builder | C | Redaktionskalender — Themen, Serien, Kadenz im Gleichgewicht zur realen Kapazität (kein Over-Posting). |
| social-creative-builder | C | Plattform-native Posts (Hook/Body/CTA), message-matched und Claims-Ledger-bewusst. |
| short-video-scripter | C | Short-Form-Video-Skripte — Hook, Beats, On-Screen-Text, Retention-Struktur. |
| advocacy-program-designer | C | Employee-/Community-Advocacy-Programm — Opt-in, Disclosure-Defaults, teilbares Asset-Kit. |
| ⛩ social-quality-auditor | E+C+H+O (SQS) | ECHO-Gate der Auditor-Klasse: bewertet SQS, erzwingt E1/C1/C2/H1/H2/O1, gibt SHIP/FIX/BLOCK aus; trägt einen **Pre-Publish-Go/No-Go**-Modus. |
| engagement-inbox-manager | H | Reply-/Comment-/DM-Triage-Playbook — Response-Tiers, Eskalation, Genuine-Engagement-Disziplin (kein fabriziertes/geködertes Engagement). |
| social-selling-planner | H | Founder-/Team-Social-Selling-Motion — beziehungsorientierter Outreach, keine automatisierten DMs. |
| crisis-response-planner | H | Vorformulierte Krisen-Tiers, Holding-Statements, Eskalationsleiter und Pause-the-Queue-Trigger. |
| social-pulse-monitor | O | Mentions-/Sentiment-/Topic-Puls aus keyless Quellen, Spike-vs-Sustain-Auswertungen (Proxy-Daten gekennzeichnet). |
| share-of-voice-tracker | O | Share-of-Voice gegen benannte Wettbewerber über einen periodenstabilen Nenner. |
| dark-social-attributor | O | Attribuiert Dark-Social-/unverlinkten Traffic — UTM-Disziplin, Erfassung selbstberichteter Attribution, Referral-Parsing. |
| social-measurement-loop | O | Liest eine ausgelieferte Änderung gegen eine Baseline über ein Fenster zurück → Promote / Keep-testing / Rollback. |

**Disziplinübergreifend wiederverwendet** (in ihren Heimatphasen gezählt, nicht dupliziert): `trend-spotter`, `audience-mapper`, `content-amplifier`, `outreach-manager`, `competitor-tracker`, `landing-optimizer`, `performance-analyzer`, `roi-calculator`, `report-generator`, `offer-claims-registry`, `community-launch-runner`, `creator-registry`, `page-play-builder`, `memory-management` — siehe [echo-benchmark.md](../references/echo-benchmark.md).

</details>

### Protokollschicht (8)

Die gemeinsame Wahrheits- & Speicher-Maschinerie — siehe [Architektur § Die Protokollschicht](#die-protokollschicht) für Rollen und Alleinschreiber-Regeln.

| Gruppe | Skills |
|-------|--------|
| **Protokoll** | [entity-optimizer](../protocol/entity-optimizer/SKILL.md), [creator-registry](../protocol/creator-registry/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md), [consent-registry](../protocol/consent-registry/SKILL.md), [launch-registry](../protocol/launch-registry/SKILL.md), [channel-registry](../protocol/channel-registry/SKILL.md), [narrative-registry](../protocol/narrative-registry/SKILL.md), [memory-management](../protocol/memory-management/SKILL.md) |

<details><summary><b>Zweck pro Skill (Protokoll)</b></summary>

| Skill | Was er tut |
|-------|--------------|
| entity-optimizer | Kanonisches Entitätsprofil für Knowledge Graph, Wikidata, AI-Disambiguierung. |
| creator-registry | Kanonisches Creator-Roster/-Dossier — deduplizierte Handles, herkunftsgekennzeichnete Audience-Statistiken, Raten, Compliance-Historie. |
| offer-claims-registry | Kanonisches Offer- & Claim-Substanziierungsbuch — der Datensatz, gegen den die O1/T2-Claim-Prüfungen beurteilt werden. |
| consent-registry | Kanonischer Einwilligungs-/Unterdrückungsdatensatz pro Subjekt — Opt-in-Zeitstempel + Rechtsgrundlage, Double-Opt-in-Nachweis, Append-only-Unsub-/Bounce-/Complaint-Historie; der Datensatz, gegen den die S2/N1-Vetos urteilen. |
| launch-registry | Kanonisches Dossier pro Launch + Launch-Kalender — Tier, Launch-Typ, Einweg-Lebenszyklusstufe (draft→…→GA), maßgebliche Daten + Embargo-Verpflichtungen, Kanal-Einreichungsbuch, Outcome-Snapshot; die Launch-Wahrheits-SSOT. |
| channel-registry | Kanonischer Datensatz pro Kanal — Handles, Eigentum/Autorisierung, Plattformnormen, Disclosure-Defaults; die Kanal-Wahrheits-SSOT, gegen die das ECHO-E1-Kanal-Wahrheits-Veto urteilt. |
| narrative-registry | Kanonischer Brand-Narrative-Kanon — genehmigte strategische Narrative, Message-System, Sprache/Lexikon, Proof-Points; die Brand-Kanon-SSOT, gegen die das TALE-T1-Wahrheits-Veto urteilt. |
| memory-management | Prüfen, befördern, herabstufen und archivieren des HOT/WARM/COLD-Projektspeichers. |

</details>

---

## Befehle

Acht Befehle: `/aaron-marketing:auto` leitet jedes Ziel durch alle sieben Disziplinen, und jede Disziplin hat genau einen expliziten Einstiegspunkt. Quelle: [commands/](../commands).

| Befehl | Wofür | Eingrenzung |
|---------|-----------|-----------|
| `/aaron-marketing:auto` | Beschreibe ein beliebiges Ziel — leitet die Absicht ab und führt den kleinsten nützlichen Workflow aus | `--deep` (erschöpfend / Stresstest) |
| `/aaron-marketing:narrative` | Brand Narrative (TALE-Schleife): die aktuelle Story & Kategorie tracen, die strategische Narrative & das Message-System architektieren, sie über Kanäle landen, das Qualitäts-Gate, Resonanz & Drift | `--phase trace\|architect\|land\|evaluate` |
| `/aaron-marketing:seo-geo` | SEO/GEO End-to-End: Nachfrage/Wettbewerber recherchieren, Inhalte erstellen, Qualität/Technik/Sichtbarkeit/Autorität auditieren, Rankings/Berichte/Speicher verfolgen | `--mode research\|create\|audit\|track` + Flags pro Modus (`--competitors` `--map` · `--brief` `--series` `--refresh` `--publish` `--meta` `--schema` `--type` · `--full` `--tech` `--visibility` `--authority` · `--alert` `--report` `--remember` `--period`) |
| `/aaron-marketing:influencer` | Influencer: Audience-Insight, Discovery & Fit, Planung, Outreach, Amplification, ROI | `--phase discover\|plan\|activate\|measure` |
| `/aaron-marketing:ad` | Paid Ads (ROAS-Schleife): Segmente, Struktur, Creative, Experiment-Design, das Audit-Gate, Messung | `--phase research\|orchestrate\|activate\|scale` |
| `/aaron-marketing:email` | E-Mail (SEND-Schleife): Deliverability/Consent, Segmentierung, Creative, Lifecycle-Flows, Monetarisierung, Send-Testing, das Audit-Gate | `--phase setup\|engage\|nurture\|deliver` |
| `/aaron-marketing:launch` | Produkt-Launch (RAMP-Schleife): Positionierung, Tier & Fenster, Message House & Assets, das Readiness-Gate, Launch-Day-Ablauf, Monitoring & Retro | `--phase research\|assemble\|mobilize\|prove` |
| `/aaron-marketing:social` | Organic Social (ECHO-Schleife): Kanal-Portfolio & Stimme, Kalender & Creative, das Qualitäts-Gate, Engagement-/Crisis-Hosting, Puls & Messung | `--phase explore\|craft\|host\|observe` |

Die tägliche Arbeit beginnt normalerweise mit `/aaron-marketing:auto`; die anderen sieben sind explizite Disziplin-Einstiegspunkte, mit `--mode` / `--phase` zur Eingrenzung der Stufe.

**Umbenennungshinweis:** Befehle verwenden das Präfix `/aaron-marketing:`. Die früheren Befehle `research` / `create` / `audit` / `track` sind jetzt Modi von `/aaron-marketing:seo-geo` (Flags unverändert). Ältere `/seo:*`- und `/aaron-seo-geo:*`-Namen werden über `auto` wiederhergestellt — z. B. gibt `/aaron-marketing:auto /aaron-seo-geo:audit https://example.com/blog/post` `/aaron-marketing:seo-geo https://example.com/blog/post --mode audit` zurück.

---

## Konnektoren & Ausbaustufen

Skills benennen Tools mit `~~category`-Platzhaltern (`~~SEO tool`, `~~web analytics`, `~~ad platform`, `~~email platform`, …) statt spezifischer Anbieter, und jede Kategorie hat einen **keyless Tier-1-Pfad**. Vollständige Rezepte — einschließlich des kostenlosen/Erstanbieter-Endpunkts für jede Kategorie — stehen in [CONNECTORS.md](../CONNECTORS.md).

### Die Konnektorschicht ist selbst ein Produkt

**100+ dokumentierte Integrationspfade** über drei durchdachte Schichten — und jeder verdient seinen Platz:

| Schicht | Was du bekommst |
|-------|--------------|
| **21 gebündelte Zero-Dependency-Konnektoren** | Reine Python-Standardbibliothek — kein `pip`, kein Build-Schritt. Keyless Live-SERP + JS-gerendertes Scraping (Firecrawl, Tavily), eine AI-Answer-Citation-Probe, DNS-over-HTTPS-E-Mail-Auth-Pulls, Wikipedia-Aufmerksamkeitsserien, GDELT-News-Mentions, echte YouTube-Creator-Metriken, IndexNow + Baidu-Index-Push, Resend-ESP-Automatisierung und ein git-differenzierbares Messbuch, das jeden von ihnen in eine Vorher/Nachher-Zeitreihe verwandelt. |
| **60+ dokumentierte offizielle/kostenlose APIs** | Jede Zeile verlinkt die **offizielle Dokumentation** des Anbieters, trägt ein Verifiziert-am-Datum, und jeder Link wird vor Auslieferung HTTP-geprüft. Enthält die Pfade, die die meisten Tool-Listen übersehen: GSC URL Inspection, CrUX History (40 Wochen Field-CWV), die Gmail Postmaster Tools API, Metas Ad Library, Microsoft Claritys Data Export API. |
| **Anbieter-MCP-Server** | 18 Remote-Endpunkte katalogisiert (nie automatisch registriert — deine `/mcp`-Liste bleibt sauber) plus die offiziellen selbst gehosteten Server für Google Analytics, Search Console, **Google Ads** und **Microsoft Clarity**. Zwei Remote-MCPs funktionieren ganz ohne Schlüssel (Firecrawl, Tavily). |

Was sie vertrauenswürdig statt nur zahlreich macht:

- **Drei Sicherheitsklassen, durchdachte Gates** ([SECURITY.md](../SECURITY.md)): Gehostete Fetcher führen vor jedem delegierten Fetch einen **lokalen robots.txt-Pre-Flight** aus und verweigern bei Disallow; alles, was externen Zustand verändert (E-Mail-Versand, Index-Pushes), ist **standardmäßig Dry-Run** hinter einem expliziten `--live`-Flag, mit Idempotenzschlüsseln, wo der Anbieter sie unterstützt, und ohne Auto-Retry, wo nicht.
- **Verifiziert, dann re-verifiziert**: Endpunkte werden gegen primäre Anbieter-Dokumente mit Datum geprüft, keyless Pfade werden live getestet, ein CI-Guard erzwingt Versions-/Tracking-Sync, und ein Pre-Release-Live-Smoke fängt Endpunkt-Drift ab (er hat bereits echte API-Änderungen abgefangen — zweimal).
- **Fakten, keine Urteile**: Konnektoren melden Datensatzpräsenz, geparste Tags und Rohserien; die Auditor-Gates urteilen, und Skills kennzeichnen jede Zahl mit **Measured / User-provided / Estimated**.
- **Ein geschriebenes Playbook** ([docs/connector-playbook.md](connector-playbook.md)) regelt jede Ergänzung — qualifizieren, verifizieren, implementieren, testen, verdrahten, dokumentieren, tracken, regressieren, festhalten — sodass die Qualität hält, während der Katalog wächst.

| Stufe | Erfordert | Was du bekommst |
|------|----------|---------|
| **Tier 1** (Standard) | Nichts | Daten einfügen oder aus kostenlosen/öffentlichen Quellen ziehen. Das vollständige Analyse-Framework läuft so oder so. |
| **Tier 2** | Eine kostenlose Erstanbieter-API oder MCP | Automatischer Abruf deiner eigenen GSC- / GA4- / Core-Web-Vitals-Daten. |
| **Tier 3** | Ein umfassenderes MCP-Set | Vollautomatisierte Multi-Source-Workflows. |

- **Gebündelte Zero-Dependency-Helfer** unter `scripts/connectors/` (nur Python-Standardbibliothek) ziehen öffentliche/eigene Daten lokal — z. B. PageSpeed/CrUX, Open PageRank, Page-Crawl, Wayback CDX, Wikidata SPARQL, Common Crawl, advertools-Rezepte — plus **`resend.py`**, direkte Resend-ESP-Automatisierung für die E-Mail-Skills (Free-Tier-Key: Domain-Auth-Status, Seed-Test-Sends, Suppression-Sync, Broadcast-Scheduling; verändernde Subcommands standardmäßig Dry-Run und erfordern `--live`), und **`firecrawl.py`** + **`tavily.py`**, keyless Hosted-Fetcher-Automatisierung für die Research-Skills (Firecrawl: Live-Web-SERP + JS-gerendertes Page-Markdown + Site-Maps; Tavily: bewertete Suche + Cited-Sources-Probe einer AI-Answer-Engine für GEO + URL-Extract — beide kostenlos ganz ohne Schlüssel, beide mit einem eingebauten lokalen robots.txt-Pre-Flight).
- **Kostenlose/keyless Quellen** pro Kategorie dokumentiert: Google Search Console & GA4 (eigene Daten), PageSpeed/CrUX, Wikidata, Common Crawl, Open PageRank, Firecrawl keyless SERP/Scrape, Tavily keyless AI-Search, DNS-over-HTTPS-E-Mail-Auth-Records (`doh.py`), Wikipedia-Aufmerksamkeitsserien (`pageviews.py`), GDELT-News-Mentions (`gdelt.py`), YouTube-Creator-Metriken mit einem Free-Key (`youtube.py`), IndexNow + Baidu-Index-Push (`indexpush.py`, Dry-Run-gegatet), die Ad-Transparency-Bibliotheken (Meta/Google/TikTok) und Rezept-Zeilen für crt.sh, den W3C-Validator, oEmbed und HN Algolia.
- **Opt-in-MCP-Server** (Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, die selbst gehostete kostenlose **OpenSEO**-Suite, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack, Resend, das keyless Firecrawl und Tavily) sind in [`docs/mcp-catalog.json`](mcp-catalog.json) als **reine Copy-Paste-Referenz** katalogisiert — der Katalog sitzt außerhalb des automatisch registrierten Plugin-Root-`.mcp.json`-Pfads, sodass nichts für dich registriert wird. Kopiere die gewünschten Einträge in deine eigene MCP-Konfiguration.

Paid-Ads-Skills bewerten aus deinem **eigenen manuellen Kontoexport** (nativer Ad-Manager-CSV, GA4, E-Commerce). Mit Schlüssel versehene Ad-Plattform-APIs (Google Ads SDK, Meta Marketing API) sind nur Opt-in-Tier-2/3 und **niemals** eine Tier-1-Voraussetzung. E-Mail-Skills bewerten genauso — aus deinem **eigenen ESP-Export** — und jedes Deliverability-Signal ist keyless (DNS-Lookups, ein DMARC-RUA-Report und ein Seed-List-Inbox-Test), sodass eine mit Schlüssel versehene ESP-API auch keine Tier-1-Voraussetzung ist; wenn Resend dein ESP ist, automatisiert das gebündelte `resend.py` dieselbe Schleife auf dem Free-Tier.

---

## Empfohlene Workflows

**SEO/GEO**
1. **Research** — `keyword-research` → `competitor-analysis` → `content-gap-analysis`
2. **Build** — `content-writer` → `geo-content-optimizer` → `serp-markup-builder` / `page-play-builder`
3. **Optimize** — `content-quality-auditor` (⛩ Publish-Gate) → `on-page-seo-auditor` → `technical-seo-checker` → `site-structure-optimizer`
4. **Monitor** — `rank-tracker` → `performance-monitor` → `offsite-signal-analyzer`; `domain-authority-auditor` (⛩) für die Vertrauensprüfung

**Influencer**
1. **Discover** — `audience-mapper` → `trend-spotter` → `influencer-discovery` → `fit-scorer` (C³ ACE)
2. **Plan** — `competitor-tracker` → `campaign-planner` → `brief-generator` → `budget-optimizer`
3. **Activate** — `outreach-manager` → `content-reviewer` (⛩ ART-Gate) → `contract-helper` → `content-amplifier`
4. **Measure** — `landing-optimizer` → `performance-analyzer` → `roi-calculator` → `report-generator`

**Paid Ads (ROAS-Schleife)**
1. **Research** — `audience-segment-builder` → `campaign-architect`
2. **Orchestrate** — `ad-creative-builder` → `ad-test-designer` (+ `landing-optimizer` für die Seite)
3. **Activate** — `conversion-signal-qa` → `ad-account-auditor` (⛩ RQS-Gate), bevor irgendein Budget live geht
4. **Scale** — `paid-measurement-loop` → `attribution-reconciler` → `roi-calculator` → `report-generator`

**Email (SEND-Schleife)**
1. **Setup** — `deliverability-qa` → `list-segment-builder`
2. **Engage** — `email-creative-builder`
3. **Nurture** — `email-sequence-designer` → `newsletter-monetization-planner`
4. **Deliver** — `send-experiment-designer` → `email-quality-auditor` (⛩ EQS-Gate) vor dem Versand

Für eine vollständige Vertrauensprüfung kombiniere `content-quality-auditor` mit `domain-authority-auditor` zu einer kombinierten 120-Item-Bewertung. Mit aktivem `memory-management` bleiben Übergaben und offene Schleifen automatisch im HOT/WARM/COLD-Speicher erhalten.

---

## Repository-Struktur

```
narrative/{trace,architect,land,evaluate}/                  # Narrative — TALE (16, inkl. seines Gates)
seo-geo/{research,build,optimize,monitor}/                  # SEO/GEO (16, inkl. seiner 2 Gates)
influencer/{discover,plan,activate,measure}/                   # Influencer (16, inkl. seines Gates)
ad/research|orchestrate|activate|scale/            # Paid Ads — ROAS (16, inkl. seines Gates)
email/setup|engage|nurture|deliver/                  # Email — SEND (16, inkl. seines Gates)
launch/research|assemble|mobilize|prove/             # Launch — RAMP (16, inkl. seines Gates)
social/explore|craft|host|observe/                   # Social — ECHO (16, inkl. seines Gates)
protocol/                                            # Protokollschicht (8) — Wahrheitsregister + Speicher
commands/        # 8 Slash-Befehle (auto, narrative, seo-geo, influencer, ad, email, launch, social)
references/      # gemeinsamer Vertrag, Zustandsmodell, die 8 Benchmarks, Auditor-Runbook, Plattform-Packs
evals/           # strukturelle Eval-Fälle pro Skill + structure-manifest.json
hooks/           # hooks.json + claude-hook.sh (die einzige Laufzeitlogik)
scripts/         # validate-skill.sh + connectors/ (stdlib) + CI-Guards
memory/          # HOT/WARM/COLD-Gerüst + Register-Speicher (entities/creators/claims/consent/launch/channels/narrative-registry)
docs/            # lokalisierte READMEs (zh)
.claude-plugin/  # plugin.json + marketplace.json-Spiegel
```

---

## Designphilosophie

- **Skills sind Inhalt.** Der einzige Code ist der Bash-Validator, der Bash-Hook-Runner und Zero-Dependency-Python-Standardbibliothek-Konnektor/Check-Helfer. Niemals Drittanbieter- / `pip`-Abhängigkeiten — durch einen Dependency-Creep-Guard erzwungen.
- **Keyless zuerst.** Jede `~~category` hat ein kostenloses/eigene-Daten-Rezept; MCP und bezahlte Tools sind reiner Komfort.
- **Chirurgisch & MECE.** Jeder Skill besitzt eine Aufgabe mit einer klaren Scope-Grenze; überlappende Arbeit wird als *Modus* eines bestehenden Skills ausgeliefert statt als neuer dünner Skill. Register kuratieren, Gates urteilen, Analysatoren speisen Gates.
- **Keine erfundenen Zahlen.** Skills kennzeichnen jede Zahl mit Measured / User-provided / Estimated und liefern einen AI-Slop- / Banned-Phrase-Detektor.
- **Compliance ist Anleitung, nicht Gesetz.** FTC-Offenlegungs- und Claim-Integritäts-Prüfungen markieren Risiko; sie sind keine Rechtsberatung.

---

## Qualitäts-Guards (CI)

Jede Änderung läuft gegen eine Reihe von Fail-Closed-Guards (alle in `scripts/` und `tests/`):

| Guard | Prüft |
|-------|--------|
| `validate-skill.sh` | Frontmatter, erforderliche Abschnitte, Versionskonsistenz, plugin-relative Links über alle 120 Skills. |
| `golden-auditor-math.py` | Deterministische Gewichtssumme + Arithmetik der Musterbeispiele für **alle acht** Frameworks. |
| `check-evals.py` | Eval-Struktur-Lint + `structure-manifest.json` (120/120 Skills tragen Eval-Fälle). |
| `check-pii.py` | Blockiert committete Secrets / PII (Token-Level-Allowlist, Fail-Closed). |
| `check-stdlib-only.sh` | Dependency-Creep-Guard + die Paid-Ads-Keyed-API-Red-Line. |
| `check-versions.sh` | Versions-Sync-Guard: Bundle-Version identisch über plugin.json / beide marketplace-Spiegel / beide README-Badges / CLAUDE.md / VERSIONS.md-Release-Zeile + Changelog-Eintrag, und jede SKILL.md-Version stimmt mit ihrer VERSIONS.md-Zeile überein. |
| `tests/test_connectors_local.py` | Offline-Unit-Tests für die reinen Request-Builder jedes Konnektors (kein Netzwerk in CI). |
| `tests/test_hook_artifact_gate.sh` | Verhaltenstests für das Artifact Gate des Hooks + SessionStart-Bereinigung. |

Live-Endpunkt-Drift wird separat vom **manuellen** [`scripts/connectors/smoke-live.sh`](../scripts/connectors/smoke-live.sh) abgedeckt — ein minimaler echter Aufruf pro gehostetem Konnektor mit Shape-Assertions (Rate-Limit-Antworten zählen als SKIP); führe es vor einem Release aus, niemals in CI.

---

## Beitragen & Projektdokumente

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** — Authoring-Regeln, die Beitrags-Checkliste und die maßgebliche 8-Datei-Tracking-Liste.
- **[VERSIONS.md](../VERSIONS.md)** — Versionen pro Skill + Changelog (aktuelles Bundle: `16.0.0`).
- **[SECURITY.md](../SECURITY.md)** · **[PRIVACY.md](../PRIVACY.md)** · **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** — Sicherheits-, Datenschutz- und Community-Richtlinie.
- **[CLAUDE.md](../CLAUDE.md)** / **[AGENTS.md](../AGENTS.md)** — Agent-seitiger Kontext für dieses Repo.

---

## Haftungsausschluss

Diese Skills unterstützen Brand-Narrative-, SEO/GEO-, Influencer-Marketing-, Paid-Ads-, E-Mail-Marketing-, Produkt-Launch- und Organic-Social-Workflows, garantieren aber **nicht** Rankings, AI-Zitationen, Traffic, Engagement, Conversions, ROAS, Deliverability oder Geschäftsergebnisse. Influencer-, Ad-, E-Mail- und Social-Compliance-Prüfungen (FTC-Offenlegung, Claim-Integrität, Plattform-Policy, Consent/Opt-in, Material-Connection-Offenlegung) sind Anleitung, keine Rechtsberatung. Verifiziere Empfehlungen mit qualifizierten Fachleuten, bevor du dich bei größeren Strategie-, Finanz- oder Rechtsentscheidungen darauf verlässt.

## Lizenz

Apache License 2.0 — siehe [LICENSE](../LICENSE).

*Zuletzt mit dem englischen README synchronisiert: v16.0.3*

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
 </picture>
</a>
