const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const {
  exec,
  getOrgDetails,
  getMaxCreatedDate,
  getDeploymentLogForComponents,
  getDeployedComponents,
  waitForDeploymentCompletion,
} = require('./utils');

/**
 * Build component specs (id + names to match in DataKitDeploymentLog) for each
 * component in a deployment payload.
 */
function buildComponentSpecs(payload) {
  const specs = [];

  const components =
    payload && payload.inputs && payload.inputs[0] && payload.inputs[0].dataKitComponentsInput
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
      specs.push({
        id: component.bundleConfig.bundleName,
        type: 'DataStreamBundle',
        names: [component.bundleConfig.bundleName].filter(Boolean),
      });
    }
  });

  return specs;
}

/**
 * Step 4: Deploy Liability Accruals Engine data kit
 * @param {string} orgAlias - The Salesforce org alias
 * @param {string} scriptsDir - Path to the scripts directory
 * @param {string} orgId - The Salesforce org ID
 * @param {string} namespace - Org namespace prefix (e.g. "cgcloud_dev__"), or '' for unmanaged orgs
 * @param {boolean} dryRun - If true, skip actual deployment
 */
async function deployEngine(orgAlias, scriptsDir, orgId, namespace = '', dryRun = false) {
  console.log('\n=== Step 4: Deploying Liability Accruals Engine ===');

  const dataKitName = 'LiabilityAccrualsEngine';
  const payloadPath = path.join(scriptsDir, 'engine-deployment-payload.json');

  console.log(`Payload: ${payloadPath}`);

  if (namespace) {
    console.log(`Org namespace: ${namespace}`);
  }

  const payload = JSON.parse(fs.readFileSync(payloadPath, 'utf8'));
  const originalPayload = JSON.parse(JSON.stringify(payload));
  const allComponentSpecs = buildComponentSpecs(payload);
  const deploymentLog = getDeploymentLogForComponents(orgAlias, allComponentSpecs);
  const deployedIds = getDeployedComponents(deploymentLog, allComponentSpecs, namespace);

  if (deployedIds.size > 0) {
    console.log(`Found ${deployedIds.size} already deployed components:`);
    deployedIds.forEach(comp => console.log(`  - ${comp}`));
  }

  const components = payload.inputs[0].dataKitComponentsInput;
  const componentsToSkip = new Set();

  components.forEach((component, index) => {
    let identifier = '';

    if (component.dloConfig) {
      identifier = component.dloConfig.apiName;
    } else if (component.dataTransformConfig) {
      identifier =
        component.dataTransformConfig.apiName || component.dataTransformConfig.dataTransformDevName;
    } else if (component.bundleConfig) {
      identifier = component.bundleConfig.bundleName;
    }

    if (identifier && deployedIds.has(identifier)) {
      componentsToSkip.add(index);
    }
  });

  if (componentsToSkip.size > 0) {
    console.log(`Skipping ${componentsToSkip.size} already deployed components`);
    payload.inputs[0].dataKitComponentsInput = components.filter(
      (_, index) => !componentsToSkip.has(index),
    );
  }

  const componentCount = payload.inputs[0].dataKitComponentsInput.length;

  if (componentCount === 0) {
    console.log(`[OK] All components already deployed, skipping ${dataKitName}\n`);
    return;
  }

  console.log(`${dryRun ? 'Would deploy' : 'Deploying'} ${componentCount} components...`);

  const componentSpecs = buildComponentSpecs(payload);
  const payloadString = JSON.stringify(payload);
  const updatedPayloadString = payloadString.replace(/<SF_ORG_ID>/g, orgId.slice(0, 15));
  const updatedPayload = JSON.parse(updatedPayloadString);

  if (dryRun) {
    console.log('[DRY RUN] Skipping deployment - components that would be deployed:');
    componentSpecs.forEach(spec => console.log(`  - [${spec.type}] ${spec.id}`));
    console.log(`[DRY RUN] Payload file: ${payloadPath}`);
    console.log('[OK] Step 4 completed (dry run)\n');
    return;
  }

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
      fs.writeFileSync(
        headerFile,
        `Authorization: Bearer ${orgDetails.accessToken}\n`,
        { mode: 0o600 },
      );
      fs.writeFileSync(bodyFile, JSON.stringify(updatedPayload), { mode: 0o600 });
      response = execFileSync(
        'curl',
        [
          '-s',
          '-X',
          'POST',
          url,
          '--header',
          `@${headerFile}`,
          '-H',
          'Content-Type: application/json',
          '--data',
          `@${bodyFile}`,
        ],
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
    try {
      fs.unlinkSync(backupPath);
    } catch (_) {}
  }
}

module.exports = deployEngine;
