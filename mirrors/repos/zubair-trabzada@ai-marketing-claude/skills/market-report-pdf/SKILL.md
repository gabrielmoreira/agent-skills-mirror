# PDF Marketing Report Generator

## Skill Purpose
Generate a professional, visually polished PDF marketing report using the Python script `scripts/generate_pdf_report.py`. This skill collects all available audit and analysis data, structures it into the expected JSON format, invokes the script, and produces a branded PDF with score gauges, bar charts, comparison tables, findings, and a prioritized action plan.

## When to Use
- User wants a PDF version of the marketing report (not just Markdown)
- User is preparing a deliverable for a client presentation
- User asks for a "polished report", "client-ready report", or "PDF report"
- User wants a visual report with charts and scores
- Triggered by `/market report-pdf` or `/market report-pdf <domain>`

## When to Use PDF vs Markdown

| Format | Best For | Pros | Cons |
|---|---|---|---|
| **PDF** | Client presentations, email attachments, sales collateral | Professional appearance, consistent formatting, visual charts, printable | Harder to edit, requires Python script |
| **Markdown** | Internal use, quick reference, iterative editing, version control | Easy to edit, readable in any editor, git-friendly | Less visually polished, no charts |

**Rule of thumb:** If the report is going to a client or prospect, use PDF. If it is for internal use or further editing, use Markdown.

## How to Execute

### Step 1: Collect All Available Data
Gather data from all previous skill runs. Check for these files in the project directory:

**Primary data sources:**
- `MARKETING-AUDIT.md` -- Overall audit results
- `LANDING-CRO.md` -- Landing page conversion analysis
- `SEO-AUDIT.md` -- SEO findings
- `BRAND-VOICE.md` -- Brand voice analysis
- `COMPETITOR-ANALYSIS.md` -- Competitor comparison data
- `FUNNEL-ANALYSIS.md` -- Funnel analysis
- `SOCIAL-AUDIT.md` -- Social media audit
- `EMAIL-AUDIT.md` -- Email marketing audit
- `AD-AUDIT.md` -- Advertising audit

**If no previous data exists:**
1. Recommend the user run `/market audit <url>` first for the best results
2. If the user insists on generating a report without prior audits, analyze the provided URL directly and build the data structure from scratch
3. Use the analyze_page.py script to gather automated data: `python scripts/analyze_page.py <url>`

### Step 2: Build the JSON Data Structure
The `scripts/generate_pdf_report.py` script expects a JSON file as input with this exact structure:

```json
{
  "url": "https://example.com",
  "date": "March 1, 2026",
  "brand_name": "Example Co",
  "overall_score": 62,
  "executive_summary": "A 2-4 sentence summary of the overall marketing health, key opportunities, and estimated revenue impact of implementing recommendations.",
  "categories": {
    "Content & Messaging": {
      "score": 68,
      "weight": "25%"
    },
    "Conversion Optimization": {
      "score": 52,
      "weight": "20%"
    },
    "SEO & Discoverability": {
      "score": 74,
      "weight": "20%"
    },
    "Competitive Positioning": {
      "score": 48,
      "weight": "15%"
    },
    "Brand & Trust": {
      "score": 70,
      "weight": "10%"
    },
    "Growth & Strategy": {
      "score": 55,
      "weight": "10%"
    }
  },
  "findings": [
    {
      "severity": "Critical",
      "finding": "Description of the most important finding"
    },
    {
      "severity": "High",
      "finding": "Description of a high-priority finding"
    },
    {
      "severity": "Medium",
      "finding": "Description of a medium-priority finding"
    },
    {
      "severity": "Low",
      "finding": "Description of a lower-priority finding"
    }
  ],
  "quick_wins": [
    "First quick win action item",
    "Second quick win action item",
    "Third quick win action item"
  ],
  "medium_term": [
    "First medium-term action item",
    "Second medium-term action item",
    "Third medium-term action item"
  ],
  "strategic": [
    "First strategic action item",
    "Second strategic action item",
    "Third strategic action item"
  ],
  "competitors": [
    {
      "name": "Competitor A",
      "positioning": "Their market position",
      "pricing": "Their pricing model",
      "social_proof": "Their trust signals",
      "content": "Their content approach"
    },
    {
      "name": "Competitor B",
      "positioning": "Their market position",
      "pricing": "Their pricing model",
      "social_proof": "Their trust signals",
      "content": "Their content approach"
    }
  ]
}
```

### Step 3: Field-by-Field Data Assembly Guide

#### `url` (string, required)
The target website URL. Use the full URL including protocol.

#### `date` (string, required)
The report generation date. Format: "Month DD, YYYY" (e.g., "March 1, 2026").

#### `brand_name` (string, required)
The company or brand name. Used in competitor comparison table headers.

#### `overall_score` (integer, 0-100, required)
The weighted average of all category scores. Calculate as:
```
overall_score = (content * 0.25) + (conversion * 0.20) + (seo * 0.20) + (competitive * 0.15) + (brand * 0.10) + (growth * 0.10)
```

#### `executive_summary` (string, required)
A 2-4 sentence summary covering:
- Current marketing health assessment
- Top 1-2 most impactful findings
- Estimated revenue impact of implementing recommendations
- Recommended first step

Keep it concise and impactful. This appears on the cover page right below the score gauge.

#### `categories` (object, required)
Exactly 6 categories with their scores. The categories map to these evaluation areas:

| Category | What It Measures | Scoring Guidance |
|---|---|---|
| Content & Messaging | Copy quality, value proposition, headline clarity, CTA text, brand voice consistency | 80+: Clear, benefit-driven, specific. 60-79: Adequate but generic. <60: Vague, feature-focused, unclear |
| Conversion Optimization | Social proof, form design, CTA placement, objection handling, urgency | 80+: Multiple proof types, optimized forms, clear CTAs. 60-79: Some elements present. <60: Missing critical elements |
| SEO & Discoverability | Title tags, meta descriptions, headers, schema, internal linking, page speed | 80+: Fully optimized. 60-79: Mostly present with gaps. <60: Major issues or missing elements |
| Competitive Positioning | Differentiation, pricing clarity, comparison content, market awareness | 80+: Clear positioning, comparison pages exist. 60-79: Some differentiation. <60: No clear positioning |
| Brand & Trust | Design quality, trust badges, security indicators, professional appearance | 80+: Modern design, trust signals throughout. 60-79: Adequate design. <60: Outdated or unprofessional |
| Growth & Strategy | Lead capture, email marketing, content strategy, acquisition channels | 80+: Multi-channel strategy in place. 60-79: Some channels active. <60: No clear growth strategy |

#### `findings` (array, required)
An array of finding objects, each with `severity` and `finding` fields.

**Severity levels:**
- `Critical` -- Directly losing revenue or customers. Fix immediately.
- `High` -- Significant impact on growth. Fix within 1-2 weeks.
- `Medium` -- Meaningful improvement opportunity. Fix within 1 month.
- `Low` -- Nice-to-have improvement. Fix when time allows.

**Writing effective findings:**
- Be specific: "Homepage headline says 'Welcome to Our Platform'" not "Headline needs improvement"
- Quantify impact: "Missing meta descriptions on 8 of 12 landing pages"
- Reference benchmarks: "Page load time is 4.2s (benchmark: under 2s)"
- Include evidence: "No testimonials found on homepage, pricing page, or signup page"

Aim for 5-10 findings. Order from most to least severe.

#### `quick_wins` (array, required)
3-5 action items that can be implemented within one week with minimal effort. Each should be a specific, actionable instruction.

**Good quick win:** "Rewrite the homepage headline from 'Welcome to Our Platform' to 'Cut Your Reporting Time by 75% -- Automated Analytics for Growth Teams'"

**Bad quick win:** "Improve the headline" (too vague)

#### `medium_term` (array, required)
3-5 action items requiring 1-3 months to implement. These are more involved but have high impact.

#### `strategic` (array, required)
3-5 action items requiring 3-6 months. These are foundational changes that require planning and sustained effort.

#### `competitors` (array, optional)
Up to 3 competitor objects for the comparison table. If no competitor data is available, omit this field -- the script will skip the competitor section.

### Step 4: Write the JSON File
Save the assembled data as a temporary JSON file:

```bash
# Write the JSON data to a temporary file
cat > /tmp/report_data.json << 'JSONEOF'
{
  ... assembled JSON data ...
}
JSONEOF
```

### Step 5: Invoke the PDF Generator Script

**Prerequisites check:**
First, verify that `reportlab` is installed:
```bash
python3 -c "import reportlab" 2>/dev/null || pip3 install reportlab
```

**Generate the report:**
```bash
python3 scripts/generate_pdf_report.py /tmp/report_data.json "MARKETING-REPORT-<domain>.pdf"
```

Replace `<domain>` with the target website's domain name (without protocol or www), using hyphens instead of dots. For example:
- `example.com` becomes `MARKETING-REPORT-example-com.pdf`
- `myapp.io` becomes `MARKETING-REPORT-myapp-io.pdf`

**Demo mode (no arguments):**
Running the script without arguments generates a sample report with placeholder data:
```bash
python3 scripts/generate_pdf_report.py
# Creates: MARKETING-REPORT-sample.pdf
```

### Step 6: Verify the Output
After generation, verify the PDF was created:
```bash
ls -la "MARKETING-REPORT-<domain>.pdf"
```

Report the file path and size to the user.

### Step 7: Clean Up
Remove the temporary JSON file:
```bash
rm /tmp/report_data.json
```

## PDF Report Contents

The generated PDF includes the following pages:

### Page 1: Cover Page
- Report title: "Marketing Audit Report"
- Target URL
- Generation date
- Overall score gauge (circular visualization with color coding)
- Grade letter (A+ through F)
- Executive summary paragraph

### Page 2: Score Breakdown
- Horizontal bar chart showing all 6 category scores with color coding
- Score table with category names, scores, weights, and status labels
- Color coding: Green (80+), Blue (60-79), Yellow (40-59), Red (<40)

### Page 3: Key Findings
- Findings table with severity labels and descriptions
- Color-coded severity indicators (Critical = red, High = orange, Medium = yellow, Low = blue)
- Findings ordered from most to least severe

### Page 4: Prioritized Action Plan
- Quick Wins section (This Week)
- Medium-Term section (1-3 Months)
- Strategic section (3-6 Months)
- Numbered action items in each tier

### Page 5: Competitive Landscape (if competitor data provided)
- Comparison table with client vs up to 3 competitors
- Rows: Positioning, Pricing, Social Proof, Content

### Final Page: Methodology
- Scoring methodology explanation
- Category weights and measurement criteria
- Footer: "Generated by AI Marketing Suite for Claude Code"

## Color Scheme

The PDF uses a professional color palette:

| Element | Color | Hex Code |
|---|---|---|
| Primary (headers, titles) | Dark Navy | #1B2A4A |
| Accent (links, highlights) | Blue | #2D5BFF |
| Highlight (attention) | Orange | #FF6B35 |
| Success (high scores) | Green | #00C853 |
| Warning (medium scores) | Amber | #FFB300 |
| Danger (low scores, critical) | Red | #FF1744 |
| Light background | Light Gray | #F5F7FA |
| Body text | Dark Gray | #2C3E50 |
| Secondary text | Medium Gray | #7F8C9B |
| Borders | Light Border | #E0E6ED |

## Score-to-Color Mapping
- 80-100: Green (#00C853) -- Strong performance
- 60-79: Blue (#2D5BFF) -- Solid with room to improve
- 40-59: Amber (#FFB300) -- Needs attention
- 0-39: Red (#FF1744) -- Critical issues

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'reportlab'` | Run `pip3 install reportlab` |
| Script produces empty PDF | Check that JSON data has all required fields |
| Score gauge not rendering | Ensure `overall_score` is a number 0-100 |
| Competitor table missing | Ensure `competitors` array has objects with `name`, `positioning`, `pricing`, `social_proof`, `content` fields |
| PDF is only 1 page | Check for JSON parsing errors -- run `python3 -c "import json; json.load(open('/tmp/report_data.json'))"` |
| Fonts look wrong | The script uses Helvetica (built into reportlab). No custom fonts needed. |

## Integration with Other Skills

This skill works best when combined with other audit skills. The recommended workflow:

1. Run `/market audit <url>` -- Generates comprehensive audit data
2. Run `/market competitors <url>` -- Adds competitor comparison data
3. Run `/market seo <url>` -- Adds detailed SEO findings
4. Run `/market landing <url>` -- Adds CRO analysis
5. Run `/market report-pdf <url>` -- Compiles everything into a PDF

The PDF report skill will automatically look for output files from these skills and incorporate their data into the report JSON.

## Output
- **File:** `MARKETING-REPORT-<domain>.pdf`
- **Location:** Project root directory
- **Size:** Typically 200KB-500KB depending on content volume
- **Pages:** 5-7 pages depending on whether competitor data and additional sections are included

## Key Principles
- The PDF report is the most client-facing deliverable in the toolkit. Quality matters.
- Always verify the JSON data is complete and accurate before generating. Garbage in, garbage out.
- Use the PDF for initial client impressions and sales conversations. Follow up with the more detailed Markdown report if the client engages.
- Every score should be justifiable. If a client asks "why did I get a 52 in Conversion Optimization?", the findings should provide clear evidence.
- Round scores to whole numbers. Decimals imply false precision.
- Keep the executive summary tight -- 2-4 sentences maximum. Clients skim cover pages.
- If generating for a prospect (not yet a client), the report serves as a sales tool. Make the opportunities compelling and the action plan achievable.
