// Throttles a playwright-cli session (Chromium only) to Chrome DevTools' "Slow 3G" preset:
// 2 s latency, 400 kbit/s each way. It covers every open page and every page opened later.
// Usage: playwright-cli -s=<session> run-code --filename=<skill-dir>/scripts/slow-3g.js
async page => {
  const conditions = { offline: false, latency: 2000, downloadThroughput: 50000, uploadThroughput: 50000 };
  const throttle = async p => {
    const cdp = await p.context().newCDPSession(p);
    await cdp.send('Network.emulateNetworkConditions', conditions);
  };
  const context = page.context();
  await Promise.all(context.pages().map(throttle));
  context.on('page', throttle);
  return `slow 3G applied to ${context.pages().length} page(s) and future tabs`;
}
