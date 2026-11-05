// Lists the page's visible controls with a CSS selector and the viewport point to click.
// Usage (browser-use): print(js(open("<skill-dir>/scripts/controls.js").read()))
// inView false means scroll first; a person can't use what is off screen.
(() => {
  const name = el => (el.getAttribute('aria-label') || el.labels?.[0]?.innerText || el.innerText
    || el.getAttribute('placeholder') || el.value || el.getAttribute('title') || el.name || '').trim().slice(0, 50);
  const selector = el => el.id ? `#${CSS.escape(el.id)}`
    : el.name ? `${el.tagName.toLowerCase()}[name="${el.name}"]` : null;
  return [...document.querySelectorAll('a[href], button, input, select, textarea, summary, [role=button], [role=link], [role=checkbox], [role=tab]')]
    .filter(el => {
      const r = el.getBoundingClientRect();
      return el.type !== 'hidden' && r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden';
    })
    .map(el => {
      const r = el.getBoundingClientRect();
      return {
        control: el.tagName.toLowerCase() + (el.type && el.tagName === 'INPUT' ? `[${el.type}]` : ''),
        name: name(el), selector: selector(el),
        x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2),
        inView: r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth,
        ...(el.disabled && { disabled: true }), ...(el.checked && { checked: true }),
      };
    });
})()
