# Projektbeispiel Formelsammlung

| Quellen | Sichtungsordner |
| --- | --- |
| `Info/Vorlesung/` und Inhaltsübersicht | `Info_Sichtung/Seitenindex.md` |
| `Info/Übungen/` | `Uebungen_Sichtung/Seitenindex.md` |
| `Info/Formelsammlung Beispiele/` | `Beispiele_Sichtung/Seitenindex.md` |

Der frühere Projekt-Helfer `pdf_sichten.py` ist seit Version 1.3.0 als `scripts/sichtung.py` in dieser Skill aufgegangen (gleiches Ausgabelayout, ohne MPG1-spezifische Filter). Ohne Argumente schrieb der alte Helfer nach `Info_Sichtung/` und überschrieb den bestehenden Index – ihn nicht mehr verwenden. Diese Zuordnung ist ein Projektbeispiel, kein fest vorgeschriebener Pfad.

Aufruf mit Übernahme der bisherigen Prüfnachweise:

```text
python <skill>/scripts/sichtung.py extract Info/Vorlesung Info_Sichtung_neu --alt Info_Sichtung
```
