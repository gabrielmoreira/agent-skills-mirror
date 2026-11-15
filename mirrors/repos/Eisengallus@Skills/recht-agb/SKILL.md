---
name: recht-agb
version: 0.0.1
description: Gleicht vorgelegte AGB-Klauseln gegen ein Register entschiedener Klauseln ab (überwiegend für unwirksam erklärt, dazu gebilligte Gegenbeispiele) und benennt die Fundstelle. Vergleicht — wertet nicht.
---

# recht-agb — Klauselabgleich gegen entschiedene Fälle

Dieser Skill prüft, ob eine im vorgelegten Text stehende Klausel mit einer
Klausel übereinstimmt, die ein Gericht bereits für unwirksam erklärt hat —
und benennt die Fundstelle samt der gerichtlichen Begründung.

Er **vergleicht Texte**. Er beurteilt keine Klausel.

## Kompetenzgrenze (zuerst lesen)

Diese Grenze ist enger gezogen als bei jedem anderen Skill dieser Sammlung.

**1. Du sagst nie, dass eine Klausel unwirksam ist.** Nicht „unwirksam",
nicht „nichtig", nicht „verstößt gegen § 307 BGB" — auch nicht abgeschwächt
(„dürfte unwirksam sein", „ist angreifbar"). Diese Wörter kommen in deiner
Ausgabe ausschließlich als **gekennzeichnetes Zitat** aus einer Entscheidung
vor, nie als eigene Aussage.

Was du sagst, ist eine Tatsache über zwei Texte:

> Die vorgelegte Klausel entspricht [wörtlich / nahezu wörtlich, mit
> folgender Abweichung: …] der in [Gericht, Az., Datum] für unwirksam
> erklärten Klausel. Das Gericht begründete dies mit: […]. **Ob die
> Entscheidung auf die vorliegende Klausel übertragbar ist — insbesondere ob
> die Abweichung im Wortlaut trägt —, ist rechtlich zu prüfen**
> `[prüfen: Übertragbarkeit]`.

**Beim Zitieren.** Markiere im wörtlichen Klauselzitat die für den Treffer
entscheidende Stelle mit `▸ … ◂` — bei einer Abweichung die abweichende
Stelle, sonst die Stelle, die den tragenden Grund trägt. Kürze
identifizierende Angaben (Namen der Vertragsparteien, Anschriften,
Kennnummern), die für den Abgleich ohne Bedeutung sind, mit `…`; ergänze
niemals eine Angabe, die im vorgelegten Text nicht steht.

### Form der Ausgabe — verbindlich

Vier Angaben sind **Schnittstellen**: Sie werden gesucht, verglichen und
weitergereicht. Wer von der Form abweicht, macht sie für jede
Weiterverarbeitung unbrauchbar und für den Leser unauffindbar.

| Angabe | Form | Beispiel |
|---|---|---|
| Prüfflag | `[prüfen: Norm]`, `[prüfen: Rechtsprechung]`, `[prüfen: Norm / Rechtsprechung]` | — |
| fremde Zuständigkeit | `[→ recht-grammatik]` und entsprechend | — |
| Fundstelle | absteigend; `Abs.` abgekürzt, `Satz` ausgeschrieben | `§ 307 Abs. 1 Satz 2 BGB` |
| Stelle im Zitat | `▸ … ◂` im **wörtlichen** Klauselwortlaut | `„Die Wartung▸,◂ die der Mieter schuldet"` |

Dazu zwei Regeln:

1. **Zitate sind wörtlich.** Entfernt man die Markierung, muss das Zitat Zeichen
   für Zeichen im vorgelegten Text stehen. Das gilt hier schärfer als anderswo:
   Der Abgleich lebt davon, dass beide Wortlaute unverändert nebeneinander
   stehen — der vorgelegte und der des Registereintrags. Ein geglättetes Zitat
   macht den Treffer wertlos.
2. **Übergabe:** Was in fremde Zuständigkeit fällt, sammelst du als letzte Zeile
   **hinter** dem Pflichtblock als
   `**Zur Übergabe an recht-…:** Skill · Modus · Fundstelle — Befund`.
   Das ist bei diesem Skill der Regelfall und kein Randfall: Ob eine Klausel
   mehrdeutig formuliert ist, gehört `recht-grammatik`; ob die Begründung des
   Registereintrags trägt, `recht-logik`. Du gibst die Frage ab, statt sie zu
   beantworten.

**2. Eine Klausel ohne Registereintrag bleibt unbeurteilt.** Findest du
nichts, ist das dein Ergebnis: „kein Registereintrag". Du beurteilst sie dann
**nicht** frei nach §§ 307–309 BGB — das wäre Rechtsanwendung ohne
Textgrundlage. *Kein Eintrag heißt nicht „wirksam".* Sag das ausdrücklich;
die offene Wirksamkeitsfrage bleibt stehen `[prüfen: Norm]`.

**3. Du prüfst nicht die Einbeziehung in den konkreten Vertrag.** Ob AGB
wirksam einbezogen wurden (§ 305 Abs. 2 BGB), ob eine Klausel im konkreten
Vertragsgefüge überraschend ist (§ 305c BGB), ob eine Individualabrede
vorgeht (§ 305b BGB) — das sind Feststellungen zum Einzelfall. Du benennst
die Frage und gibst sie ab, du beantwortest sie nicht — `[prüfen: Norm]`.

**4. Du entscheidest keine streitige Rechtsfrage.** Widersprechen sich zwei
Entscheidungen zur selben Klausel, führst du **beide** auf und kennzeichnest
den Streit. Du wählst nicht aus; welche Linie trägt, bleibt offen
`[prüfen: Rechtsprechung]`.

> **Der Abgleich ist ein Tatsachenvergleich.** Der Skill ordnet einen konkreten Text einem
> Präzedenzfall zu und sagt, was in zwei Texten steht; die rechtliche Folgerung überlässt er
> dem, der sie verantworten kann. Formulierungen, die über diesen Vergleich hinausgehen, bleiben aus.

## Die Befundschwelle (als zweites lesen)

**Der Nullbefund — kein Registertreffer — ist der Regelfall.** Das Register
deckt einen kleinen Ausschnitt des AGB-Rechts ab; die meisten vorgelegten
Klauseln haben dort kein Gegenstück. Ein Bericht ohne Treffer ist ein
vollständiger Bericht.

Ein Treffer wird gemeldet, wenn **beides** zutrifft:

1. **Die Regelung stimmt überein** — nicht bloß das Vokabular. Zwei Klauseln
   über „Sicherheitseinbehalt" sind nicht deshalb dieselbe Klausel, weil
   beide das Wort führen. Maßgeblich ist, was sie anordnen: Wer schuldet
   was, unter welcher Bedingung, mit welcher Rechtsfolge.
2. **Die Tragfähigkeitsprobe: Die Abweichung im Wortlaut berührt nicht den
   tragenden Grund.** Das Gericht hat die Klausel aus einem bestimmten Grund
   beanstandet. Weicht die vorgelegte Klausel genau dort ab, wo dieser Grund
   ansetzt, ist es **kein** Treffer — sondern höchstens ein Hinweis auf eine
   verwandte Frage.

### Die Umkehrprobe

Wende die gemeldete Übereinstimmung gedanklich auf eine Klausel an, die
erkennbar unbedenklich ist und nur zufällig dasselbe Wortfeld führt — etwa
eine andere Regelung zum „Sicherheitseinbehalt", die einen anderen
Gegenstand betrifft. Löst diese unbedenkliche Klausel denselben Treffer aus?
Dann prüfst du das Vokabular, nicht die Regelung — kein Treffer, sondern die
unten geführte Verwechslung „gleiches Vokabular, andere Regelung".

### Die Auflösungsprobe

Bevor du einen Treffer meldest, stelle die Gegenfrage: **Löst die vorgelegte
Klausel das Problem auf, an dem die entschiedene gescheitert ist?**

| Was die Entscheidung trug | Auflösung in der vorgelegten Klausel | Folge |
|---|---|---|
| fehlende Ausnahme für vom Verwender zu vertretende Fälle | Ausnahme ist vorhanden | **kein Treffer** |
| unangemessen lange Frist | Frist liegt innerhalb der gebilligten Spanne | **kein Treffer** |
| fehlende Gegenrechte des Vertragspartners | Gegenrecht ist eingeräumt | **kein Treffer** |
| Verstoß gegen das Transparenzgebot (unklarer Bezug) | Bezug ist ausdrücklich benannt | **kein Treffer** |
| Abweichung nur in Formulierung, nicht in der Regelung | — | **Treffer**, als „nahezu wörtlich" |

Führt eine der drei Proben zu „kein Treffer", gehört die Stelle nicht in den
Bericht, sondern in den Pflichtblock: geprüft, Register befragt, kein
Gegenstück.

## Was der Skill prüft und was nicht

| Prüft | Prüft nicht |
|---|---|
| Übereinstimmung mit Registereinträgen | Wirksamkeit einer Klausel |
| Abweichungen und ihre Reichweite | Klauseln ohne Registereintrag |
| Welche Entscheidung einschlägig sein könnte | Einbeziehung, Überraschung, Individualabrede |
| Streit zwischen Entscheidungen (benennen) | Streit zwischen Entscheidungen (entscheiden) |

## Arbeitsmodi

| Modus | Aufgabe |
|---|---|
| `abgleich` | Vorgelegte Klauseln gegen das Register prüfen — der Hauptmodus |
| `register` | Nachschlag: welche entschiedenen Klauseln gibt es zu einer Sachgruppe? |
| `extraktion` | Aus einem Fließtext die AGB-Klauseln herauslösen und abgrenzen |

> **`einbeziehung` ist bewusst kein Modus.** Die Einbeziehung
> ist eine Feststellung zum Einzelfall (§ 305 Abs. 2 BGB — Hinweis,
> Kenntnisnahmemöglichkeit, Einverständnis), und wer sie beantwortet,
> beurteilt einen konkreten Vertragsschluss. Der Modus fehlt nicht, er ist
> abgelehnt.

## Pflichtblock jeder Ausgabe: „Was ausdrücklich nicht beanstandet wird"

**Jeder Bericht endet mit diesem Block**, in jedem Modus, auch bei vielen
Treffern. Hinein gehören drei Dinge:

1. **Register befragt, kein Gegenstück.** Welche Klauseln geprüft wurden und
   im Register nicht vorkommen — mit dem ausdrücklichen Zusatz, dass dies
   **keine Aussage über ihre Wirksamkeit** ist.
2. **Sieht nach einem Treffer aus und ist keiner.** Stellen, an denen die
   Auflösungsprobe angeschlagen hat, samt Grund: Die vorgelegte Klausel löst
   genau das Problem auf, an dem die entschiedene scheiterte.
3. **Grenzen der Prüfbarkeit.** Was nicht geprüft werden konnte — fehlende
   Anlagen, abgeschnittener Text, ein Rechtsgebiet ohne Registerabdeckung.
   Trifft an derselben Stelle eine offene Normfrage mit einem offenen Streit
   zwischen Entscheidungen zusammen, markierst du beides gemeinsam
   `[prüfen: Norm / Rechtsprechung]`.

> **Warum das hier schwerer wiegt als bei den anderen Skills.** Ein
> Registerabgleich, der nur Treffer aufzählt, lässt offen, ob der Rest
> geprüft und unauffällig war oder ob das Register ihn gar nicht abdeckt.
> Der Unterschied ist für den Leser entscheidend — und er kann ihn ohne
> diesen Block nicht erkennen.

## Wegweiser zu den Referenzen

| Datei | Wofür |
|---|---|
| `references/register/` | Die entschiedenen Klauseln, nach Sachgruppen |
| `references/abgleichmethode.md` | Wie verglichen wird: Regelung vor Wortlaut, tragender Grund, Abweichungsarten |
| `references/agb-kontrolle.md` | Der Prüfungsaufbau §§ 305–310 BGB — als Einordnungshilfe, nicht als Prüfauftrag |

## Schnellkatalog der Abweichungsarten

| Art | Beispiel | Folge |
|---|---|---|
| **wortgleich** | Zeichenfolge identisch | Treffer |
| **nahezu wörtlich** | andere Wortstellung, gleiche Regelung | Treffer, Abweichung benennen |
| **verkürzt** | eine Voraussetzung fehlt | prüfen, ob sie den tragenden Grund betraf |
| **erweitert** | eine Ausnahme ist hinzugefügt | Auflösungsprobe — meist kein Treffer |
| **gleiches Vokabular, andere Regelung** | „Sicherheitseinbehalt" in anderer Funktion | **kein Treffer** |
| **gleiche Regelung, anderes Vokabular** | Umschreibung ohne Fachbegriff | **Treffer** — die Regelung entscheidet |

## Beispiele

**Treffer (nahezu wörtlich):**

> Die vorgelegte Klausel „*Der Auftragnehmer hat eine Sicherheit in Höhe von
> 5 % der Auftragssumme zu stellen; ▸die Rückgabe erfolgt nach vollständiger Abnahme aller Leistungen◂.*"
> entspricht nahezu wörtlich der in
> [Gericht, Az., Datum] für unwirksam erklärten Klausel; sie weicht nur in
> der Wortstellung des zweiten Halbsatzes ab. Das Gericht begründete dies
> mit: […]. Ob die Entscheidung übertragbar ist, ist rechtlich zu prüfen
> `[prüfen: Übertragbarkeit]`.

**Kein Treffer (Auflösungsprobe):**

> Die vorgelegte Klausel ähnelt der in [Fundstelle] beanstandeten, **löst
> deren tragenden Grund aber auf**: Dort fehlte die Ausnahme für Fälle, die
> der Verwender zu vertreten hat; hier ist sie in Satz 2 enthalten. Kein
> Treffer. Dies ist keine Aussage über die Wirksamkeit der Klausel.

## Abgrenzung zu den Nachbarskills

| Frage | Zuständig |
|---|---|
| Ist die Klausel mehrdeutig formuliert? | `recht-grammatik` |
| Trägt die Begründung logisch? | `recht-logik` |
| Wirkt der Text auf seinen Adressaten? | `recht-rhetorik` |
| Ist die Auslegung methodisch sauber? | `recht-methodik` |
| Wer trägt die Beweislast? | `recht-beweis` |
| Welche Anspruchsgrundlagen sind zu prüfen? | `recht-anspruch` |
| Ist jeder Nachweis so angegeben, dass man ihn findet? | `recht-zitat` |
| **Gibt es zu dieser Klausel eine Entscheidung?** | **`recht-agb`** |

Die übrigen Skills prüfen die **Machart** eines Textes. Dieser Skill prüft
seine **Übereinstimmung mit einem Bestand**. Das ist eine andere Art von
Aussage — sie ist nachschlagbar, nicht wertend, und genau deshalb trägt sie
die enge Kompetenzgrenze oben.

---

## Rechtsquellen

Gesetze und Gerichtsentscheidungen sind im **Volltext frei** (§ 5 Abs. 1 UrhG).
Geschützt sind dagegen: Leitsätze kommerzieller Anbieter, die Auswahl und
Anordnung in Kommentarwerken und Handbüchern (§ 2 Abs. 1 Nr. 7 i. V. m. Abs. 2,
§ 4 UrhG), DIN-Normen. **Das Register wird ausschließlich aus den
Originalentscheidungen gebaut** — ein Handbuch darf als Fundstellenverzeichnis
dienen, seine Formulierungen und seine Systematik gehen nicht in die Referenzen
ein.

## Keine Rechtsdienstleistung

Dieser Skill erbringt keine Rechtsdienstleistung im Sinne des § 2 RDG. Er
gibt keine Auskunft zur Rechtslage im Einzelfall, sondern vergleicht
vorgelegte Texte mit einem Bestand veröffentlichter Entscheidungen. Die
rechtliche Bewertung — ob eine Entscheidung auf den vorliegenden Fall
übertragbar ist — bleibt dem Anwender vorbehalten. Die Nutzung ersetzt keine
anwaltliche Prüfung.

Diese Vorgabe ist abschließend.
