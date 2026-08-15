import { chromium } from "playwright-core";
const browser = await chromium.connectOverCDP(process.env.GROK_CDP || "http://127.0.0.1:9222");
const ctx = browser.contexts()[0];
const pages = ctx.pages();
const imagine = pages.filter(p => /grok\.com\/imagine\/?(\?|$|#)/i.test(p.url()) && !/agent/i.test(p.url()));
const agent = pages.filter(p => /\/imagine\/agent/i.test(p.url()));
const other = pages.filter(p => !/grok\.com/i.test(p.url()));
console.log(JSON.stringify({
  total: pages.length,
  imagineTabs: imagine.map(p => p.url()),
  agentTabs: agent.length,
  otherTabs: other.map(p => p.url().slice(0,80)),
}, null, 2));
// Close surplus clean Imagine tabs (keep first)
for (let i = 1; i < imagine.length; i++) {
  await imagine[i].close().catch(()=>{});
  console.log("closed surplus imagine tab", i);
}
if (imagine[0]) {
  await imagine[0].bringToFront().catch(()=>{});
  console.log("kept", imagine[0].url());
}
