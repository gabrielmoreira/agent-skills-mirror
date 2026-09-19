const os = require('os');
const fs = require('fs');
const path = require('path');
const { exec, execDeployJson, execSfJson } = require('./utils');

/**
 * Step 3: Deploy TPM Accruals Data Kit metadata to the org
 * @param {string} orgAlias - The Salesforce org alias
 * @param {string} dataKitPath - Path to the data kit
 * @param {boolean} dryRun - If true, skip actual deployment
 */
async function deployMetadata(orgAlias, dataKitPath, dryRun = false) {
  console.log('\n=== Step 3: Deploying TPM Accruals Data Kit ===');
  console.log(`Source: ${dataKitPath}`);
  console.log(`Target org: ${orgAlias}`);

  if (dryRun) {
    console.log('[DRY RUN] Skipping deployment - files prepared at:');
    console.log(`  ${dataKitPath}/force-app`);
    console.log('[OK] Step 3 completed (dry run)\n');
    return;
  }

  // Convert to MDAPI format first, then deploy via --metadata-dir.
  // This bypasses SF CLI source-tracking ("NothingToDeploy" errors on non-scratch
  // orgs where tracking state diverges from org reality).
  const mdapiOut = path.join(os.tmpdir(), `tpm_accruals_mdapi_${Date.now()}`);
  console.log('Converting source to MDAPI format...');
  const convertResult = execSfJson(['project', 'convert', 'source', '--output-dir', mdapiOut, '--json'], { cwd: dataKitPath });
  if (convertResult.status !== 0) {
    throw new Error(`Source conversion failed: ${convertResult.message || JSON.stringify(convertResult)}`);
  }
  console.log(`Converted to: ${convertResult.result && convertResult.result.location || mdapiOut}`);

  console.log('Deploying metadata...');
  execDeployJson(['project', 'deploy', 'start', '--metadata-dir', mdapiOut, '--target-org', orgAlias]);

  // Clean up temp dir
  try { fs.rmSync(mdapiOut, { recursive: true }); } catch (cleanupErr) {
    console.warn(`[WARN] Could not remove temp directory ${mdapiOut}: ${cleanupErr.message}`);
  }

  console.log('[OK] TPM Accruals Data Kit deployed successfully\n');
}

module.exports = deployMetadata;
