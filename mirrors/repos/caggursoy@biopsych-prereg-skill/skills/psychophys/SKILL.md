# Psychophysiology Preregistration Skill

## Description

Analyzes psychophysiology research projects and generates comprehensive preregistration documents. Detects physiological signal acquisition systems, processing parameters, and analysis plans from scripts and documentation.

## Objective

Generate modality-appropriate psychophysiology preregistration by:
1. Confirming psychophysiology modality
2. Extracting acquisition parameters from scripts and data files
3. Detecting signal processing pipeline (artifact detection, decomposition)
4. Extracting statistical analysis plan
5. Creating preregistration draft using psychophysiology template
6. Guiding user through missing sections

## Workflow

### Step 1: Confirm Modality
Verify psychophysiology detection:
- Display files found: .acq, .edf, .mat, .txt files with physiological data
- Identify signal types: ECG, EDA, EMG, respiration, pupillometry
- Confirm with user: "I detected psychophysiology files. Proceed?"

### Step 2: Detect Signal Types and Software

**Software detection:**
```
AcqKnowledge detected: grep for ".acq", "biopac", "AcqKnowledge"
Kubios detected: grep for "kubios", "hrv", "rr_intervals"
Ledalab detected: grep for "ledalab", "eda", "scr"
MATLAB detected: grep for ".mat", "load", "ecg", "eda"
Python detected: grep for "neurokit", "biosppy", "hrv", "eda"
R detected: grep for "RHRV", "physio", "eda.R"
```

**Signal type detection:**
```
ECG/HRV: grep for "ecg", "hrv", "rr", "ibi", "heart_rate", "r_peaks"
EDA/SCR: grep for "eda", "gsr", "scr", "scl", "skin_conductance"
EMG: grep for "emg", "electromyography", "muscle"
Respiration: grep for "resp", "breathing", "respiration_rate"
Pupillometry: grep for "pupil", "eye_tracking", "pupil_diameter"
```

### Step 3: Extract Acquisition Parameters

**From AcqKnowledge files (.acq):**
- Sampling rate from file header
- Channel names and units
- Recording duration
- Hardware configuration

**From Python scripts (NeuroKit2, BioSPPy):**
```python
# ECG/HRV extraction
ecg_signals, info = nk.ecg_process(ecg, sampling_rate=1000)
hrv_time = nk.hrv_time(peaks, sampling_rate=1000)
hrv_freq = nk.hrv_frequency(peaks, sampling_rate=1000)

# EDA extraction
eda_signals, info = nk.eda_process(eda, sampling_rate=100)
scr_peaks = nk.eda_peaks(eda_cleaned)

# Detect:
- Sampling rate
- Signal processing functions
- Analysis parameters
```

**From MATLAB scripts:**
```matlab
% ECG/HRV
[r_peaks, rr_intervals] = detect_r_peaks(ecg, fs);
hrv_metrics = calculate_hrv(rr_intervals);

% EDA
[scr, scl] = decompose_eda(eda_signal, fs);

% Detect:
- Sampling frequency (fs)
- Detection algorithms
- Analysis windows
```

**From R scripts (RHRV, physio):**
```r
# HRV analysis
hrv.data <- LoadBeatRR(file)
hrv.data <- FilterNIHR(hrv.data)
hrv.data <- CalculateTimeAnalysis(hrv.data)

# Detect:
- Data loading methods
- Filtering parameters
- Analysis functions
```

### Step 4: Extract Signal Processing Pipeline

**ECG/HRV Processing:**
- R-peak detection algorithm (Pan-Tompkins, Hamilton, etc.)
- Artifact detection method
- Ectopic beat handling
- RR interval filtering
- Interpolation method
- Detrending

**EDA Processing:**
- Artifact detection and removal
- Decomposition method (high-pass filter, CDA, cvxEDA)
- Baseline correction
- SCR detection criteria (amplitude threshold, rise time)
- Tonic vs. phasic separation

**EMG Processing:**
- Filtering (high-pass, low-pass, notch)
- Rectification method
- Smoothing/envelope extraction
- Baseline correction
- Burst detection criteria

**Respiration Processing:**
- Peak detection
- Rate calculation
- Artifact handling
- Baseline correction

### Step 5: Extract Analysis Plan

**From analysis scripts:**
- Baseline period definition
- Analysis windows (e.g., task vs. rest)
- Dependent variables:
  - HRV: SDNN, RMSSD, pNN50, LF, HF, LF/HF
  - EDA: SCL, SCR amplitude, SCR frequency, AUC
  - EMG: mean amplitude, peak amplitude, integrated EMG
  - Respiration: rate, variability
- Statistical tests (t-test, ANOVA, mixed models)
- Covariates and confounds
- Multiple comparisons correction

**Keywords to search:**
- `baseline`, `task`, `rest`, `condition`
- `ttest`, `anova`, `lm`, `lmer`, `glm`
- `SDNN`, `RMSSD`, `LF`, `HF`, `SCL`, `SCR`
- `mean`, `median`, `peak`, `auc`

### Step 6: Generate Draft

Create `PREREGISTRATION_DRAFT.md` with:
- **Metadata** (from METADATA_SCHEMA.md)
- **Study Information** (title, hypotheses, design)
- **Participants** (N, criteria, exclusions)
- **Psychophysiological Measures** (signal types, acquisition)
- **Signal Processing** (detection algorithms, artifact handling)
- **Analysis Plan** (dependent variables, statistical tests)
- **Ethics** (from ETHICS_PRIVACY_TEMPLATE.md)

### Step 7: Interactive Completion

Guide user through sections:
1. Verify detected signal types and software
2. Confirm acquisition parameters (sampling rate, electrode placement)
3. Detail signal processing decisions
4. Specify analysis windows and dependent variables
5. Define statistical analysis plan
6. Complete missing sections

## Detection Patterns

### File Extensions
- `.acq` - AcqKnowledge/BIOPAC data
- `.edf` - European Data Format (common for physiological signals)
- `.mat` - MATLAB data files
- `.txt`, `.csv` - Text-based physiological data
- `.hea`, `.dat` - PhysioNet WFDB format
- `.ibi`, `.rr` - RR interval files

### Software Keywords
- AcqKnowledge: `acq`, `biopac`, `AcqKnowledge`
- Kubios: `kubios`, `hrv_analysis`, `rr_correction`
- Ledalab: `ledalab`, `analyze`, `optimize`
- NeuroKit2: `nk.ecg_process`, `nk.eda_process`, `nk.hrv`
- BioSPPy: `biosppy.signals`, `ecg.ecg`, `eda.eda`
- RHRV: `LoadBeatRR`, `FilterNIHR`, `CalculateTimeAnalysis`

### Signal Keywords
- ECG/HRV: `ecg`, `hrv`, `r_peak`, `rr_interval`, `ibi`, `heart_rate`, `SDNN`, `RMSSD`, `LF`, `HF`
- EDA: `eda`, `gsr`, `scr`, `scl`, `skin_conductance`, `tonic`, `phasic`
- EMG: `emg`, `muscle`, `rectify`, `envelope`, `burst`
- Respiration: `resp`, `breathing`, `respiration_rate`, `breath`
- Pupillometry: `pupil`, `diameter`, `dilation`, `constriction`

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
- Physiology-specific exclusions: [TO BE COMPLETED]
  - Cardiovascular conditions (for ECG/HRV)
  - Skin conditions (for EDA)
  - Medications affecting autonomic function
- Compensation: [TO BE COMPLETED]

## Psychophysiological Measures

### Signal Types
- Signals recorded: [detected: ECG/EDA/EMG/Respiration/Pupil]

### ECG/HRV Acquisition (if applicable)
- System: [detected from files: AcqKnowledge/BIOPAC/etc.]
- Lead configuration: [TO BE COMPLETED]
- Electrode placement: [TO BE COMPLETED]
- Sampling rate: [VERIFY: detected value]
- Online filters: [TO BE COMPLETED]

### EDA Acquisition (if applicable)
- System: [detected from files]
- Electrode placement: [TO BE COMPLETED]
- Electrode type: [TO BE COMPLETED]
- Sampling rate: [VERIFY: detected value]
- Measurement mode: [TO BE COMPLETED]

### EMG Acquisition (if applicable)
- System: [detected from files]
- Muscle sites: [TO BE COMPLETED]
- Electrode placement: [TO BE COMPLETED]
- Sampling rate: [VERIFY: detected value]

### Other Signals
- [Additional signals as detected]

## Experimental Paradigm
- Task: [TO BE COMPLETED]
- Conditions: [TO BE COMPLETED]
- Trial structure: [TO BE COMPLETED]
- Baseline period: [extracted or TO BE COMPLETED]

## Signal Processing

### ECG/HRV Processing (if applicable)
- R-peak detection: [detected algorithm or TO BE COMPLETED]
- Artifact detection: [extracted method or TO BE COMPLETED]
- Ectopic beat handling: [TO BE COMPLETED]
- RR interval filtering: [extracted or TO BE COMPLETED]

### EDA Processing (if applicable)
- Artifact removal: [extracted method or TO BE COMPLETED]
- Decomposition method: [detected or TO BE COMPLETED]
- SCR detection criteria: [extracted or TO BE COMPLETED]
- Baseline correction: [TO BE COMPLETED]

### EMG Processing (if applicable)
- Filtering: [extracted parameters or TO BE COMPLETED]
- Rectification: [TO BE COMPLETED]
- Smoothing: [extracted or TO BE COMPLETED]

## Analysis Plan

### Dependent Variables
- HRV measures: [detected: SDNN/RMSSD/LF/HF or TO BE COMPLETED]
- EDA measures: [detected: SCL/SCR or TO BE COMPLETED]
- EMG measures: [TO BE COMPLETED]
- Analysis windows: [extracted or TO BE COMPLETED]

### Statistical Analysis
- Primary analyses: [extracted or TO BE COMPLETED]
- Statistical tests: [detected or TO BE COMPLETED]
- Covariates: [TO BE COMPLETED]
- Multiple comparisons: [TO BE COMPLETED]

## Ethics & Data Management
[From ETHICS_PRIVACY_TEMPLATE.md]
```

## Behavior Rules

1. **Always scan script files** before asking about parameters
2. **Detect signal types** from file extensions and keywords
3. **Mark confidence levels** for each detection:
   - ✓ High (direct in script, >2 mentions)
   - ~ Medium (inferred from patterns)
   - ? Low (guess, needs verification)
4. **Never modify** project files
5. **Ask focused questions** - one section at a time
6. **Provide examples** for user input fields
7. **Save as** `PREREGISTRATION_DRAFT.md` in project root

## Example Interaction

```
User: Create a preregistration

Agent:
1. Scans directory
2. Finds: data.acq, process_hrv.py, analyze_eda.m
3. ✓ Detects: Psychophysiology (confidence: high)
4. Identifies signals:
   - ECG/HRV (found "hrv", "r_peaks", "RMSSD")
   - EDA (found "eda", "scr", "ledalab")
5. Scans Python script:
   - Finds: nk.ecg_process(ecg, sampling_rate=1000)
   - Finds: nk.hrv_time(peaks) → SDNN, RMSSD
   - Finds: nk.hrv_frequency(peaks) → LF, HF
6. Scans MATLAB script:
   - Finds: ledalab analyze
   - Finds: SCR detection threshold: 0.05 µS
7. Generates draft with:
   - ✓ Signals: ECG, EDA
   - ✓ Sampling rate: 1000 Hz (ECG)
   - ✓ HRV measures: SDNN, RMSSD, LF, HF
   - ~ EDA processing: Ledalab
   - ? Electrode placement: [TO BE COMPLETED]
8. Asks:
   - "Confirm ECG lead configuration?"
   - "Specify EDA electrode placement?"
   - "Define baseline and task periods?"
9. Saves: PREREGISTRATION_DRAFT.md
```

## Configuration

Load from `configs/psychophys-config.json`:
```json
{
  "modality": "psychophys",
  "template": "templates/psychophys/PSYCHOPHYSIOLOGY_PREREGISTRATION_GUIDE.md",
  "signal_types": ["ecg", "hrv", "eda", "emg", "respiration", "pupil"],
  "search_patterns": {
    "software": ["acqknowledge", "biopac", "kubios", "ledalab", "neurokit", "biosppy", "rhrv"],
    "ecg_keywords": ["ecg", "hrv", "r_peak", "rr_interval", "SDNN", "RMSSD", "LF", "HF"],
    "eda_keywords": ["eda", "gsr", "scr", "scl", "skin_conductance"],
    "emg_keywords": ["emg", "muscle", "rectify", "envelope"],
    "resp_keywords": ["resp", "breathing", "respiration_rate"],
    "pupil_keywords": ["pupil", "diameter", "dilation"]
  },
  "required_sections": [
    "Metadata",
    "Study Information",
    "Participants",
    "Psychophysiological Measures",
    "Experimental Paradigm",
    "Signal Processing",
    "Analysis Plan",
    "Ethics"
  ]
}
```

## Related Resources

- Template: `templates/psychophys/PSYCHOPHYSIOLOGY_PREREGISTRATION_GUIDE.md`
- Common metadata: `templates/biopsych/common/METADATA_SCHEMA.md`
- Ethics template: `templates/biopsych/common/ETHICS_PRIVACY_TEMPLATE.md`
- References: See README.md "Psychophysiology Resources" section

## Key References

1. Boucsein et al. (2012). Publication recommendations for electrodermal measurements. Psychophysiology, 49(8), 1017-1034.
2. Task Force (1996). Heart rate variability: Standards of measurement. European Heart Journal, 17(3), 354-381.
3. Fridlund & Cacioppo (1986). Guidelines for human electromyographic research. Psychophysiology, 23(5), 567-589.
4. Cacioppo et al. (2007). Handbook of Psychophysiology (3rd ed.). Cambridge University Press.
