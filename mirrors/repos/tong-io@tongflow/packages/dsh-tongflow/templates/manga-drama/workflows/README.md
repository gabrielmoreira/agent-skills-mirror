One workflow file per generated asset, named after its target: `CHR_MEI_REF.tongflow.json`,
`EP01_SC001_SH0010_KF.tongflow.json`, `EP01_CUT.tongflow.json`. Start from `templates/`
(`tongflow_workflow_new({ path: 'EP01_SC001_SH0010_KF', fromTemplate: 'shot-keyframe' })`),
then patch the prompt / refs into the nodes so the file is self-contained and re-runnable.
