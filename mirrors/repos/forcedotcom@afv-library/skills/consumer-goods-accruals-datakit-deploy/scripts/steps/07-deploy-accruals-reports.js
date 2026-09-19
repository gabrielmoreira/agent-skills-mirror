const fs = require('fs');
const os = require('os');
const path = require('path');
const { execDeployJson, execSfJson } = require('./utils');

const OBJECT_SOURCE_TARGET_MAPS_DIR = 'objectSourceTargetMaps';

/**
 * Step 7: Deploy Accruals Reports with Data Space replacements.
 *
 * The Accruals Reports payload contains references between objects (DLOs/DLMs)
 * and ObjectSourceTargetMap definitions. The maps reference fields that only
 * exist after the other folders (objects, wave, ...) are deployed, so we must
 * deploy them in two passes: first everything except objectSourceTargetMaps,
 * then objectSourceTargetMaps on its own.
 *
 * @param {string} orgAlias - The Salesforce org alias
 * @param {string} setupDir - The setup directory path
 * @param {boolean} skipDataSpace - Whether to skip data space configuration
 * @param {string} configuredDataSpaceName - The data space name from config
 * @param {string} configuredDataSpacePrefix - The data space prefix from config
 * @param {string} namespace - Org namespace prefix (e.g. "cgcloud_dev__"), or '' for unmanaged orgs
 * @param {boolean} dryRun - If true, skip deployment but keep temp files
 */
async function deployAccrualsReports(
  orgAlias,
  setupDir,
  skipDataSpace,
  configuredDataSpaceName,
  configuredDataSpacePrefix,
  namespace = '',
  dryRun = false
) {
  console.log('\n=== Step 7: Deploying Accruals Reports ===');

  // Use "default" and empty prefix if skipping data space, otherwise use configured values
  const dataSpaceName = skipDataSpace ? 'default' : configuredDataSpaceName;
  const dataSpacePrefix = skipDataSpace ? '' : configuredDataSpacePrefix;

  console.log(`Data Space Name: ${dataSpaceName}`);
  console.log(`Data Space Prefix: ${dataSpacePrefix || '(empty)'}`);
  console.log(`Org Namespace: ${namespace || '(none)'}`);

  // setupDir is already the CGCloudAddons extraction dir (e.g. <tmp>/CGCloudAddons)
  const sourceDir = path.join(setupDir, 'TPM', 'Accruals', 'Accruals Reports');
  const tempDir = path.join(setupDir, 'temp-accruals-reports');

  if (fs.existsSync(tempDir)) {
    console.log('Cleaning up existing temp directory...');
    fs.rmSync(tempDir, { recursive: true });
  }

  console.log('Copying Accruals Reports to temp directory...');
  copyDirectory(sourceDir, tempDir);

  console.log('Replacing Data Space placeholders and namespace in file names and contents...');
  replaceDataSpacePlaceholders(tempDir, dataSpaceName, dataSpacePrefix, namespace);

  const deployPath = path.join(tempDir, 'force-app');
  const defaultDir = path.join(deployPath, 'main', 'default');
  const objectSourceTargetMapsPath = path.join(defaultDir, OBJECT_SOURCE_TARGET_MAPS_DIR);
  const hasMaps = fs.existsSync(objectSourceTargetMapsPath);

  // objectSourceTargetMaps reference Data Cloud DLO/DLM objects by name.
  //
  // The template uses _ORG_NS_ (replaced above with the org namespace, e.g. "cgcloud__")
  // and _DATASPACE_PREFIX_ (replaced with e.g. "DS2_").
  //
  // For DLO (__dll) and DLM (__dlm) object names and their field names, _ORG_NS_ is wrong:
  // Data Cloud objects (MktDataLakeObject / MktDataModelObject) carry their OWN
  // NamespacePrefix, which is independent of the org/package namespace. We query the
  // actual DLO NamespacePrefix from the org at runtime and use that for correction.
  //
  // For targetObjectName the DataSpace prefix (DS2_) must be KEPT — it is part of the
  // DataSpace-scoped DMO name (e.g. DS2_accrualoutput_decorated__dlm).
  //
  // Field names inside DLO/DLM references also need the DLO namespace, not the org namespace.
  if (hasMaps) {
    // Query the actual NamespacePrefix of the DLO from the org (may differ from org namespace)
    let dloNamespace = '';
    try {
      const dloQuery = execSfJson([
        'data', 'query', '--target-org', orgAlias, '--json',
        '--query', "SELECT NamespacePrefix FROM MktDataLakeObject WHERE DeveloperName='accrualoutput_decorated' LIMIT 1"
      ]);
      const dloRecs = (dloQuery.result && dloQuery.result.records) || [];
      const raw = dloRecs.length > 0 ? (dloRecs[0].NamespacePrefix || '') : '';
      dloNamespace = raw ? (raw.endsWith('__') ? raw : raw + '__') : '';
    } catch (dloNsErr) {
      // MktDataLakeObject may not be accessible in all org configurations — fall back to no DLO namespace.
      // Log so operators can see the root cause rather than hitting a silent mis-mapping later.
      console.warn(`[WARN] Could not query DLO namespace (falling back to empty): ${dloNsErr.message}`);
      dloNamespace = '';
    }

    // The org namespace (applied by replaceDataSpacePlaceholders) that we need to undo on
    // DLO/DLM names if it differs from the actual DLO namespace.
    const appliedNs = namespace || '';  // what _ORG_NS_ was replaced with

    const fixObjectName = (name) => {
      let n = name;
      // If the org namespace was applied to DLO/DLM names, undo it, then re-apply the
      // correct DLO namespace (which may be different, e.g. '' for Data Cloud objects
      // even in a namespaced org).
      if (appliedNs && appliedNs !== dloNamespace) {
        const escapedApplied = appliedNs.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        // Undo on DLO/DLM object names: cgcloud__accrualX__dll → <dloNs>accrualX__dll
        n = n.replace(new RegExp(escapedApplied + '(\\w+__dl[lm])', 'g'), dloNamespace + '$1');
        // Undo on field names inside DLO/DLM refs: __dll.cgcloud__Field__c → __dll.<dloNs>Field__c
        n = n.replace(new RegExp('(__dl[lm]\\.)' + escapedApplied + '(\\w+__c)', 'g'), '$1' + dloNamespace + '$2');
      }
      // NOTE: do NOT touch the DataSpace prefix on __dlm names.
      // The MDAPI targetObjectName must include the DataSpace prefix (e.g. DS2_accrualoutput_decorated__dlm)
      // to resolve to the DataSpace-scoped DMO. Removing it causes error 1923914934.
      return n;
    };
    for (const entry of fs.readdirSync(objectSourceTargetMapsPath)) {
      const fp = path.join(objectSourceTargetMapsPath, entry);
      if (!fs.statSync(fp).isFile()) continue;
      // Fix file contents: fix object/field names, then strip the filterOperationType
      // tag from fieldSourceTargetMaps entries. That tag is present in the template but
      // is not present in working org-deployed maps and causes an "unexpected error" on deploy.
      let fileContent = fixObjectName(fs.readFileSync(fp, 'utf8'));
      fileContent = fileContent.replace(
        /\s*<filterOperationType>[^<]*<\/filterOperationType>/g, ''
      );
      fs.writeFileSync(fp, fileContent, 'utf8');
      // Fix the filename: strip any leading DataSpace prefix from the stem so the
      // MDAPI DeveloperName (= file stem) matches the masterLabel inside the XML.
      // The template uses _DATASPACE_PREFIX_ as a file-naming hint; after replacement
      // the file starts with e.g. "DS2_" but the DeveloperName should not have that.
      let fixedName = entry;
      if (dataSpacePrefix && fixedName.startsWith(dataSpacePrefix)) {
        fixedName = fixedName.slice(dataSpacePrefix.length);
      }
      if (namespace && fixedName.startsWith(namespace)) {
        fixedName = fixedName.slice(namespace.length);
      }
      if (fixedName !== entry) {
        fs.renameSync(fp, path.join(objectSourceTargetMapsPath, fixedName));
      }
    }
  }

  if (dryRun) {
    console.log('[DRY RUN] Skipping deployment - files prepared at:');
    console.log(`  ${tempDir}`);
    if (hasMaps) {
      console.log(`[DRY RUN] objectSourceTargetMaps would deploy in a second pass from:`);
      console.log(`  ${objectSourceTargetMapsPath}`);
    }
    console.log('[DRY RUN] Temp directory preserved for inspection');
    console.log('[OK] Step 7 completed (dry run)\n');
    return;
  }

  // Deployment order:
  //   Pass 1 — objects (DLM fields) only: must deploy before objectSourceTargetMaps
  //             (the maps reference fields that only exist once the DLM objects are in place).
  //             Wave (CRM Analytics) folder is staged aside so it doesn't cause
  //             "Not available for deploy" failures if CRM Analytics is not enabled.
  //   Pass 2 — objectSourceTargetMaps
  //   Pass 3 — wave (CRM Analytics dashboards), best-effort: warns but does not crash
  //             if CRM Analytics is not enabled in the org.

  const wavePath = path.join(defaultDir, 'wave');
  const hasWave = fs.existsSync(wavePath);
  const stagedWavePath = path.join(tempDir, '__staged-wave');

  // Stage wave aside so it doesn't contaminate the first two passes
  if (hasWave) {
    if (fs.existsSync(stagedWavePath)) fs.rmSync(stagedWavePath, { recursive: true });
    console.log('Staging wave folder aside for the third deployment pass...');
    fs.renameSync(wavePath, stagedWavePath);
  }

  let stagedMapsPath = null;
  if (hasMaps) {
    stagedMapsPath = path.join(tempDir, '__staged-objectSourceTargetMaps');
    if (fs.existsSync(stagedMapsPath)) fs.rmSync(stagedMapsPath, { recursive: true });
    console.log('Setting aside objectSourceTargetMaps for the second deployment pass...');
    fs.renameSync(objectSourceTargetMapsPath, stagedMapsPath);
  }

  // Helper: convert tempDir source to MDAPI and deploy it, then clean up mdapi temp.
  function convertAndDeploy(label) {
    const mdapiOut = path.join(os.tmpdir(), `tpm_accruals_reports_mdapi_${label}_${Date.now()}`);
    try {
      const conv = execSfJson(['project', 'convert', 'source', '--output-dir', mdapiOut, '--json'], { cwd: tempDir });
      if (conv.status !== 0) {
        throw new Error(`Source conversion failed (${label}): ${conv.message || JSON.stringify(conv)}`);
      }
      execDeployJson(['project', 'deploy', 'start', '--metadata-dir', mdapiOut, '--target-org', orgAlias]);
    } finally {
      try { fs.rmSync(mdapiOut, { recursive: true }); } catch (cleanupErr) {
        console.warn(`[WARN] Could not remove temp directory ${mdapiOut}: ${cleanupErr.message}`);
      }
    }
  }

  try {
    // Pass 1: objects (DLM fields)
    console.log('Deploying Accruals Reports metadata (pass 1: objects)...');
    convertAndDeploy('pass1');

    // Pass 2: objectSourceTargetMaps.
    // The ObjectSourceTargetMap MDAPI deploy requires the DataSpace-scoped DMO
    // (DS2_accrualoutput_decorated) to have IsEnabled=true in MktDataModelObject.
    // The DataKit deployment leaves it as INACTIVE. We activate it here via
    // the Tooling API before deploying the map.
    if (stagedMapsPath) {
      console.log('Restoring objectSourceTargetMaps for the second deployment pass...');
      fs.renameSync(stagedMapsPath, objectSourceTargetMapsPath);
      stagedMapsPath = null;

      // Activate the DataSpace-scoped DMO (MktDataModelObject) so MDAPI can deploy the map.
      if (!skipDataSpace && dataSpacePrefix) {
        console.log('Activating DataSpace-scoped DMO for objectSourceTargetMaps deploy...');
        // DMO must be active before MDAPI will accept the ObjectSourceTargetMap.
        // If activation fails, the map deploy will fail with opaque error 1923914934 — throw early with a clear message.
        activateDmoForDataSpace(orgAlias, dataSpacePrefix, namespace);
      }

      console.log('Deploying Accruals Reports metadata (pass 2: objectSourceTargetMaps)...');
      try {
        convertAndDeploy('pass2');
      } catch (err) {
        if (err.message && (err.message.includes('no CustomObject named') || err.message.includes('Not available for deploy'))) {
          console.warn('[WARN] objectSourceTargetMaps deploy skipped — Data Cloud DLO/DLM objects not accessible via MDAPI in this org.');
          console.warn('[WARN] This is expected when Data Cloud is not fully provisioned.');
          console.warn(`[WARN] Original error: ${err.message.split('\n')[0]}`);
        } else {
          throw err;
        }
      }
    }
  } finally {
    // Restore any staged folders so the temp tree is consistent for inspection.
    if (stagedMapsPath && fs.existsSync(stagedMapsPath) && !fs.existsSync(objectSourceTargetMapsPath)) {
      fs.renameSync(stagedMapsPath, objectSourceTargetMapsPath);
    }
    if (hasWave && fs.existsSync(stagedWavePath) && !fs.existsSync(wavePath)) {
      fs.renameSync(stagedWavePath, wavePath);
    }
  }

  // Pass 3: wave (CRM Analytics) — split into two sub-passes:
  //   3a: WaveApplication (.wapp) + WaveDashboards (.wdash/.wdash-meta.xml) only
  //       These can deploy even before any data has flowed through the pipeline.
  //   3b: WaveXmd (.xmd-meta.xml) best-effort
  //       XMDs annotate datasets that only exist after the pipeline has run once.
  //       They are expected to fail on fresh installs; this is non-fatal.
  if (hasWave) {
    // Move wave back into place for conversion
    if (fs.existsSync(stagedWavePath)) fs.renameSync(stagedWavePath, wavePath);
    // Stage everything except wave aside so only wave deploys
    const stageForWave = path.join(tempDir, '__staged-non-wave');
    if (fs.existsSync(stageForWave)) fs.rmSync(stageForWave, { recursive: true });
    fs.mkdirSync(stageForWave, { recursive: true });
    const defaultEntries = fs.readdirSync(defaultDir, { withFileTypes: true });
    for (const e of defaultEntries) {
      if (e.name !== 'wave') {
        fs.renameSync(path.join(defaultDir, e.name), path.join(stageForWave, e.name));
      }
    }

    // Stage XMD files aside for pass 3b (they need datasets that don't exist yet on fresh install)
    const xmdStageDir = path.join(tempDir, '__staged-xmd');
    if (fs.existsSync(xmdStageDir)) fs.rmSync(xmdStageDir, { recursive: true });
    fs.mkdirSync(xmdStageDir, { recursive: true });
    const xmdFiles = fs.readdirSync(wavePath).filter(n => n.endsWith('.xmd-meta.xml'));
    for (const xmd of xmdFiles) {
      fs.renameSync(path.join(wavePath, xmd), path.join(xmdStageDir, xmd));
    }

    console.log('Deploying Accruals Reports metadata (pass 3a: WaveApplication + WaveDashboards)...');
    let waveDeployOk = false;
    try {
      convertAndDeploy('pass3a-wave');
      waveDeployOk = true;
    } catch (err) {
      if (err.message && err.message.includes('Not available for deploy for this organization')) {
        console.warn('[WARN] Wave dashboards skipped — CRM Analytics is not enabled/licensed in this org.');
        console.warn('[WARN] Enable Analytics Studio / CRM Analytics and re-run Step 7 to deploy the dashboards.');
      } else {
        console.warn(`[WARN] Wave dashboard deploy failed: ${err.message}`);
      }
    } finally {
      // Restore staged non-wave folders
      for (const e of fs.readdirSync(stageForWave, { withFileTypes: true })) {
        const dest = path.join(defaultDir, e.name);
        if (!fs.existsSync(dest)) {
          fs.renameSync(path.join(stageForWave, e.name), dest);
        }
      }
      try { fs.rmSync(stageForWave, { recursive: true }); } catch (cleanupErr) {
        console.warn(`[WARN] Could not remove temp staging directory: ${cleanupErr.message}`);
      }
    }

    if (waveDeployOk) {
      console.log('[OK] Wave dashboards deployed.\n');
    }

    // Pass 3b: XMDs — best-effort, expected to fail if datasets don't exist yet
    if (xmdFiles.length > 0) {
      // Restore XMDs into wave folder
      for (const xmd of xmdFiles) {
        fs.renameSync(path.join(xmdStageDir, xmd), path.join(wavePath, xmd));
      }
      // Stage all non-XMD wave files aside
      const stageNonXmd = path.join(tempDir, '__staged-non-xmd');
      if (fs.existsSync(stageNonXmd)) fs.rmSync(stageNonXmd, { recursive: true });
      fs.mkdirSync(stageNonXmd, { recursive: true });
      const waveEntries = fs.readdirSync(wavePath, { withFileTypes: true });
      for (const e of waveEntries) {
        if (!e.name.endsWith('.xmd-meta.xml')) {
          fs.renameSync(path.join(wavePath, e.name), path.join(stageNonXmd, e.name));
        }
      }
      // Also stage non-wave default dirs aside
      const stageForXmd = path.join(tempDir, '__staged-non-wave-for-xmd');
      if (fs.existsSync(stageForXmd)) fs.rmSync(stageForXmd, { recursive: true });
      fs.mkdirSync(stageForXmd, { recursive: true });
      const defaultEntriesForXmd = fs.readdirSync(defaultDir, { withFileTypes: true });
      for (const e of defaultEntriesForXmd) {
        if (e.name !== 'wave') {
          fs.renameSync(path.join(defaultDir, e.name), path.join(stageForXmd, e.name));
        }
      }

      console.log('Deploying Accruals Reports metadata (pass 3b: WaveXmd, best-effort)...');
      try {
        convertAndDeploy('pass3b-xmd');
        console.log('[OK] WaveXmd metadata deployed.\n');
      } catch (err) {
        console.warn('[WARN] WaveXmd deploy skipped — datasets not yet available (expected on fresh install).');
        console.warn('[WARN] XMD files can be re-deployed after the accrual pipeline has run at least once.');
        console.warn(`[WARN] Original error: ${err.message.split('\n')[0]}`);
      } finally {
        // Restore all staged items
        for (const e of fs.readdirSync(stageNonXmd, { withFileTypes: true })) {
          const dest = path.join(wavePath, e.name);
          if (!fs.existsSync(dest)) fs.renameSync(path.join(stageNonXmd, e.name), dest);
        }
        try { fs.rmSync(stageNonXmd, { recursive: true }); } catch (_) {}
        for (const e of fs.readdirSync(stageForXmd, { withFileTypes: true })) {
          const dest = path.join(defaultDir, e.name);
          if (!fs.existsSync(dest)) fs.renameSync(path.join(stageForXmd, e.name), dest);
        }
        try { fs.rmSync(stageForXmd, { recursive: true }); } catch (_) {}
      }
    }
    try { fs.rmSync(xmdStageDir, { recursive: true }); } catch (_) {}
  }

  console.log('Cleaning up temp directory...');
  try { fs.rmSync(tempDir, { recursive: true }); } catch (_) {}

  console.log('[OK] Accruals Reports deployed successfully\n');
}

/**
 * Recursively copy a directory
 */
function copyDirectory(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDirectory(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

/**
 * Replace placeholders in a name (file or directory)
 * Handles double underscore pattern to avoid DS2__ becoming DS2___
 */
function replaceNamePlaceholders(name, dataSpaceName, dataSpacePrefix, namespace) {
  let newName = name;
  if (dataSpacePrefix === '') {
    newName = newName.replace(/_DATASPACE_PREFIX__/g, '');
  } else {
    newName = newName.replace(/_DATASPACE_PREFIX__/g, dataSpacePrefix);
  }
  newName = newName
    .replace(/_DATASPACE_PREFIX_/g, dataSpacePrefix)
    .replace(/_DATASPACE_NAME_/g, dataSpaceName)
    .replace(/_ORG_NS_/g, namespace || '');
  return newName;
}

/**
 * Replace Data Space placeholders in both file names and file contents
 */
function replaceDataSpacePlaceholders(dir, dataSpaceName, dataSpacePrefix, namespace) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const oldPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      replaceDataSpacePlaceholders(oldPath, dataSpaceName, dataSpacePrefix, namespace);

      if (entry.name.includes('_DATASPACE_PREFIX_') || entry.name.includes('_DATASPACE_NAME_') || entry.name.includes('_ORG_NS_')) {
        const newName = replaceNamePlaceholders(entry.name, dataSpaceName, dataSpacePrefix, namespace);
        const newPath = path.join(dir, newName);
        fs.renameSync(oldPath, newPath);
      }
    } else {
      replaceInFile(oldPath, dataSpaceName, dataSpacePrefix, namespace);

      if (entry.name.includes('_DATASPACE_PREFIX_') || entry.name.includes('_DATASPACE_NAME_') || entry.name.includes('_ORG_NS_')) {
        const newName = replaceNamePlaceholders(entry.name, dataSpaceName, dataSpacePrefix, namespace);
        const newPath = path.join(dir, newName);
        fs.renameSync(oldPath, newPath);
      }
    }
  }
}

/**
 * Replace placeholders in file contents
 */
function replaceInFile(filePath, dataSpaceName, dataSpacePrefix, namespace) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');

    if (content.includes('_DATASPACE_PREFIX_') || content.includes('_DATASPACE_NAME_') || content.includes('_ORG_NS_')) {
      if (dataSpacePrefix === '') {
        // If dataspace prefix is empty, remove double underscore pattern entirely
        content = content.replace(/_DATASPACE_PREFIX__/g, '');
      } else {
        // Replace double underscore pattern first to avoid double underscores in output
        // _DATASPACE_PREFIX__ with DS2_ results in DS2_ (not DS2__)
        content = content.replace(/_DATASPACE_PREFIX__/g, dataSpacePrefix);
      }

      content = content
        .replace(/_DATASPACE_PREFIX_/g, dataSpacePrefix)
        .replace(/_DATASPACE_NAME_/g, dataSpaceName)
        .replace(/_ORG_NS_/g, namespace || '');

      fs.writeFileSync(filePath, content, 'utf8');
    }
  } catch (error) {
    if (error.code === 'EISDIR') {
      // Directory entry — skip silently, expected when walking mixed trees
      return;
    }
    // Unexpected I/O failure (missing file, permission error, write error)
    throw new Error(`Failed to process template file ${filePath}: ${error.message}`, { cause: error });
  }
}

/**
 * Activate the DataSpace-scoped DMO (MktDataModelObject) via the Tooling API.
 *
 * The DataKit deployment creates the DS2_<name> DMO in INACTIVE state. MDAPI refuses to
 * deploy an ObjectSourceTargetMap for an INACTIVE DMO (opaque error 1923914934). This
 * function queries the MktDataModelObject by DeveloperName and sets IsEnabled=true via PATCH.
 */
function activateDmoForDataSpace(orgAlias, dataSpacePrefix, namespace) {
  // DeveloperName = dataSpacePrefix (without trailing _) + '_accrualoutput_decorated'
  const pfxBase = dataSpacePrefix.replace(/_$/, '');
  const dmoDevName = `${pfxBase}_accrualoutput_decorated`;

  // Query via sf data query --use-tooling-api — CLI supplies auth, no token extraction.
  // Returns: status=0 on success, result.records as array.
  const queryResult = execSfJson([
    'data', 'query',
    '--query', `SELECT Id,IsEnabled,DataModelObjectStatus FROM MktDataModelObject WHERE DeveloperName='${dmoDevName}'`,
    '--use-tooling-api', '--target-org', orgAlias, '--json'
  ]);
  const records = queryResult?.result?.records;
  if (queryResult?.status !== 0 || !Array.isArray(records)) {
    throw new Error(`Tooling query for DMO '${dmoDevName}' failed: ${queryResult?.message || JSON.stringify(queryResult)}`);
  }

  if (records.length === 0) {
    console.warn(`[WARN] DMO '${dmoDevName}' not found — skipping activation.`);
    return;
  }

  const { Id: dmoId, IsEnabled, DataModelObjectStatus } = records[0];
  if (IsEnabled && DataModelObjectStatus === 'ACTIVE') {
    console.log(`DMO '${dmoDevName}' already active — skipping.`);
    return;
  }

  console.log(`Activating DMO '${dmoDevName}' (was IsEnabled=${IsEnabled}, status=${DataModelObjectStatus})...`);
  // Update via sf data update record --use-tooling-api — CLI supplies auth, no token extraction.
  // Returns: status=0 on success, result.success=true.
  const updateResult = execSfJson([
    'data', 'update', 'record',
    '--sobject', 'MktDataModelObject',
    '--record-id', dmoId,
    '--values', `IsEnabled=true DataModelObjectStatus=ACTIVE RefEntityDeveloperName=accrualoutput_decorated`,
    '--use-tooling-api', '--target-org', orgAlias, '--json'
  ]);
  if (updateResult?.status !== 0 || !updateResult?.result?.success) {
    throw new Error(`Tooling update for DMO '${dmoDevName}' failed: ${updateResult?.message || JSON.stringify(updateResult?.result)}`);
  }
  console.log(`[OK] DMO '${dmoDevName}' activated.`);
}

module.exports = deployAccrualsReports;
