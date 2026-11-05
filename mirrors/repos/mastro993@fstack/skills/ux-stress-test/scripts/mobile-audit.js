// Measures what a small screen hides from the DOM: overflow, small targets, iOS-zooming inputs, blank time.
// Usage (browser-use): print(js(open("<skill-dir>/scripts/mobile-audit.js").read()))
// Usage (playwright-cli): playwright-cli -s=<session> --raw eval "$(cat <skill-dir>/scripts/mobile-audit.js)"
// Widths are compared against screen.width: when content is too wide, mobile Chrome zooms the
// whole page out to fit it, so window.innerWidth grows and hides the overflow.
(() => {
  const deviceWidth = screen.width;
  const isVisible = el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden';
  };
  const describe = el => {
    const name = el.getAttribute('aria-label') || el.labels?.[0]?.innerText || el.getAttribute('placeholder')
      || el.innerText || el.name || '';
    return `${el.tagName.toLowerCase()} "${name.trim().slice(0, 40)}"`;
  };
  const controls = [...document.querySelectorAll('a[href], button, input, select, textarea, [role=button]')]
    .filter(el => el.type !== 'hidden' && isVisible(el));
  const fields = controls.filter(el => ['INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName));
  const nav = performance.getEntriesByType('navigation')[0];
  const fcp = performance.getEntriesByName('first-contentful-paint')[0];
  return {
    deviceWidth,
    pageWidth: document.documentElement.scrollWidth,
    zoomedOutToFit: window.innerWidth > deviceWidth,
    controlsPastDeviceEdge: controls.filter(el => el.getBoundingClientRect().right > deviceWidth + 1).map(describe),
    tapTargetsUnder24px: controls.filter(el => {
      const r = el.getBoundingClientRect();
      return r.width < 24 || r.height < 24;
    }).map(describe),
    inputsUnder16px: fields.filter(el => parseFloat(getComputedStyle(el).fontSize) < 16).map(describe),
    firstContentfulPaintMs: fcp ? Math.round(fcp.startTime) : null,
    pageLoadMs: nav ? Math.round(nav.loadEventEnd) : null,
  };
})()
