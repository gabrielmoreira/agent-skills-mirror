# Mitwirken

Danke für nachvollziehbare Fehlerberichte und kleine, gezielte Verbesserungen.

## Fehler melden

Eröffne ein [Issue](https://github.com/Sae-l/pdf-seitenweise-sichten/issues/new) mit:

- verwendetem Release oder Commit;
- Betriebssystem, Python-Version und ausgeführtem Befehl;
- erwartetem und tatsächlichem Ergebnis sowie einer passenden Fehlermeldung;
- möglichst einer kleinen, selbst erstellten Beispieldatei.

Keine vertraulichen Unterlagen, Zugangsdaten oder fremden Lehrmaterialien veröffentlichen. Bei fehlerhaften Formeln PDF-Seite und beobachtete Extraktionsabweichung nennen; technische Fehler und fachliche Prüfung unterscheiden.

## Eine Änderung vorbereiten

Vorhandene Python-Muster und Ausgabeformate beibehalten. Neue nichttriviale Logik mit einem kleinen sinnvollen Regressionstest absichern. Originaldateien, manuelle Nachweise und vorhandene Arbeitsfassungen erhalten. Keine neue Laufzeitabhängigkeit für wenige Zeilen Hilfscode hinzufügen.

Für die Entwicklung das vollständige Repository auf einem eigenen Branch verwenden. Commit-Titel kurz und konkret halten, beispielsweise `fix: reject missing rendered images` oder `docs: clarify project installation`.

## Lokal prüfen

Nach dem Bereitstellen der Abhängigkeiten im Repository:

```sh
python -m pip install -r scripts/requirements.txt reportlab
python scripts/selbsttest.py
python scripts/plattformtest.py
python Obsidian-Plan/Pruefung/vault_pruefen.py
```

Gesperrte lokale Plattformtests ausdrücklich als übersprungen melden. Sicherheitsrichtlinien nicht umgehen; die Pflicht-CI muss alle Plattformfälle ohne Skips ausführen. Eine technische Prüfung bestätigt keine mathematische Richtigkeit oder vollständige Agent-Kompatibilität.

Nach Änderungen an `SKILL.md`, `scripts/`, `references/` oder `ARCHIVE.json` das Plugin-Paket mit `python scripts/plugin_paket.py` neu erzeugen. Danach `python scripts/pruefsummen.py --fix` ausführen; das erneuert `SHA256SUMS` und `skill_sha256` in `ARCHIVE.json`. Bei absichtlichen Vault-Änderungen dessen Manifest über `vault_pruefen.py --write` erneuern. Prüfsummen dokumentieren den Stand; sie ersetzen den Review nicht.

Der Pull Request beschreibt Problem, resultierendes Verhalten, ausgeführte Prüfungen und offene Grenzen. Die Windows-/Linux-Pflichtprüfungen müssen vor dem Merge bestehen. Details zum Release-Weg stehen in der [Repository-Konfiguration](docs/repository-konfiguration.md).
