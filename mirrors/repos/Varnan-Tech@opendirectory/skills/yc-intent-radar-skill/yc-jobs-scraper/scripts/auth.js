const { chromium } = require('playwright');
const fs = require('fs');

async function loginAndSaveSession() {
    console.log('Opening browser for login...');
    console.log('Please log in manually if you are not prompted.');
    
const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();

    console.log('Navigating to YC login page...');
    await page.goto('https://account.ycombinator.com/?continue=https://www.workatastartup.com/');

    console.log('\n--- ACTION REQUIRED ---');
    console.log('Please log in using your YC credentials in the browser window.');
    console.log('Waiting until you are redirected to the workatastartup.com dashboard...\n');

    await page.waitForURL('https://www.workatastartup.com/**', { timeout: 0 });

    console.log('Login successful! Saving session state...');
    
    await context.storageState({ path: 'state.json' });

    console.log('Session saved to state.json. You can now run the scraper!');
    await browser.close();
}

loginAndSaveSession().catch(console.error);
