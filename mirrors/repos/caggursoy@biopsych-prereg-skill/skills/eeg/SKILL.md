# EEG/ERP Preregistration Skill

## Description

Analyzes EEG/ERP research projects and generates comprehensive preregistration documents following community standards. Detects EEG system details, preprocessing parameters, and analysis plan from existing files.

## Objective

Generate modality-appropriate EEG/ERP preregistration by:
1. Confirming EEG/ERP modality
2. Extracting EEG acquisition parameters from scripts and documentation
3. Detecting preprocessing pipeline decisions
4. Extracting statistical analysis plan
5. Creating preregistration draft using EEG template
6. Guiding user through missing sections

## Workflow

### Step 1: Confirm Modality
Verify EEG/ERP detection:
- Display files found: .set, .vhdr, .fdt files
- Confirm with user: "I detected EEG/ERP files. Proceed?"

### Step 2: Extract EEG Parameters

**From EEGLAB script analysis (.m, .py):**
- `pop_loadset()` → Identify input data format
- `pop_chanedit()` → Reference electrode, ground electrode
- `pop_resample()` → Sampling rate changes
- `pop_eegfilter()` → Online/offline filters (high-pass, low-pass, notch)
- `pop_runica()` → ICA components
- `pop_selectdata()` → Trial/epoch extraction
- `eeglab_topoplot`, `figure` commands → Known electrode montage

**From MNE Python (.py files):**
- `raw.load_data()` → Data organization
- `raw.set_eeg_reference()` → Reference electrode
- `raw.filter()` → Filter parameters
- `epochs = Epochs()` → Epoch timing (tmin, tmax)
- `ica = ICA()` → ICA parameters
- `raw.get_montage()` → Electrode montage

**From documentation:**
- README: study design, hypothesis
- Protocol files: participant criteria, task description
- Data dictionaries: channel naming, sampling rates

### Step 3: Detect Preprocessing Pipeline

Search scripts for patterns:
```
artifact_detection = grep(script, "reject_", "threshold", "badchans")
ica_components = grep(script, "n_components", "ica_fit", "exclude")
baseline_correction = grep(script, "baseline", "bl_range", "mode")
downsampling = grep(script, "resample", "decim")
```

Mark confidence for each parameter.

### Step 4: Extract Analysis Plan

**From statistical analysis scripts:**
- Electrode selection (ROI or mass-univariate)
- Time windows (e.g., 100-300ms for P300)
- Statistical tests (ANOVA, t-test, linear mixed effects)
- Multiple comparisons correction (cluster, FDR, Bonferroni)
- Effect size reporting

**Keywords to search:**
- `erp`, `component`, `latency`, `amplitude`
- `stat.f_oneway`, `ttest_ind`, `lmm`, `lmer`
- `cluster`, `p.adjust`, `mne.stats`

### Step 5: Generate Draft

Create `PREREGISTRATION_DRAFT.md` with:
- **Metadata** (from METADATA_SCHEMA.md)
- **Study Information** (title, hypotheses, design)
- **EEG Acquisition** (filled from scripts + [VERIFY:])
- **Preprocessing** (filled from scripts + [TO BE COMPLETED])
- **Statistical Analysis** (filled from scripts + [TO BE COMPLETED])
- **Ethics** (from ETHICS_PRIVACY_TEMPLATE.md)

### Step 6: Interactive Completion

Guide user through sections:
1. Confirm detected EEG parameters
2. Specify preprocessing decisions not found in scripts
3. Detail statistical analysis plan
4. Complete missing sections
5. Review final document

## Detection Patterns

### File Extensions
- `.set` - EEGLAB dataset
- `.vhdr` - BrainVision header (Neuroscan)
- `.fdt` - EEGLAB data file
- `.eeg` - Generic EEG
- `.bdf` - BioSemi format

### Script Keywords (EEGLAB/MNE)
- `eeglab`, `pop_loadset`, `pop_eegfilter`
- `mne`, `raw.filter`, `Epochs`, `ICA`
- `fieldtrip`, `ft_preprocessing`, `ft_timelockanalysis`
- `electrode`, `montage`, `reference`, `ICA`, `ERP`, `component`

### Documentation Keywords
- `electrode montage`, `impedance`, `artifact`, `preprocessing`
- `sampling rate`, `filter`, `high-pass`, `low-pass`
- `ICA`, `component`, `rejection criteria`

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
- N: [extracted or TO BE COMPLETED]
- Inclusion/exclusion: [TO BE COMPLETED]
- Compensation: [TO BE COMPLETED]

## EEG Acquisition
- System: [detected from scripts: EEGLAB/BrainVision/etc.]
- Electrodes: [montage if detected]
- Sampling rate: [VERIFY: detected value]
- Reference: [VERIFY: detected electrode]
- Ground: [TO BE COMPLETED]
- Online filters: [extracted from preprocessing script]

## Experimental Paradigm
- Task: [TO BE COMPLETED]
- Stimuli: [TO BE COMPLETED]
- Trial structure: [TO BE COMPLETED]

## Preprocessing Plan
- Artifact removal: [extracted from script]
- ICA: [extracted parameters if present]
- Re-referencing: [VERIFY: detected value]
- Baseline correction: [extracted or TO BE COMPLETED]
- Downsampling: [extracted if present]

## Analysis Plan
- ERP components: [TO BE COMPLETED]
- Time windows: [extracted if specified]
- Electrodes: [extracted if specified]
- Statistical tests: [extracted from analysis script]
- Multiple comparisons: [extracted if present]

## Ethics & Data Management
[From ETHICS_PRIVACY_TEMPLATE.md]
```

## Behavior Rules

1. **Always scan script files** before asking about parameters
2. **Mark confidence levels** for each detection:
   - ✓ High (direct in script, >2 mentions)
   - ~ Medium (inferred from patterns)
   - ? Low (guess, needs verification)
3. **Never modify** project files
4. **Ask focused questions** - one section at a time
5. **Provide examples** for user input fields
6. **Save as** `PREREGISTRATION_DRAFT.md` in project root

## Example Interaction

```
User: Create a preregistration

Agent:
1. ✓ Confirms: "I found .set files. Continuing with EEG/ERP..."
2. Scans scripts:
   - Finds: pop_eegfilter(EEG, 0.5, 40) → 0.5-40 Hz
   - Finds: pop_chanedit(EEG, 'ref', 'FCz') → Reference: FCz
   - Finds: erp_times = [100 300] → Time window: 100-300ms
3. Extracts: "Sampling rate 500 Hz, EEGLAB dataset format"
4. Generates draft with:
   - ✓ EEG system: EEGLAB
   - ✓ Filters: 0.5-40 Hz
   - ~ Reference: FCz (verify)
   - ? Components detected: [TO BE COMPLETED]
5. Asks:
   - "Confirm reference as FCz?"
   - "What components are you analyzing?"
   - "Define artifact rejection thresholds"
6. Saves: PREREGISTRATION_DRAFT.md
```

## Configuration

Load from `configs/eeg-config.json`:
```json
{
  "modality": "eeg",
  "template": "templates/eeg/EEG_ERP_PREREGISTRATION_GUIDE.md",
  "search_patterns": {
    "software": ["eeglab", "mne", "fieldtrip"],
    "parameters": ["pop_eegfilter", "raw.filter", "Epochs"],
    "keywords": ["electrode", "component", "ICA", "ERP"]
  },
  "required_sections": [
    "Metadata",
    "Study Information",
    "Participants",
    "EEG Acquisition",
    "Experimental Paradigm",
    "Preprocessing Plan",
    "Analysis Plan",
    "Ethics"
  ]
}
```

## Related Resources

- Template: `templates/eeg/EEG_ERP_PREREGISTRATION_GUIDE.md`
- Common metadata: `templates/biopsych/common/METADATA_SCHEMA.md`
- Ethics template: `templates/biopsych/common/ETHICS_PRIVACY_TEMPLATE.md`
- References: See README.md "EEG/ERP Templates" section

## Key References

1. Govaart et al. (2025). EEG ERP Preregistration Template. MetaArXiv. https://doi.org/10.31222/osf.io/4nvpt
2. Pernet et al. (2020). Issues and recommendations from the OHBM COBIDAS MEEG committee for reproducible EEG and MEG research. Nature Neuroscience, 24, 1473-1474. https://doi.org/10.1038/s41593-020-00710-7
3. Paul et al. (2021). Making ERP Research More Transparent. International Journal of Psychophysiology.
