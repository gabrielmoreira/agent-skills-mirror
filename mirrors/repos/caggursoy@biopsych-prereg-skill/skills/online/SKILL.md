# Online Behavioral Preregistration Skill

## Description

Analyzes online behavioral research projects and generates comprehensive preregistration documents. Detects experiment platform, data quality procedures, and exclusion criteria from experiment code and documentation.

## Objective

Generate modality-appropriate online behavioral preregistration by:
1. Confirming online behavioral modality
2. Detecting platform (jsPsych, Qualtrics, Pavlovia, custom)
3. Extracting participant criteria and data quality thresholds
4. Identifying exclusion rules and attention checks
5. Creating preregistration draft using PRP-QUANT template
6. Guiding user through missing sections

## Workflow

### Step 1: Confirm Modality
Verify online behavioral detection:
- Display files found: .html, .js, .json files
- Identify platform patterns
- Confirm with user: "I detected online behavioral experiment files. Proceed?"

### Step 2: Detect Platform

Search for platform indicators:
```
jsPsych detected: grep for "jsPsych", "jspsych.init", ".js files with experiment logic"
Qualtrics detected: grep for "Qualtrics" API, QID references
Pavlovia detected: grep for "psychojs", "pavlovia"
Prolific detected: grep for "PROLIFIC_PID", "STUDY_ID"
MTurk detected: grep for "turkSubmitTo", "HITId"
Custom detected: experiment logic without standard framework
```

### Step 3: Extract Experiment Parameters

**From jsPsych code (.js, .html):**
```javascript
// Timeline extraction
var trial = {
  type: 'image-button-response',
  stimulus: [images],
  choices: [options],
  trial_duration: [ms]
};

// Detect:
- Trial types
- Number of trials per condition
- Stimulus properties
- Response options
- Trial timing
```

**From Qualtrics survey structure:**
- Question types and branching
- Block structure
- Skip logic
- Timing settings

**From experiment documentation:**
- README: study description, hypothesis
- protocols.txt: procedure steps
- criteria.json: participant inclusion/exclusion

**From data quality configuration:**
- Response time thresholds
- Attention check locations and passing criteria
- Bot detection rules
- Duplicate detection methods

### Step 4: Extract Exclusion Criteria

**Data quality thresholds (from config or scripts):**
- Attention check accuracy (e.g., ≥80%)
- Response time bounds (e.g., 200-5000ms)
- Missing response rate (e.g., <5%)
- DVARS/head motion (if applicable)
- Duplicate detection: same IP, device fingerprint

**Participant criteria (from documentation):**
- Age range
- Language requirements
- Location restrictions
- Device requirements (desktop/mobile)
- Browser requirements

### Step 5: Detect Data Collection Method

Identify recruitment platform:
```
Prolific: "PROLIFIC_PID" in code
MTurk: "HITId", "turkSubmitTo"
Direct links: custom URL distribution
Pavlovia: Pavlovia URL structure
Lab-based online: .localhost, internal URL
```

Track: expected N, compensation, inclusion code handling

### Step 6: Generate Draft

Create `PREREGISTRATION_DRAFT.md` with:
- **Metadata** (from METADATA_SCHEMA.md)
- **Study Information** (title, hypotheses, design)
- **Participants** (N, criteria, recruitment)
- **Experiment Design** (task description, stimuli)
- **Data Quality** (exclusion criteria, attention checks)
- **Analysis Plan** (planned tests, cleaning procedures)
- **Ethics** (from ETHICS_PRIVACY_TEMPLATE.md)

### Step 7: Interactive Completion

Guide user through sections:
1. Verify platform and experiment structure
2. Confirm participant criteria and N
3. Detail data quality procedures
4. Specify exclusion rules
5. Define attention checks
6. Complete analysis plan

## Detection Patterns

### File Extensions & Formats
- `.html` - Web-based experiment
- `.js` - JavaScript experiment code
- `.json` - Configuration files, data structure
- `.py` - Backend code (Flask, Django)
- `.php` - Server-side code

### Platform Keywords
- jsPsych: `jspsych.min.js`, `jsPsych.init`, `.on_finish`
- Qualtrics: `Qualtrics.SurveyEngine`, QID
- Pavlovia: `psychojs`, `PavloviaManager`
- Prolific: `PROLIFIC_PID`, `STUDY_ID`
- MTurk: `turkSubmitTo`, `HITId`, `assignmentId`

### Experiment Keywords
- `stimulus`, `trial`, `condition`, `block`
- `rt`, `reaction_time`, `response_time`
- `choice`, `response`, `accuracy`
- `attention_check`, `quality_check`, `bot_detection`

## Output Format

```markdown
# Preregistration: [Study Title]

## Metadata
[From METADATA_SCHEMA.md - all fields required]

## Study Information
- Research question: [extracted or TO BE COMPLETED]
- Hypotheses: [extracted or TO BE COMPLETED]
- Design: [extracted from code]

## Participants
- Planned N: [extracted estimate or TO BE COMPLETED]
- Inclusion criteria: [extracted or TO BE COMPLETED]
- Exclusion criteria: [detected data quality rules]
- Recruitment platform: [detected: Prolific/MTurk/other]
- Compensation: [TO BE COMPLETED]

## Experiment Design
- Platform: [detected: jsPsych/Qualtrics/Pavlovia]
- Task description: [extracted from code/README]
- Stimuli: [extracted or TO BE COMPLETED]
- Trial structure: [extracted or TO BE COMPLETED]
- Number of trials: [extracted or TO BE COMPLETED]
- Estimated duration: [extracted or TO BE COMPLETED]

## Data Quality Procedures
- Attention checks: [detected number and location]
- Passing criteria: [detected thresholds]
- Response time bounds: [detected if set]
- Bot detection: [TO BE COMPLETED]
- Duplicate detection: [detected methods]
- Other exclusions: [detected rules]

## Analysis Plan
- Data cleaning: [extracted procedures]
- Exclusion rules: [detected thresholds]
- Primary analyses: [TO BE COMPLETED]
- Secondary analyses: [TO BE COMPLETED]

## Ethics & Data Management
[From ETHICS_PRIVACY_TEMPLATE.md]
```

## Behavior Rules

1. **Always scan experiment code** before asking about design
2. **Extract data quality settings** from configuration
3. **Identify recruitment platform** from URLs and tokens
4. **Mark confidence levels** for each detection
5. **Never modify** experiment code without permission
6. **Ask focused questions** - one section at a time
7. **Provide examples** for user input fields
8. **Save as** `PREREGISTRATION_DRAFT.md` in project root

## Example Interaction

```
User: Create a preregistration

Agent:
1. Scans directory
2. Finds: index.html, experiment.js, config.json
3. ✓ Detects: Online behavioral (confidence: high)
4. Analyzes code:
   - Platform: jsPsych (detected "jsPsych.init")
   - Conditions: 3 found in experiment code
   - Trials per condition: 40 (extracted)
   - Attention check: 1 found (location: trial 50)
5. Reads config.json:
   - Response time bounds: 200-5000ms
   - Attention accuracy threshold: ≥80%
   - Recruitment: Prolific (detected PROLIFIC_PID)
6. Generates draft with:
   - ✓ Platform: jsPsych
   - ✓ Trials: 40 per condition
   - ✓ Data quality: attention check, RT bounds
   - ? Hypotheses: [TO BE COMPLETED]
   - ? Primary analysis: [TO BE COMPLETED]
7. Asks:
   - "Confirm trial structure?"
   - "What are your primary hypotheses?"
   - "Define primary statistical tests"
8. Saves: PREREGISTRATION_DRAFT.md
```

## Configuration

Load from `configs/online-config.json`:
```json
{
  "modality": "online",
  "template": "templates/online/ONLINE_BEHAVIORAL_PREREGISTRATION_GUIDE.md",
  "platforms": ["jspsych", "qualtrics", "pavlovia", "custom"],
  "search_patterns": {
    "jspsych": ["jspsych.min.js", "jsPsych.init", ".on_finish"],
    "qualtrics": ["Qualtrics.SurveyEngine", "QID"],
    "recruitment": ["PROLIFIC_PID", "HITId", "turkSubmitTo"]
  },
  "required_sections": [
    "Metadata",
    "Study Information",
    "Participants",
    "Experiment Design",
    "Data Quality Procedures",
    "Analysis Plan",
    "Ethics"
  ]
}
```

## Related Resources

- Template: `templates/online/ONLINE_BEHAVIORAL_PREREGISTRATION_GUIDE.md`
- Common metadata: `templates/biopsych/common/METADATA_SCHEMA.md`
- Ethics template: `templates/biopsych/common/ETHICS_PRIVACY_TEMPLATE.md`
- jsPsych documentation: https://www.jspsych.org/
- References: See README.md "Online Behavioral Templates" section

## Key References

1. PRP-QUANT Template (2020). Preregistration Standards for Psychology.
2. Joint Psychological Societies Preregistration Task Force Report (2022).
3. Bosnjak et al. (2022). Template for preregistration of quantitative research in psychology. American Psychologist.
