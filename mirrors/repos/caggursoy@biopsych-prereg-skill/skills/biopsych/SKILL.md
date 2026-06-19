# Biopsychology Preregistration Base Skill

## Description

Base skill for analyzing biopsychology research projects and generating preregistration documents. Routes to modality-specific skills based on detected research type.

## Objective

Intelligently detect biopsychology research modality and delegate to appropriate modality-specific preregistration skill.

## Workflow

### Step 1: Initial Scan
Scan project directory for characteristic files:
- **EEG/ERP indicators**: `.set`, `.fdt`, `.vhdr`, `.eeg`, `.bdf`, EEGLAB scripts, MNE, FieldTrip
- **fMRI indicators**: `.nii`, `.nii.gz`, `sub-*/` BIDS structure, SPM, FSL, fMRIPrep
- **Online behavioral**: `.html`, `.js`, `.json`, jsPsych, Qualtrics, Pavlovia, Prolific
- **Psychophysiology**: `.acq`, `.edf`, `.ibi`, `.rr`, AcqKnowledge, Kubios, Ledalab, NeuroKit2, ECG/EDA/HRV/EMG keywords

### Step 2: Modality Detection
Determine primary research modality from file patterns:
- Count file type matches per modality
- Check for BIDS structure (indicates neuroimaging)
- Search scripts for software keywords
- Check README/documentation keywords

If multiple modalities detected, ask user which is primary.

### Step 3: Route to Modality Skill
Delegate to appropriate skill:
- EEG/ERP → `skills/eeg/SKILL.md`
- fMRI → `skills/fmri/SKILL.md`
- Online → `skills/online/SKILL.md`
- Psychophysiology → `skills/psychophys/SKILL.md`

## Detection Logic

```
Scan directory recursively for:
  - File extensions matching modality patterns
  - Script content (grep for software names, parameters)
  - BIDS-compliant structure (sub-XXX folders)
  - Documentation keywords
  
Scoring:
  eeg_score = count(.set, .vhdr, .eeg) + keywords("electrode", "ICA", "ERP")
  fmri_score = count(.nii, .nii.gz) + keywords("BOLD", "TR", "fMRI")
  online_score = count(.html, .js) + keywords("jsPsych", "Qualtrics")
  psychophys_score = count(.acq) + keywords("ECG", "EDA", "HRV")
  
Modality = highest_score
Confidence = winner_score / total_score
```

## Input Detection

**From directory structure:**
- Project organization patterns
- Data folder naming
- Script locations

**From files:**
- Study title (README.md, protocol.txt)
- Sample size (power analysis scripts, N reported in docs)
- Design info (experimental paradigm descriptions)

## Output Format

Route to modality skill with detected information:
```
Detected Modality: [modality]
Confidence: [high/medium/low]
Key files found: [list]
Extracted info: [title, N estimate, design]
```

## Behavior Rules

1. **Always scan before deciding** - don't assume from project name
2. **Show detection confidence** - explain reasoning to user
3. **Allow manual override** - let user specify modality if detection wrong
4. **Preserve files** - never modify existing project data
5. **Provide fallback** - ask modality if detection ambiguous

## Example Interactions

```
User: Create a preregistration

Agent:
1. Scans project directory
2. Finds: 3 .set files, EEGLAB scripts, "electrode" mentions
3. Detects: EEG/ERP (confidence: high)
4. Routes to: skills/eeg/SKILL.md
5. Skill continues with EEG-specific extraction and template
```

```
User: Create a preregistration

Agent:
1. Scans project directory
2. Finds: 2 .nii.gz files, SPM scripts, BIDS structure (sub-01, sub-02)
3. Detects: fMRI (confidence: high)
4. Routes to: skills/fmri/SKILL.md
5. Skill continues with fMRI-specific extraction and template
```

```
User: Create a preregistration

Agent:
1. Scans project directory
2. Finds: Equal files for EEG and online (.js, .html, .set)
3. Ambiguous detection (medium confidence)
4. Asks: "I found both EEG and online experiment files. Which is primary?"
5. User: "Online"
6. Routes to: skills/online/SKILL.md
```

## Configuration

Load from `configs/biopsych-config.json`:
```json
{
  "modalities": ["eeg", "fmri", "online", "psychophys"],
  "confidence_threshold": 0.6,
  "scan_depth": 3,
  "file_patterns": {
    "eeg": [".set", ".vhdr", ".eeg", ".bdf"],
    "fmri": [".nii", ".nii.gz"],
    "online": [".html", ".js", ".json"],
    "psychophys": [".acq", ".edf", ".ibi", ".rr"]
  }
}
```

## Related Skills

- `skills/eeg/SKILL.md` - EEG/ERP preregistration
- `skills/fmri/SKILL.md` - fMRI preregistration
- `skills/online/SKILL.md` - Online behavioral preregistration
- `skills/psychophys/SKILL.md` - Psychophysiology preregistration

## Templates

All templates in `templates/` directory:
- `templates/biopsych/common/METADATA_SCHEMA.md` - Required for all
- `templates/biopsych/common/ETHICS_PRIVACY_TEMPLATE.md` - Required for all
- Modality-specific templates (routed by skill)
