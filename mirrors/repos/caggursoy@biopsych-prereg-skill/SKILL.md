# Biopsychology Preregistration Assistant

## Description

This skill automatically analyzes a research project directory and generates a preregistration document based on the files and information it finds. It intelligently detects the research modality (EEG, fMRI, online behavioral, psychophysiology) and creates an appropriate preregistration template, filling in what it can discover and leaving blanks for user input.

## Objective

Generate a comprehensive, modality-appropriate preregistration document by:
1. Analyzing the project directory structure and files
2. Detecting the research modality/modalities
3. Extracting relevant information from existing files (scripts, data, documentation)
4. Creating a preregistration draft with discovered information
5. Identifying missing information and prompting the user interactively

## Workflow

### Step 1: Scan Directory
When invoked, immediately scan the current directory:
- List all files and subdirectories
- Identify file types and extensions
- Detect research modality indicators
- Find documentation and scripts

### Step 2: Detect Modality
Based on file patterns, determine research type:
- **EEG/ERP**: .set, .fdt, .vhdr, EEGLAB/MNE scripts
- **fMRI**: .nii, .nii.gz, BIDS structure, SPM/FSL scripts
- **Online**: .html, .js, jsPsych/Qualtrics files
- **Psychophys**: .acq, ECG/EDA/HRV data files

### Step 3: Extract Information
Read relevant files to extract:
- Study title and description
- Sample size and power analysis
- Experimental design
- Analysis parameters
- Software versions
- Hypotheses (from documentation)

### Step 4: Generate Draft
Create preregistration with:
- **Filled sections**: Information found in files
- **[TO BE COMPLETED]**: Missing required information
- **[VERIFY: value]**: Uncertain detections needing confirmation

### Step 5: Interactive Completion
Ask user to:
- Confirm detected information
- Fill in missing sections
- Clarify ambiguous findings
- Review and approve final document

## Usage

Invoke with:
- `/preregister`
- "Create a preregistration"
- "Generate prereg from my project"

## Detection Patterns

### EEG/ERP
- Extensions: `.set`, `.fdt`, `.vhdr`, `.eeg`, `.bdf`
- Scripts: EEGLAB, MNE, FieldTrip
- Keywords: "electrode", "ERP", "ICA"

### fMRI
- Extensions: `.nii`, `.nii.gz`
- Structure: BIDS format
- Scripts: SPM, FSL, fMRIPrep
- Keywords: "BOLD", "TR", "GLM"

### Online Behavioral
- Extensions: `.html`, `.js`, `.json`
- Frameworks: jsPsych, Qualtrics, Pavlovia
- Keywords: "MTurk", "Prolific"

### Psychophysiology
- Extensions: `.acq`, `.mat`
- Software: AcqKnowledge, Kubios
- Keywords: "ECG", "HRV", "EDA"

## Output Format

Generate Markdown document with structure:
```markdown
# Preregistration: [Study Title]

## Metadata
- Title: [detected or TO BE COMPLETED]
- Authors: [TO BE COMPLETED]
- Date: [current date]
- Modality: [detected modality]

## Study Information
[Filled from README or TO BE COMPLETED]

## [Modality-Specific Sections]
[Based on detected modality template]

## Analysis Plan
[Extracted from scripts or TO BE COMPLETED]
```

## Behavior Rules

1. **Always scan directory first** before asking questions
2. **Mark confidence levels** for detected information
3. **Never modify** existing project files
4. **Ask one section at a time** to avoid overwhelming user
5. **Provide examples** when requesting user input
6. **Reference templates** from templates/ directory
7. **Save draft** as `PREREGISTRATION_DRAFT.md` in current directory

## Example Interaction

```
User: Create a preregistration
