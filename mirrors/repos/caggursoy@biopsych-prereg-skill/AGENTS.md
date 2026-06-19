# AGENTS.md - Instructions for AI Agents

## Repository Purpose

This repository provides an automated preregistration generation skill for biopsychology research. The implementation consists of modality-specific skills that analyze research projects and generate preregistrations.

## Implementation Overview

The skill system is organized hierarchically:

1. **Base Skill** (`skills/biopsych/SKILL.md`):
   - Scans project directory and detects modality
   - Routes to appropriate modality-specific skill
   - Loads configuration from `configs/biopsych-config.json`

2. **Modality-Specific Skills**:
   - `skills/eeg/SKILL.md` - EEG/ERP research analysis
   - `skills/fmri/SKILL.md` - fMRI research analysis  
   - `skills/online/SKILL.md` - Online behavioral research analysis
   - Each has its own configuration file in `configs/`

3. **Configuration Files** (`configs/*.json`):
   - Define file patterns and software signatures
   - Specify parameters to extract
   - Set confidence thresholds
   - Document required sections

## How to Use This Repository

### When User Requests Preregistration

1. **Start with base skill** - Read `skills/biopsych/SKILL.md`
2. **Scan the current directory** for research files
3. **Detect modality** using patterns in `configs/biopsych-config.json`
4. **Load modality-specific skill**:
   - EEG detected → `skills/eeg/SKILL.md` + `configs/eeg-config.json`
   - fMRI detected → `skills/fmri/SKILL.md` + `configs/fmri-config.json`
   - Online detected → `skills/online/SKILL.md` + `configs/online-config.json`
5. **Extract information** using patterns from modality config
6. **Select appropriate template** from `templates/` directory
7. **Generate draft** with filled/blank/verify sections
8. **Save as** `PREREGISTRATION_DRAFT.md`
9. **Interact with user** to complete missing sections

### Detection Patterns

**EEG/ERP**: `.set`, `.fdt`, `.vhdr`, `.eeg`, `.bdf` files; EEGLAB/MNE/FieldTrip scripts
**fMRI**: `.nii`, `.nii.gz` files; BIDS structure; SPM/FSL/fMRIPrep scripts
**Online**: `.html`, `.js`, `.json` files; jsPsych/Qualtrics/Pavlovia code
**Psychophys**: `.acq`, `.mat` files; AcqKnowledge/Kubios scripts; ECG/EDA/HRV keywords

### Templates Available

- `templates/eeg/EEG_ERP_PREREGISTRATION_GUIDE.md` - For EEG/ERP studies
- `templates/fmri/FMRI_PREREGISTRATION_GUIDE.md` - For fMRI studies
- `templates/online/ONLINE_BEHAVIORAL_PREREGISTRATION_GUIDE.md` - For online experiments
- `templates/psychophys/PSYCHOPHYSIOLOGY_PREREGISTRATION_GUIDE.md` - For psychophysiology
- `templates/biopsych/common/METADATA_SCHEMA.md` - Common metadata (use for all)
- `templates/biopsych/common/ETHICS_PRIVACY_TEMPLATE.md` - Ethics section (use for all)

### Information to Extract

From **scripts** (Python, R, MATLAB):
- Software versions
- Preprocessing parameters
- Statistical tests
- Sample size calculations
- Analysis pipelines

From **documentation** (README, protocols):
- Study title and description
- Hypotheses
- Experimental design
- Participant criteria
- Ethics approval information

From **data files**:
- Number of participants
- Number of trials/conditions
- Data structure

### Output Format

Create `PREREGISTRATION_DRAFT.md` with:
- Metadata section (always include)
- Ethics section (always include)
- Modality-specific sections (based on detected type)
- Filled sections (information found in files)
- `[TO BE COMPLETED]` markers for missing required information
- `[VERIFY: detected_value]` markers for uncertain detections
- Comments showing where information was found

### User Interaction Guidelines

1. **Announce what you detected** before generating
2. **Show confidence levels** (high/medium/low)
3. **Ask questions one section at a time** (not overwhelming)
4. **Provide examples** when requesting input
5. **Allow skipping** sections to return later
6. **Confirm uncertain detections** before finalizing

### Example Workflow

```
User: "Create a preregistration"

Agent:
1. Scans directory
2. Finds .set files and EEGLAB scripts
3. Detects: EEG/ERP study
4. Reads README for study title
5. Parses preprocessing script for parameters
6. Generates draft using EEG template
7. Marks missing sections
8. Asks user to confirm/complete
9. Saves PREREGISTRATION_DRAFT.md
```

### Important Rules

- **Never modify** existing project files
- **Always mark** uncertain detections for verification
- **Include all** required sections from templates
- **Reference** where information was found
- **Ask before** making assumptions
- **Save output** as `PREREGISTRATION_DRAFT.md`

### Multimodal Studies

If multiple modalities detected:
1. Ask user which is primary
2. Combine relevant templates
3. Add synchronization section
4. Avoid duplicate sections

### Error Handling

- **No files found**: Ask about study type, create blank template
- **Ambiguous modality**: Present options, ask user to choose
- **Conflicting info**: Show conflicts, ask for clarification
- **Missing critical info**: Mark as required, explain why needed

### References

All templates include comprehensive references. When generating preregistrations:
- Cite the template used
- Include DOIs for methods
- Reference software versions
- Link to preregistration platforms

### Quick Reference

- **Base skill**: `skills/biopsych/SKILL.md`
- **EEG skill**: `skills/eeg/SKILL.md`
- **fMRI skill**: `skills/fmri/SKILL.md`
- **Online skill**: `skills/online/SKILL.md`
- **Configurations**: `configs/*.json`
- **Usage guide**: `USAGE_GUIDE.md`
- **Contributing guide**: `CONTRIBUTING.md`
- **Validation checklist**: `VALIDATION_CHECKLIST.md`
- **Project summary**: `PROJECT_SUMMARY.md`
- **Main documentation**: `README.md`

## Coding Conventions

- Use Markdown for all outputs
- Follow template structure exactly
- Mark sections clearly (`[TO BE COMPLETED]`, `[VERIFY: ...]`)
- Include inline comments for transparency
- Save with descriptive filenames

## Testing

Before deploying or using a skill, verify:
- [ ] Modality correctly detected
- [ ] Configuration file loads properly
- [ ] All required sections in template
- [ ] Extracted information is accurate
- [ ] Missing sections marked appropriately
- [ ] User prompts are clear and helpful
- [ ] Output saved correctly

For comprehensive validation, see `VALIDATION_CHECKLIST.md`

## Version Information

- **Implementation**: v1.1 (complete with modality-specific skills)
- **Templates based on**: 2025-2026 standards
- **Last updated**: 2026-06-17
- **Status**: ✅ Ready for production

### What's Implemented

- ✅ Base skill for modality detection (`skills/biopsych/SKILL.md`)
- ✅ EEG/ERP skill with parameter extraction (`skills/eeg/SKILL.md`)
- ✅ fMRI skill with BIDS validation (`skills/fmri/SKILL.md`)
- ✅ Online behavioral skill with platform detection (`skills/online/SKILL.md`)
- ✅ Configuration files for all modalities
- ✅ Example preregistrations for each modality
- ✅ Validation checklist for testing
- ✅ Contributing guidelines
- ✅ MIT License

### Future Enhancements

- [ ] Psychophysiology skill (`skills/psychophys/SKILL.md`)
- [ ] MEG/MEEG skills  
- [ ] TMS/fNIRS templates
- [ ] EMA/ESM templates
- [ ] Multi-modal integration improvements
- [ ] Web-based UI for skill execution

---

**Status**: The goal is to make preregistration easy and thorough. Extract what you can, mark what's missing, and guide the user through completion interactively.
