const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const {
  exec,
  getOrgDetails,
  getMaxCreatedDate,
  getBundleStreamMap,
  getDeploymentLogForComponents,
  getDeployedComponents,
  waitForDeploymentCompletion,
} = require('./utils');

/**
 * Build a list of component specs from a deployment payload.
 * Each spec carries an id (used for logging) and an array of names that, if
 * any are recorded as Successful in DataKitDeploymentLog, indicate the
 * component was deployed.
 *
 * For DataStreamBundle components we also include the developer names of the
 * dataStreamTemplates contained in the bundle, since DataKitDeploymentLog
 * tends to record the underlying streams rather than the bundle name itself.
 *
 * @param {object} payload - The DeployDataKitComponents payload
 * @param {Map<string, string[]>} bundleStreamMap - bundleName -> [streamDevNames]
 * @returns {Array<{id: string, type: string, names: string[]}>}
 */
function buildComponentSpecs(payload, bundleStreamMap) {
  const specs = [];

  const components =
    payload &&
    payload.inputs &&
    payload.inputs[0] &&
    payload.inputs[0].dataKitComponentsInput
      ? payload.inputs[0].dataKitComponentsInput
      : [];

  components.forEach(component => {
    if (component.dloConfig) {
      specs.push({
        id: component.dloConfig.apiName,
        type: 'DataLakeObject',
        names: [component.dloConfig.apiName, component.dloConfig.dataSourceObjectDevName].filter(Boolean),
      });
    } else if (component.dataTransformConfig) {
      specs.push({
        id: component.dataTransformConfig.apiName || component.dataTransformConfig.dataTransformDevName,
        type: 'DataTransform',
        names: [
          component.dataTransformConfig.apiName,
          component.dataTransformConfig.dataTransformDevName,
        ].filter(Boolean),
      });
    } else if (component.bundleConfig) {
      const bundleName = component.bundleConfig.bundleName;
      const childStreams = bundleStreamMap.get(bundleName) || [];
      // Bundles may not appear by their bundle name in the deployment log.
      // Track them by bundle name AND by their child data stream developer names.
      specs.push({
        id: bundleName,
        type: 'DataStreamBundle',
        names: [bundleName, ...childStreams],
      });
    } else if (component.dataActionTargetConfig) {
      specs.push({
        id: component.dataActionTargetConfig.name,
        type: 'DataActionTarget',
        names: [component.dataActionTargetConfig.name].filter(Boolean),
      });
    } else if (component.dataActionConfig) {
      specs.push({
        id: component.dataActionConfig.name,
        type: 'DataAction',
        names: [component.dataActionConfig.name].filter(Boolean),
      });
    }
  });

  return specs;
}

/**
 * Step 5: Deploy TPM Accruals data kit
 * @param {string} orgAlias - The Salesforce org alias
 * @param {string} scriptsDir - Path to the scripts directory
 * @param {string} dataKitPath - Path to the TPM Accruals Data Kit (for bundle->stream mapping)
 * @param {string} orgId - The Salesforce org ID
 * @param {string} namespace - Org namespace prefix (e.g. "cgcloud_dev__"), or '' for unmanaged orgs
 * @param {boolean} dryRun - If true, skip actual deployment
 */
async function deployTPMAccruals(orgAlias, scriptsDir, dataKitPath, orgId, namespace = '', dryRun = false) {
  console.log('\n=== Step 5: Deploying TPM Accruals ===');

  const dataKitName = 'TPM_Accruals';
  const payloadPath = path.join(scriptsDir, 'tpm-accruals-deployment-payload.json');

  console.log(`Payload: ${payloadPath}`);
  if (namespace) {
    console.log(`Org namespace: ${namespace}`);
  }

  // Read payload
  const payload = JSON.parse(fs.readFileSync(payloadPath, 'utf8'));
  const originalPayload = JSON.parse(JSON.stringify(payload));

  // Build bundle -> [stream developer names] map from the data kit's metadata.
  // This lets us recognize a bundle as deployed when its underlying streams
  // appear in the deployment log even if the bundle name itself does not.
  const bundleStreamMap = getBundleStreamMap(dataKitPath);

  // Build component specs (one per declared component) from the original payload
  const allComponentSpecs = buildComponentSpecs(payload, bundleStreamMap);

  // Check existing deployments for these specific components
  const deploymentLog = getDeploymentLogForComponents(orgAlias, allComponentSpecs);
  const deployedIds = getDeployedComponents(deploymentLog, allComponentSpecs, namespace);

  if (deployedIds.size > 0) {
    console.log(`Found ${deployedIds.size} already deployed components:`);
    deployedIds.forEach(comp => console.log(`  - ${comp}`));
  }

  // Filter out already deployed components from the payload
  const components = payload.inputs[0].dataKitComponentsInput;
  const componentsToSkip = new Set();

  components.forEach((component, index) => {
    let identifier = '';
    if (component.dloConfig) {
      identifier = component.dloConfig.apiName;
    } else if (component.dataTransformConfig) {
      identifier = component.dataTransformConfig.apiName || component.dataTransformConfig.dataTransformDevName;
    } else if (component.bundleConfig) {
      identifier = component.bundleConfig.bundleName;
    } else if (component.dataActionTargetConfig) {
      identifier = component.dataActionTargetConfig.name;
    } else if (component.dataActionConfig) {
      identifier = component.dataActionConfig.name;
    }

    if (identifier && deployedIds.has(identifier)) {
      componentsToSkip.add(index);
    }
  });

  if (componentsToSkip.size > 0) {
    console.log(`Skipping ${componentsToSkip.size} already deployed components`);
    payload.inputs[0].dataKitComponentsInput = components.filter((_, index) =>
      !componentsToSkip.has(index)
    );
  }

  const componentCount = payload.inputs[0].dataKitComponentsInput.length;

  if (componentCount === 0) {
    console.log(`[OK] All components already deployed, skipping ${dataKitName}\n`);
    return;
  }

  console.log(`${dryRun ? 'Would deploy' : 'Deploying'} ${componentCount} components...`);

  // Build component specs for the components actually being deployed
  const componentSpecs = buildComponentSpecs(payload, bundleStreamMap);

  // Replace org ID placeholder
  const payloadString = JSON.stringify(payload);
  const updatedPayloadString = payloadString.replace(/<SF_ORG_ID>/g, orgId.slice(0, 15));
  const updatedPayload = JSON.parse(updatedPayloadString);

  if (dryRun) {
    console.log('[DRY RUN] Skipping deployment - components that would be deployed:');
    componentSpecs.forEach(spec => {
      const extras = spec.names.length > 1 ? ` (also tracked via: ${spec.names.slice(1).join(', ')})` : '';
      console.log(`  - [${spec.type}] ${spec.id}${extras}`);
    });
    console.log(`[DRY RUN] Payload file: ${payloadPath}`);
    console.log('[OK] Step 5 completed (dry run)\n');
    return;
  }

  // Save backup
  const backupPath = payloadPath + '.backup';
  fs.writeFileSync(backupPath, JSON.stringify(originalPayload, null, 2));

  try {
    const orgDetails = getOrgDetails(orgAlias);
    const url = `${orgDetails.instanceUrl}/services/data/v62.0/actions/custom/flow/sfdatakit__DeployDataKitComponents`;

    // Capture the Salesforce server timestamp before triggering deploy so the
    // poller uses WHERE CreatedDate >= deploymentStartTime (immune to local clock-skew).
    let deploymentStartTime = '';
    try {
      deploymentStartTime = getMaxCreatedDate(orgAlias);
    } catch (_) {
      // If server-time query fails, fall back to no filter — better than crashing
    }

    const headerFile = path.join(os.tmpdir(), `sf-auth-${process.pid}.txt`);
    const bodyFile = path.join(os.tmpdir(), `sf-body-${process.pid}.json`);
    let response;
    try {
      fs.writeFileSync(headerFile, `Authorization: Bearer ${orgDetails.accessToken}\n`, { mode: 0o600 });
      fs.writeFileSync(bodyFile, JSON.stringify(updatedPayload), { mode: 0o600 });
      response = execFileSync(
        'curl',
        ['-s', '-X', 'POST', url, '--header', `@${headerFile}`, '-H', 'Content-Type: application/json', '--data', `@${bodyFile}`],
        { encoding: 'utf8' },
      );
    } finally {
      try { fs.unlinkSync(headerFile); } catch (e) { console.warn(`Warning: failed to delete auth header file ${headerFile}: ${e.message}`); }
      try { fs.unlinkSync(bodyFile); } catch (e) { console.warn(`Warning: failed to delete body file ${bodyFile}: ${e.message}`); }
    }

    const result = JSON.parse(response);
    console.log('Deployment initiated');

    if (result.isSuccess === false || result.errors) {
      console.error('Deployment API returned errors:', result);
      throw new Error('Deployment failed');
    }

    await waitForDeploymentCompletion(orgAlias, componentSpecs, deploymentStartTime, namespace);
  } finally {
    fs.writeFileSync(payloadPath, JSON.stringify(originalPayload, null, 2));
    fs.unlinkSync(backupPath);
  }
}

module.exports = deployTPMAccruals;
