# Hinweise für KI-Agenten

Dieses Repository enthält den Skill `pdf-seitenweise-sichten`: lokale PDFs über Seitenindex und seitenweise Markdown-Dateien sparsam sichten. Die Verfahrensanweisungen für die Nutzung stehen nur in [SKILL.md](SKILL.md).

## Installation für Nutzer

Wenn ein Nutzer dich bittet, das Werkzeug einzurichten:

1. Python 3.12 oder neuer prüfen (`python --version`, unter macOS/Linux `python3`). Fehlt `pypdfium2` oder `Pillow`, den Nutzer fragen und dann `python -m pip install -r scripts/requirements.txt` aus dem Skill-Ordner ausführen. Keine Systemeinstellungen oder Ausführungsrichtlinien ändern.
2. Passenden Weg wählen:
   - **Claude Code:** `/plugin install pdf-seitenweise-sichten --marketplace Sae-l/pdf-seitenweise-sichten`
   - **Codex:** `codex plugin marketplace add Sae-l/pdf-seitenweise-sichten` und `codex plugin add pdf-seitenweise-sichten@sae-l-skills`, danach neue Sitzung
   - **Cursor, VS Code/Copilot oder ein bestimmtes Projekt:** Repository klonen, dann `python scripts/install_projekt.py "<vorhandener-projektordner>"`
   Meldet Windows `Filename too long`, den Nutzer fragen, ob `git config --global core.longpaths true` gesetzt werden darf, und dann wiederholen.
3. Prüfen: `python <skill-ordner>/scripts/sichtung.py --help` muss die Befehle `extract`, `check`, `search`, `read`, `render`, `save` zeigen.
4. Erste Nutzung: `extract <pdf-ordner> <neuer-ausgabeordner>`, danach `search` und `read` wie in SKILL.md. Ausgabeordner nie in den PDF-Ordner legen und nie überschreiben.

Details und Grenzen (Cloud ohne lokale Laufwerke, Updates): [docs/installation.md](docs/installation.md).

## Arbeit am Repository

- Prüfungen wie in der CI (benötigt `reportlab`):
  ```sh
  python -m pip install -r scripts/requirements.txt reportlab
  python scripts/selbsttest.py
  python scripts/plattformtest.py
  python Obsidian-Plan/Pruefung/vault_pruefen.py
  python scripts/plugin_paket.py --check
  python scripts/pruefsummen.py
  ```
- Nach Änderungen an `SKILL.md`, `scripts/`, `references/` oder `ARCHIVE.json`: `python scripts/plugin_paket.py`. `plugins/` ist eine erzeugte Kopie und wird nie von Hand bearbeitet.
- Danach `python scripts/pruefsummen.py --fix`. Das Skript erneuert `SHA256SUMS` und `skill_sha256` in `ARCHIVE.json`. Neue Dateien zuerst als Zeile in `SHA256SUMS` eintragen.
- `.gitattributes` setzt `* -text`: Zeilenenden jeder Datei unverändert lassen (`CHANGELOG.md` hat CRLF, die Skripte haben LF). Steuerzeichen wie `U+FFFE` im Quelltext als Escape `\ufffe` schreiben, nie als echtes Zeichen.
- Lehrmaterialien, Kurs-PDFs und erzeugte Sichtungen gehören nicht ins Repository (siehe `.gitignore`); für Tests synthetische PDFs mit `reportlab` erzeugen.
- Einträge in `CHANGELOG.md` unter „Unveröffentlicht“; Commit-Titel kurz, z. B. `fix: …`, `feat: …`, `docs: …`. Weiteres in [CONTRIBUTING.md](CONTRIBUTING.md).
