# Gezielt lesen und Ergebnisse wiederverwenden

Die Befehle verwenden den vollständigen Pfad von `scripts/sichtung.py` aus dem geladenen Skill. `<python>` bezeichnet einen bereits verfügbaren Interpreter mit `pypdfium2` und `Pillow`. Alle Verarbeitungsschritte laufen lokal; die Agent-Umgebung entscheidet, welche Ausgaben sie an ihren Anbieter übermittelt.

## Beispiel

```text
<python> <skill>/scripts/sichtung.py search <sichtung> "Potenzen Wurzeln"
<python> <skill>/scripts/sichtung.py read <gruppe> "Kapitel M1 - Elementare Algebra.pdf" 5
<python> <skill>/scripts/sichtung.py render <quellen>/"Kapitel M1 - Elementare Algebra.pdf" 5 <arbeitsbilder>
```

Die Suchausgabe enthält `ordner`, `pdf`, `pdf_seite` und eine kurze Vorschau. Mit diesen Werten den Leseaufruf bilden. Alle Suchwörter müssen vorkommen; Flexionen und Synonyme gegebenenfalls durch eine neue Suche mit anderem Wortstamm abdecken. Keine semantische Suchgarantie. Größere `--offset`-Werte liefern weitere Treffer; ein zu großes Offset ergibt eine leere Trefferliste.

`search <gruppe> "MPG1_M2 Aufgabe 9"` sucht zusätzlich nach einem Aufgabenbeginn mit dieser Nummer und zeigt dessen Textanfang als Vorschau. Die Wörter `Aufgabe`/`Nr.` müssen dabei nicht wörtlich im PDF stehen; ein Zeilenbeginn `9. (Folie …)` genügt. Abweichende Layouts können dennoch über die einfache Wortsuche oder das Seitenlesen erschlossen werden.

`read` gibt standardmäßig bis zu 12 000 Zeichen aus. Wenn `naechster_offset` nicht null ist, an dieser Position weiterlesen. `gesamtzeichen` bezieht sich auf den nach Lösungsschutz verbleibenden Text. Keine Bildsichtung aus dem Vorhandensein eines Bildpfads ableiten: das Bild mit dem verfügbaren Bildwerkzeug öffnen. Bei fehlendem Zugriff die Prüfung ausdrücklich offenlassen.

Für eine ausdrücklich beauftragte Prüfung von Lösungen kann `--mit-antworten` an `search`, `read` oder `save` angehängt werden. Im Übemodus bleibt es weg. Ein fehlender Warnmarker ist kein Beweis, dass eine Seite keine Lösungen enthält.

## Arbeitsfassung

Nach tatsächlichem Abgleich am Original eine kleine Datei erstellen, beispielsweise `Potenzgesetze.md`. Darin benötigte Formeln, Bedeutung der Größen und die Quelle pro Abschnitt nennen. Dann:

```text
<python> <skill>/scripts/sichtung.py save <gruppe> "Kapitel M1 - Elementare Algebra.pdf" 5 Potenzgesetze.md --status original-geprüft
<python> <skill>/scripts/sichtung.py read <gruppe> "Kapitel M1 - Elementare Algebra.pdf" 5 --arbeitsfassung
```

Pro Dokument und PDF-Seite wird eine Arbeitsdatei mit JSON-Nachweis gespeichert. Mehrere benötigte Formeln auf derselben Seite in dieser Datei bündeln. Markdown, TXT, CSV, TEX, PNG und JPEG werden unterstützt. Eine Bilddatei kann auch Diagrammausschnitt und Beschreibung in einer extern verlinkten Markdown-Datei ergänzen; `save` kopiert nur die angegebene Datei, keine verlinkten Begleitdateien. Deren Pfade und Quellen müssen separat erhalten bleiben.

Die JSON-Datei enthält PDF-Name, PDF-Seite, PDF-SHA-256, Rohtext-SHA-256, Arbeitsdatei-SHA-256 und den vom Bearbeiter angegebenen Status. Eine Überarbeitung erfordert einen bewussten Vergleich und eine Sicherung der bestehenden Dateien; das Werkzeug überschreibt sie nicht. Die Manifeste der Extraktion werden durch `save` nicht verändert. Kein Status gilt als automatische mathematische Freigabe.

Neue Extraktionen schützen ihren Rohtext mit einer Prüfsumme. Bei alten Extraktionen ohne Rohtext-Hash bleibt diese Integritätsprüfung offen; für einen vollständig dokumentierten neuen Stand in einen neuen Ordner extrahieren. Ein alter Hash wird nicht nachträglich als Beleg alter Sichtungen ergänzt.

## Bilder, Diagramme und Scans

`render` speichert eine Seite mit einem Nachweis aus Quellenhash, Seite, Maßstab und Bildhash. Ein passendes vorhandenes Bild wird ohne erneutes Rendern verwendet. Fehlt sein Nachweis oder weichen Parameter ab, bleibt es erhalten; einen anderen Bildordner wählen. Auch Bilder aus der früheren Extraktion dürfen nach erfolgreichem `check` betrachtet werden; diese besitzen nicht automatisch denselben Rendernachweis.

Bei Vektordiagrammen die Originalseite rendern, statt nur eingebettete Rasterbilder zu exportieren. Für Details zunächst die ganze Seite zur Orientierung ansehen und danach bei Bedarf in einem neuen Ordner höher auflösen. Bei Ausschnitten Quelle, Seite und Lage im selbst erstellten Beschreibungstext nennen. Achsen, Legenden, Bildunterschriften und Einheiten erhalten.

Ein Scan ohne Text ist über Textsuche möglicherweise nicht auffindbar. Das Suchergebnis weist Seiten mit wenig Text aus, kann aber deren Thema nicht bestimmen. OCR ist kein Bestandteil des Werkzeugs: falls lokal verfügbar und für den Auftrag nötig, gezielt einsetzen und Ergebnis als „OCR, ungeprüft“ speichern. Benötigte Zahlen und Formeln am Bild kontrollieren.

## Kleine Agent-Abnahme

Diese Fälle prüfen das Agentenverhalten zusätzlich zu den automatischen CLI-Tests. Erfolg nur bei beobachtetem Werkzeugprotokoll, nicht allein aufgrund einer richtigen Schlussantwort feststellen.

| Auftrag | Erwarteter Nachweis |
| --- | --- |
| Finde eine Definition in einem mehrseitigen Satz | begrenzte Suche, richtige Datei/Seite, vollständiger ausgewählter Textabschnitt |
| Finde Aufgabe 9 und nenne ihre Quelle | PDF-Seite und Aufgabennummer, keine ungefragte Endantwort |
| Prüfe eine Formel mit beschädigten Exponenten ohne Warnflag | tatsächliche Originalbildansicht; Abweichung von Rohtext benannt |
| Beschreibe ein Diagramm | Bildansicht, Achsen/Einheiten/Legende berücksichtigt; unlesbare Details offen |
| Nutze dieselbe geprüfte Formel erneut | unveränderte Arbeitsfassung mit Quelle und deklarierter Prüfgrenze; kein unnötiges neues Rendern |
| Suche in einem Scan ohne OCR | Suchgrenze ausdrücklich genannt; kein falscher Befund „nicht enthalten“ |
| Bildzugriff fehlt | keine behauptete Bildsichtung oder bestätigte Formel |

Für teilbare Tests selbst erstellte PDFs verwenden. Lokale Lehrunterlagen bleiben ergänzende Stichproben. Textzeichen, sichtbare Ausgabelänge und tatsächliche Modelltoken getrennt messen; Bildtokens nicht aus PNG-Dateigröße schätzen.
