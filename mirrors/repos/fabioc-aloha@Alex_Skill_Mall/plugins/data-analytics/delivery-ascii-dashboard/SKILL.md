---
type: skill
lifecycle: stable
inheritance: inheritable
name: delivery-ascii-dashboard
description: Render data dashboards as pure ASCII art in monospace text -- the cheapest, most portable delivery method. No rendering engine, no SVG, no browser. LLM-native output with predictable character geometry.
tier: standard
applyTo: '**/*ascii*,**/*text*dashboard*,**/*terminal*,**/*console*,**/*plain*'
currency: 2026-05-02
lastReviewed: 2026-05-02
---

# Delivery: ASCII Dashboard

Render dashboards as pure ASCII art. No emojis, no Unicode box-drawing beyond the basic set, no external renderer. The output is a monospace text block that looks correct in any terminal, any markdown code fence, any log file, any LLM context window.

This is the cheapest delivery method: zero dependencies, zero tokens spent on SVG coordinates, predictable character geometry. An LLM can produce and validate the output in the same context window.

## When to Use

- Quick status snapshots in terminal output, log files, or commit messages
- Chat-based reporting where the consumer is another LLM or a terminal user
- Environments where SVG/HTML rendering is unavailable (CI logs, SSH sessions, plain-text email)
- Token-constrained contexts where SVG coordinate math would waste budget
- Rapid prototyping before committing to a richer delivery format

## When NOT to Use

- The audience expects polished visuals (use `delivery-svg-markdown` or `delivery-html-dashboard`)
- Charts require color encoding for meaning (ASCII is monochrome)
- More than 80 columns of data (wrapping breaks the layout)
- Interactive filtering or drill-through is required

## Module 1: Character Geometry

ASCII dashboards are predictable because every character occupies exactly one cell in a monospace grid. No emoji, no CJK, no combining characters.

### Grid Constants

| Constant | Value | Rationale |
| --- | --- | --- |
| Max width | 78 characters | Fits 80-column terminals with 1-char margin each side |
| Card padding | 1 character inside each border | Readable without waste |
| Column gap | 2 characters (`  `) | Visually separates side-by-side cards |
| Row gap | 1 blank line | Separates card rows |
| Title centering | Centered within card width | Visual anchor |
| Number alignment | Right-aligned within column | Scannable |

### Box-Drawing Characters

Use only the basic ASCII set for maximum portability:

| Element | Characters | Example |
| --- | --- | --- |
| Horizontal border | `-` | `------------------` |
| Vertical border | `|` | `| content |` |
| Corners | `+` | `+--+` |
| Separator | `=` or `-` | `+==================+` |
| Bar fill | `#` | `######` |
| Bar empty | `.` or space | `......` |
| Sparkline up | `/` | |
| Sparkline down | `\` | |
| Sparkline flat | `_` | |
| Bullet | `*` | `* item` |

### Why No Emojis

Emojis render as 1 or 2 cells depending on the terminal, font, and OS. A green circle `🟢` might be 1 cell in VS Code and 2 cells in Windows Terminal. This breaks column alignment. ASCII characters are always 1 cell, always predictable.

Status indicators use letters instead:

| Status | ASCII | Meaning |
| --- | --- | --- |
| Complete | `[x]` | Done |
| In progress | `[-]` | Active |
| Not started | `[ ]` | Pending |
| Pass | `[OK]` | Check passed |
| Fail | `[!!]` | Check failed |
| Warning | `[??]` | Needs attention |

## Module 2: Layout Patterns

### KPI Strip (single row of metrics)

```text
+----------------+  +----------------+  +----------------+
|   REVENUE      |  |   USERS        |  |   CHURN        |
|   $4.2M        |  |   12,847       |  |   3.1%         |
|   +12% YoY     |  |   +892 MoM     |  |   -0.4pp       |
+----------------+  +----------------+  +----------------+
```

Width per card = `(78 - (N-1)*2) / N` where N = number of cards. For 3 cards: 24 chars each.

### Horizontal Bar Chart

```text
Revenue by Region
==========================================
North America  | #################### | 42%
Europe         | ###########          | 23%
Asia Pacific   | #########            | 19%
Latin America  | #####                | 11%
Other          | ##                   |  5%
==========================================
```

Bar width = total width - label width - value width - borders. Fill character `#`, empty is space. Labels left-aligned, values right-aligned.

### Sparkline Row

```text
Trend (12 months):  _/\__/\/\___/\  High: 4.2M  Low: 2.1M
```

Characters: `/` = up, `\` = down, `_` = flat, `^` = peak. One character per data point. Keep to 20 characters max (readable at a glance).

### Two-Column Dashboard

```text
+------------------------------------+  +------------------------------------+
|  SALES PIPELINE                    |  |  SUPPORT TICKETS                   |
+------------------------------------+  +------------------------------------+
|                                    |  |                                    |
|  Q1   | ########           | $2.1M |  |  Open     | ###########    |  127  |
|  Q2   | ###########        | $2.8M |  |  Pending  | ######         |   68  |
|  Q3   | ###############    | $3.7M |  |  Closed   | ############## |  156  |
|  Q4   | ################## | $4.2M |  |  Overdue  | ##             |   23  |
|                                    |  |                                    |
|  Trend: __/\/\__/\  YTD: $12.8M   |  |  Avg resolution: 4.2 days         |
+------------------------------------+  +------------------------------------+
```

Each column = `(78 - 2) / 2 = 38` characters wide (including borders). Gap = 2 chars.

### Full Dashboard (3 rows)

```text
+==============================================================================+
|                        FLEET STATUS -- 2026-05-02                            |
+==============================================================================+

+----------------+  +----------------+  +----------------+  +----------------+
|  HEIRS         |  |  UPGRADED      |  |  PENDING       |  |  PLUGINS       |
|     41         |  |      8         |  |     33         |  |    279         |
|  total fleet   |  |  [x] v0.9.9   |  |  [-] queued    |  |  in Mall       |
+----------------+  +----------------+  +----------------+  +----------------+

+------------------------------------+  +------------------------------------+
|  VERSION DISTRIBUTION              |  |  TOP PLUGINS                       |
+------------------------------------+  +------------------------------------+
|  v0.9.9    | ####           | 19%  |  |  mermaid-mode   | #########  |  7  |
|  no-marker | ############## | 68%  |  |  academic-paper  | #          |  1  |
|  v0.6.2    | #              |  5%  |  |  data-story      | #          |  1  |
|  v0.9.1    | #              |  2%  |  |  chart-interp    | #          |  1  |
|  other     | #              |  5%  |  |  exec-story      | #          |  1  |
+------------------------------------+  +------------------------------------+

+---------------------------------------------------------------------------+
| NEXT: node scripts/fleet-upgrade.cjs --apply    33 heirs ready            |
+---------------------------------------------------------------------------+
```

## Module 3: Construction Rules

### Rule 1: Compute widths before drawing

```text
total_width = 78
n_columns = 2
gap = 2
card_width = (total_width - (n_columns - 1) * gap) / n_columns
bar_area = card_width - label_width - value_width - 4  (borders + padding)
```

Never eyeball widths. Compute from the grid constants, then fill.

### Rule 2: Right-align numbers, left-align labels

```text
WRONG:  North America | ############ | 42%
RIGHT:  North America  | ############ |  42%
```

Numbers scan faster when the ones digit is in a fixed column.

### Rule 3: Sort bars by value (unless time-ordered)

Largest bar on top. The eye scans top-down; put the story first.

### Rule 4: One header per card, centered

```text
+------------------------------------+
|          VERSION DISTRIBUTION       |
+------------------------------------+
```

Center the title within the card width. No bold, no underline (not portable). Caps or title case for visual weight.

### Rule 5: Footer row for actions

The last row of the dashboard is the call to action. It spans the full width and contains the one thing the reader should do next.

### Rule 6: Validate with character count

After generating, count characters per line. Every line within a card must have the same length. If not, padding is wrong. This is the advantage of ASCII: you can validate by counting.

## Module 4: Generating from Data

### Input Format

The dashboard takes a simple JSON or table structure:

```json
{
  "title": "Fleet Status",
  "date": "2026-05-02",
  "kpis": [
    { "label": "HEIRS", "value": "41", "detail": "total fleet" },
    { "label": "UPGRADED", "value": "8", "detail": "[x] v0.9.9" }
  ],
  "charts": [
    {
      "title": "Version Distribution",
      "type": "bar",
      "items": [
        { "label": "v0.9.9", "value": 19 },
        { "label": "no-marker", "value": 68 }
      ]
    }
  ],
  "footer": "NEXT: node scripts/fleet-upgrade.cjs --apply"
}
```

### Generation Algorithm

1. Compute grid layout (how many columns, card widths)
2. Render each component into a string array (one string per line)
3. For multi-column layouts, zip the line arrays side by side with gap spacing
4. Pad every line to its card width (right-pad with spaces inside borders)
5. Validate: every line in a card has identical character count
6. Join with newlines
7. Run the Alignment QA Loop (see below)

## Module 5: Alignment QA Loop

After generating the dashboard, run a mechanical validation before writing the output file. This is mandatory. Do not skip it. Do not self-report "all lines OK" without actually measuring. "Looks correct" is not a measurement.

### The Problem This Solves

LLMs cannot reliably count characters in generated text. The model will produce lines it believes are 78 characters but are actually 77, 79, or 80. This is not a rare edge case; it happens on nearly every generation. The only reliable fix is to measure after generation and fix before delivery.

### Validation Method

Use `run_in_terminal` to measure every line. This is the ONLY acceptable validation method. Mental counting or estimation is not acceptable.

PowerShell:
```powershell
$lines = Get-Content "<file>"
$fails = $lines | Where-Object { $_.Length -gt 0 -and $_.Length -ne 78 }
if ($fails) { $fails | ForEach-Object { "$($_.Length): $_" } }
else { "ALL LINES OK (78 chars)" }
```

### Construction Method (prevents most failures)

Do not freehand ASCII lines. Use a padding function to construct each line:

```
function Row(content):  return "| " + content.padRight(74) + " |"
function Border(char):  return "+" + (char * 76) + "+"
```

For side-by-side panels:
```
function DualRow(left, right):
  L = "| " + left.padRight(34) + " |"
  R = "| " + right.padRight(34) + " |"
  return L + "  " + R
```

Generate lines using these functions, then validate. This approach prevents most misalignment on first pass.

### Width Constants (do not deviate)

| Element | Formula | Result |
| --- | --- | --- |
| Total line width | fixed | 78 |
| Full-width border | `+` + 76 dashes + `+` | 78 |
| Full-width inner | `\| ` + 74 content + ` \|` | 78 |
| Side-by-side border | `+` + 36 + `+` + `  ` + `+` + 36 + `+` | 78 |
| Side-by-side inner | `\| ` + 34 + ` \|` + `  ` + `\| ` + 34 + ` \|` | 78 |

The width is 78, NOT 80. Common mistake: using 80 as the target because "80-column terminal." The 1-char margin on each side means content is 78.

### Fix-and-Recheck Loop

If any line fails:

1. Identify the failing lines (line number + measured width + content)
2. Determine whether the line is too long (trim trailing content before `|`) or too short (add spaces before closing `|`)
3. Apply the fix
4. Re-run the terminal measurement command
5. Repeat until zero failures

Do NOT write the output file until the measurement passes with zero failures. A dashboard with misaligned edges is a rendering bug, not a cosmetic issue.

## Anti-Patterns

| Anti-pattern | Fix |
| --- | --- |
| Using emojis for status indicators | Use `[x]`, `[!!]`, `[OK]` -- always 1 cell per character |
| Eyeballing column widths | Compute from grid constants. Count characters. |
| Mixing Unicode box-drawing (`┌─┐`) with ASCII (`+--+`) | Pick one. ASCII `+-|` is safest across all environments |
| Lines of different lengths within a card | Pad every line to card width. This is the #1 rendering bug |
| More than 78 characters wide | Wrapping breaks the layout. Redesign or split into rows |
| Putting detailed data in the dashboard | ASCII is for summaries. Link to detail elsewhere |

## Cross-References

- `visual-vocabulary` -- select chart types before rendering. ASCII supports: bar, KPI, sparkline, table.
- `storytelling-requirements` -- the brief determines whether ASCII is the right delivery target.
- `delivery-svg-markdown` -- upgrade path when ASCII isn't enough (richer visuals, color, branding).
- `delivery-html-dashboard` -- upgrade path when interactivity is needed.
