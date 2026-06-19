# fMRI Preregistration Skill

## Description

Analyzes fMRI research projects and generates comprehensive preregistration documents. Detects fMRI acquisition parameters, preprocessing pipeline, and statistical analysis plan from BIDS structure and scripts.

## Objective

Generate modality-appropriate fMRI preregistration by:
1. Confirming fMRI modality
2. Extracting acquisition parameters from BIDS metadata and data files
3. Detecting preprocessing pipeline (SPM, FSL, fMRIPrep)
4. Extracting statistical analysis plan (GLM, contrasts)
5. Creating preregistration draft using fMRI template
6. Guiding user through missing sections

## Workflow

### Step 1: Confirm Modality
Verify fMRI detection:
- Display files found: .nii, .nii.gz files
- Check for BIDS structure: `sub-*/func/*.nii.gz`
- Confirm with user: "I detected fMRI files (BIDS format). Proceed?"

### Step 2: Extract fMRI Parameters

**From BIDS structure:**
- `sub-*/func/*_bold.nii.gz` → Functional images
- `sub-*/anat/*_T1w.nii.gz` → Structural images
- `sub-*/func/*_bold.json` → Acquisition parameters (TR, TE, FA, voxel size)

**From JSON sidecars (automatic BIDS extraction):**
```json
{
  "EchoTime": 0.030,
  "RepetitionTime": 2.0,
  "FlipAngle": 90,
  "VoxelSize": [3, 3, 3],
  "NumberOfVolumesDiscardedAtBeginning": 5,
  "MagneticFieldStrength": 3.0
}
```

**From preprocessing scripts (SPM, FSL, fMRIPrep):**
- `spm_preproc.m` → SPM12 parameters
- `feat design.fsf` → FSL settings
- `fmriprep` command → fMRIPrep configuration
- `flirt`, `fnirt` commands → Registration parameters

**From analysis scripts (.m, .py, .R):**
- SPM.stats.fmri_spec → GLM design
- SPM.stats.fmri_est → Estimation method
- Contrast definitions → Statistical contrasts
- `glm`, `lm`, `lmer` in Python/R → Model specification

### Step 3: Detect Preprocessing Pipeline

Search for software indicators:
```
SPM detected: grep for "spm", "spm12", "spm_preproc"
FSL detected: grep for "flirt", "fnirt", "feat", "fslmaths"
fMRIPrep detected: grep for "fmriprep", "bids"
Custom pipeline: grep for preprocessing steps
```

Extract parameters:
- **Realignment/Motion correction**: detected motion parameters
- **Normalization**: standard space (MNI152 2mm, etc.)
- **Smoothing**: kernel size (e.g., 6mm FWHM)
- **Registration**: linear vs. nonlinear

### Step 4: Extract Statistical Analysis Plan

**From GLM design:**
- Regressors: main effects and conditions
- Covariates: motion parameters, confounds
- Contrasts: specific comparisons (e.g., task > rest)
- Duration of effects: stick/parametric/time-expanded

**From statistical scripts:**
- Test type: univariate GLM, multivariate, ROI analysis
- Multiple comparisons correction: cluster extent, FWE, FDR
- Thresholds: p-values, k-values (minimum cluster size)
- Exclusion criteria: motion (FD), DVARS thresholds

### Step 5: Generate Draft

Create `PREREGISTRATION_DRAFT.md` with:
- **Metadata** (from METADATA_SCHEMA.md)
- **Study Information** (title, hypotheses, design)
- **fMRI Acquisition** (extracted from BIDS)
- **Participant Information** (N, criteria)
- **Data Acquisition** (sequence parameters)
- **Preprocessing** (detected pipeline + parameters)
- **Statistical Analysis** (GLM, contrasts, thresholds)
- **Ethics** (from ETHICS_PRIVACY_TEMPLATE.md)

### Step 6: Interactive Completion

Guide user through sections:
1. Verify BIDS structure and acquisition parameters
2. Confirm preprocessing pipeline and parameters
3. Detail statistical analysis plan and contrasts
4. Specify ROIs if relevant
5. Define thresholds and multiple comparisons correction
6. Complete missing sections

## Detection Patterns

### File Extensions & Structure
- `.nii` - Uncompressed NIfTI image
- `.nii.gz` - Compressed NIfTI image (standard)
- `.json` - BIDS metadata sidecar
- BIDS structure: `sub-*/func/sub-*_task-*_bold.nii.gz`

### Software Keywords
- SPM: `spm`, `spm12`, `spm_preproc`, `matlabbatch`
- FSL: `flirt`, `fnirt`, `feat`, `fslmaths`, `feat_model`
- fMRIPrep: `fmriprep`, `bids`, `bold_std`
- Analysis: `GLM`, `contrast`, `beta`, `design matrix`

### BIDS Compliance
- Must have: `sub-*/func/*_bold.nii.gz` and `*_bold.json`
- Recommended: `sub-*/anat/*_T1w.nii.gz`
- Check: file naming follows BIDS standard

## Output Format

```markdown
# Preregistration: [Study Title]

## Metadata
[From METADATA_SCHEMA.md - all fields required]

## Study Information
- Research question: [extracted or TO BE COMPLETED]
- Hypotheses: [extracted or TO BE COMPLETED]
- Design: [extracted]

## Participants
- N: [extracted from sub-* directories or TO BE COMPLETED]
- Inclusion/exclusion: [TO BE COMPLETED]
- Compensation: [TO BE COMPLETED]

## fMRI Acquisition
- Scanner: [VERIFY: detected field strength]
- Sequence: [extracted from JSON: T2*-weighted, BOLD]
- TR: [VERIFY: extracted value]
- TE: [VERIFY: extracted value]
- Flip angle: [VERIFY: extracted value]
- Voxel size: [extracted from NIfTI header]
- Number of volumes: [extracted]
- Multiband factor: [extracted if present]

## Task Design
- Task name: [TO BE COMPLETED]
- Stimuli: [TO BE COMPLETED]
- Trial duration: [TO BE COMPLETED]
- Timing: [TO BE COMPLETED]

## Preprocessing Pipeline
- Software: [detected: SPM/FSL/fMRIPrep]
- Realignment: [extracted parameters]
- Normalization: [standard space detected]
- Smoothing kernel: [extracted if present]

## Statistical Analysis
- GLM design: [extracted from scripts]
- Contrasts: [extracted or TO BE COMPLETED]
- Statistical test: [univariate GLM or TO BE COMPLETED]
- Multiple comparisons: [extracted thresholds]
- ROIs: [TO BE COMPLETED if applicable]

## Ethics & Data Management
[From ETHICS_PRIVACY_TEMPLATE.md]
```

## Behavior Rules

1. **Always check BIDS structure** before other detection
2. **Extract from JSON sidecars** for acquisition parameters
3. **Mark confidence levels** for each detection
4. **Never modify** BIDS data
5. **Ask focused questions** - one section at a time
6. **Provide examples** for user input fields
7. **Save as** `PREREGISTRATION_DRAFT.md` in project root

## Example Interaction

```
User: Create a preregistration

Agent:
1. Scans directory
2. Finds: sub-01, sub-02, ... BIDS structure
3. ✓ Detects: fMRI (confidence: high)
4. Reads BIDS JSON:
   - TR: 2.0s, TE: 0.030s, FA: 90°
   - Voxel size: 3×3×3 mm
5. Scans scripts:
   - Finds: SPM12 preprocessing
   - Finds: 6mm Gaussian smoothing
   - Finds: GLM with main effects
6. Generates draft with:
   - ✓ Acquisition parameters (from JSON)
   - ~ Preprocessing: SPM12, 6mm smoothing
   - ? Contrasts: [TO BE COMPLETED]
7. Asks:
   - "Confirm preprocessing parameters?"
   - "Define contrasts of interest"
   - "What are your statistical thresholds?"
8. Saves: PREREGISTRATION_DRAFT.md
```

## Configuration

Load from `configs/fmri-config.json`:
```json
{
  "modality": "fmri",
  "template": "templates/fmri/FMRI_PREREGISTRATION_GUIDE.md",
  "search_patterns": {
    "software": ["spm", "fsl", "fmriprep"],
    "parameters": ["flirt", "fnirt", "spm_preproc", "feat"],
    "keywords": ["BOLD", "TR", "TE", "GLM", "contrast"]
  },
  "required_sections": [
    "Metadata",
    "Study Information",
    "Participants",
    "fMRI Acquisition",
    "Task Design",
    "Preprocessing Pipeline",
    "Statistical Analysis",
    "Ethics"
  ]
}
```

## Related Resources

- Template: `templates/fmri/FMRI_PREREGISTRATION_GUIDE.md`
- Common metadata: `templates/biopsych/common/METADATA_SCHEMA.md`
- Ethics template: `templates/biopsych/common/ETHICS_PRIVACY_TEMPLATE.md`
- BIDS specification: https://bids-standard.github.io/
- References: See README.md "fMRI Templates" section

## Key References

1. Beyer et al. (2021). A fMRI pre-registration template. PsychArchives.
2. OSF fMRI Preregistration Template
3. Gau et al. (2020). Brain Imaging Data Structure (BIDS)
