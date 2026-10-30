# Repository-Konfiguration

Prüfdatum: 22.10.2026. Einstellungen auf GitHub können sich nach diesem Datum ändern.

| Bereich | Konfiguration |
| --- | --- |
| Sichtbarkeit und Lizenz | Öffentlich, MIT, Hauptzweig `main` |
| Hauptzweig | Pull Request erforderlich; keine externe Genehmigung nötig; offene Review-Diskussionen müssen erledigt sein |
| Pflichtprüfungen | `Python 3.12 / ubuntu-latest` und `Python 3.12 / windows-latest`, aktueller Basisstand erforderlich |
| Schutzumfang | Gilt auch für Administratoren; Force-Push und Löschen von `main` verboten |
| Geheimnisse | GitHub Secret-Scanning und Push-Schutz aktiviert |
| Abhängigkeiten | Dependabot-Warnungen aktiviert; automatische Sicherheits-Updates sind nicht aktiviert |
| Actions | Standard-Token nur lesend; automatische PR-Genehmigung durch Workflows deaktiviert |
| Workflow-Abhängigkeiten | Verwendete Actions auf konkrete Commit-SHAs festgelegt |
| Veröffentlichung | Nur Release-Job mit Schreibrecht; neuer Versions-Tag erzeugt nach Prüfungen einen Entwurf mit ZIP und SHA-256-Datei |
| Copilot-Umgebung | Separater Setup-Workflow mit Leserecht bereitet Python/PDF-Abhängigkeiten vor; der GitHub-Skill-Einstieg verweist auf die verbindliche Root-Datei |

## ECC-Integration

ECC kommentiert die PR-Prüfungen, meldet jedoch fehlende Berechtigung zum Veröffentlichen eigener GitHub Checks. Dafür müsste der App-Betreiber „Checks: read and write“ bereitstellen und der Installationsinhaber die Änderung genehmigen. Diese Berechtigung wurde nicht erweitert. ECC-Kommentare sind deshalb keine verpflichtenden Statusprüfungen; die beiden tatsächlich veröffentlichten GitHub-Actions-Prüfungen sichern den Merge.

## Release-Verifikation

Vor einem Tag müssen die Prüfungen für den exakten Release-Commit grün sein. Nach dem Release-Job ZIP und `SHA256SUMS` erneut von GitHub herunterladen, den ZIP-Hash prüfen und jede enthaltene Datei byteweise mit dem Tag vergleichen. Erst dann den Entwurf veröffentlichen und den öffentlichen Release samt Assets zurücklesen. Vorhandene Versions-Tags nicht verschieben.

## Manueller Release-Start ab v1.5.0

Die vorhandene Release-Action unterstützt zusätzlich `workflow_dispatch` mit einer Versionsangabe wie `v1.5.0`. Nach erfolgreicher Pflicht-CI wird sie auf `main` gestartet. Sie prüft Version, Selbsttest, Plattformtest, Vault und Dateihashes, setzt danach einen neuen Tag auf den exakten Workflow-Commit und erzeugt ZIP, SHA-256-Datei und Entwurf. Vorhandene Tags werden nicht überschrieben. Die Schreibrechte bleiben auf den bestehenden Release-Job begrenzt. Anschließend weiterhin Download und byteweisen Tagvergleich durchführen, bevor der Entwurf veröffentlicht wird.
