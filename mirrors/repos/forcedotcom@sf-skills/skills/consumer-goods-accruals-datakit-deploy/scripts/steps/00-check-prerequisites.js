const readline = require('readline');

/**
 * Step 0: Check Prerequisites
 * Presents prerequisites to the user and waits for confirmation
 */
async function checkPrerequisites() {
  console.log('\n=== Step 0: Prerequisites ===');

  console.log('\nBefore proceeding, confirm ALL of the following are complete in your org.\n');

  console.log('--- PERMISSIONS ---');
  console.log('\n1. Assign permission set "Data Cloud Architect" to:');
  console.log('   - The System Admin user');
  console.log('   - The user assigned to the Accrual Ingestion Process');
  console.log('\n2. Enable CRM Analytics (if you need Accruals dashboards):');
  console.log('   Setup > Feature Settings > Analytics > Analytics > Getting Started > Enable CRM Analytics');
  console.log('   Then assign permission set "CRM Analytics Plus Admin" to the System Admin.');

  console.log('\n--- DATA CLOUD ---');
  console.log('\n3. Data Cloud is enabled and set up (via the Data Cloud app, not Setup).');
  console.log('\n4. Salesforce CRM connector is active:');
  console.log('   Data Cloud app > Data Cloud Setup > Salesforce CRM > enable Home Org connection.');
  console.log('   Also activate any other required connectors using the dropdown button.');
  console.log('\n5. A user is assigned to the Accrual Ingestion Process:');
  console.log('   Setup > Processing Services Pairing > Accrual Ingestion Process.');

  console.log('\n--- INTEGRATION ---');
  console.log('\n6. OAuth scope "cdp_ingest_api" is configured on the integration app used by TPM Offcore.');
  console.log('   Check Setup > App Manager (Connected Apps) or Setup > External Client Apps.');
  console.log('   The app name varies by org — locate the one used by TPM Offcore.');

  console.log('\n');

  // Wait for user confirmation
  await waitForUserConfirmation();

  console.log('[OK] Prerequisites confirmed. Proceeding to next step...\n');
}

/**
 * Wait for user to press Enter.
 * Auto-confirms immediately when stdin is not a TTY (piped / headless run).
 */
function waitForUserConfirmation() {
  if (!process.stdin.isTTY) {
    console.log('[Auto-confirmed: running non-interactively]');
    return Promise.resolve();
  }
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    rl.question('Press Enter when you have confirmed all prerequisites are met...', () => {
      rl.close();
      resolve();
    });
  });
}

module.exports = checkPrerequisites;
