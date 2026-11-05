// "Invoicely": a tiny invoicing SaaS with deliberately planted first-run friction.
// Eval fixture for the ux-stress-test skill. Runs on plain Node, no dependencies:
//   node demo-app/server.mjs   (PORT defaults to 4173)
import http from 'node:http';
import { randomUUID } from 'node:crypto';

const PORT = Number(process.env.PORT ?? 4173);
const users = new Map(); // email -> { password, workspace, slug }
const sessions = new Map(); // sid -> email
const invoices = new Map(); // id -> { email, client, amount, due }

// Render-blocking "analytics bundle": ~300 KB of padding, never cached.
const vendorJs = `/* vendor bundle */\n${'// padding '.repeat(27000)}\nwindow.analytics = { ready: true };\n`;

const css = `
  body { font-family: system-ui, sans-serif; margin: 0; color: #222; }
  header, footer { display: flex; gap: 16px; align-items: center; padding: 12px 24px; background: #f4f4f8; }
  header .logo { font-weight: 700; margin-right: auto; }
  main { padding: 24px; }
  .card { width: 560px; margin: 32px auto; padding: 24px; border: 1px solid #ddd; border-radius: 8px; }
  .btn { display: inline-block; padding: 10px 16px; border-radius: 6px; background: #ddd; color: #222; text-decoration: none; border: 0; }
  .btn.primary { background: #4b3fe0; color: #fff; }
  input { display: block; width: 100%; margin: 8px 0; padding: 6px; font-size: 13px; box-sizing: border-box; }
  input[type=checkbox] { display: inline; width: auto; }
  .icon-btn { width: 20px; height: 20px; padding: 0; background: #4b3fe0; color: #fff; border: 0; border-radius: 4px; }
  .error { color: #c00; }
  .muted { color: #888; font-size: 12px; }
`;

const page = (title, body) => `<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title} · Invoicely</title>
<script src="/vendor.js"></script>
<style>${css}</style></head>
<body>${body}</body></html>`;

const landing = () => page('Invoices at warp speed', `
  <header><span class="logo">Invoicely</span><a class="btn" href="/demo">Book a demo</a><a href="/pricing">Pricing</a></header>
  <main>
    <h1>Invoices at warp speed</h1>
    <p>Invoicely streamlines your AR ops so you can stop chasing payments and start getting paid.</p>
    <a class="btn primary" href="/signup">Get the ball rolling</a>
  </main>
  <footer><a href="/terms">Terms</a><a href="/privacy">Privacy</a></footer>`);

const pricing = () => page('Pricing', `
  <header><a class="logo" href="/">Invoicely</a></header>
  <main><h1>Pricing</h1><h2>Pro — $9/month</h2><p>Free trial included.</p>
  <a class="btn primary" href="/signup">Start free trial</a></main>`);

const privacy = () => page('Privacy', `
  <main><h1>Privacy Policy</h1><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor
  incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation.</p></main>`);

const signup = (error = '') => page('Sign up', `
  <div class="card"><h1>Create your account</h1>
  <p class="muted">Pro plan: $12/month after your 14-day trial.</p>
  ${error && `<p class="error">${error}</p>`}
  <form method="post" action="/signup">
    <input name="email" placeholder="Email">
    <input name="password" type="password" placeholder="Password">
    <label><input type="checkbox" name="share" checked> Share my data with partners and send me offers</label>
    <p><button class="btn primary">Create account</button></p>
  </form></div>`);

const step1 = (error = '') => page('Set up', `
  <div class="card"><h1>Step 1 of 2: Provision your tenant slug</h1>
  ${error && `<p class="error">${error}</p>`}
  <form method="post" action="/onboarding/1">
    <input name="workspace" placeholder="Workspace name">
    <input name="slug" placeholder="tenant-slug">
    <button class="icon-btn">→</button>
  </form></div>`);

const step2 = () => page('First invoice', `
  <div class="card"><h1>Step 2 of 2: Create your first invoice</h1>
  <form method="post" action="/onboarding/2">
    <input name="client" placeholder="Client">
    <input name="amount" placeholder="Amount">
    <input name="due" placeholder="03/04/2026">
    <p><a href="/onboarding/1">← Back</a> <button class="btn primary">Let's go!</button></p>
  </form></div>`);

// Workspace and client names are interpolated unescaped on purpose.
const success = (user, invoice, id) => page('Done', `
  <div class="card"><h1>🎉 You're all set, ${user.workspace}!</h1>
  <p>Invoice ${id} for ${invoice.client} ($${invoice.amount}) is ready to send.</p></div>`);

const readForm = req => new Promise(resolve => {
  let body = '';
  req.on('data', chunk => { body += chunk; });
  req.on('end', () => resolve(Object.fromEntries(new URLSearchParams(body))));
});

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

const currentUser = req => {
  const sid = /(?:^|;\s*)sid=([^;]+)/.exec(req.headers.cookie ?? '')?.[1];
  const email = sessions.get(sid);
  return email && { email, ...users.get(email) };
};

async function handle(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const route = `${req.method} ${url.pathname}`;
  const html = (body, status = 200) => { res.writeHead(status, { 'content-type': 'text/html' }); res.end(body); };
  const redirect = (to, headers = {}) => { res.writeHead(303, { location: to, ...headers }); res.end(); };

  if (route === 'GET /vendor.js') {
    res.writeHead(200, { 'content-type': 'text/javascript', 'cache-control': 'no-store' });
    return res.end(vendorJs);
  }
  if (route === 'GET /') return html(landing());
  if (route === 'GET /pricing') return html(pricing());
  if (route === 'GET /privacy') return html(privacy());
  if (route === 'GET /signup') return html(signup());

  if (route === 'POST /signup') {
    const { email = '', password = '' } = await readForm(req);
    if (!/^[a-z0-9._-]+@[a-z0-9.-]+\.[a-z]{2,}$/.test(email) || password.length < 14) {
      return html(signup('Invalid input'), 400);
    }
    if (users.has(email)) throw new Error('UNIQUE constraint failed: users.email');
    users.set(email, { password });
    await sleep(800); // slow "provisioning", with no feedback in the UI
    const sid = randomUUID();
    sessions.set(sid, email);
    return redirect('/onboarding/1', { 'set-cookie': `sid=${sid}; Path=/; HttpOnly` });
  }

  const user = currentUser(req);
  if (url.pathname.startsWith('/onboarding') || url.pathname === '/success') {
    if (!user) return redirect('/signup');
  }

  if (route === 'GET /onboarding/1') return html(step1());
  if (route === 'POST /onboarding/1') {
    const { workspace = '', slug = '' } = await readForm(req);
    if (slug.length > 64) throw new RangeError(`slug exceeds column width (${slug.length})`);
    if (user.slug) return html(step1('Slug already taken'), 409);
    users.set(user.email, { ...users.get(user.email), workspace, slug });
    return redirect('/onboarding/2');
  }
  if (route === 'GET /onboarding/2') return html(step2());
  if (route === 'POST /onboarding/2') {
    const { client = '', amount = '', due = '' } = await readForm(req);
    const id = `INV-${String(invoices.size + 1).padStart(3, '0')}`;
    invoices.set(id, { email: user.email, client, amount: parseFloat(amount), due });
    return redirect(`/success?id=${id}`);
  }
  if (route === 'GET /success') {
    const id = url.searchParams.get('id');
    return html(success(user, invoices.get(id), id));
  }

  res.writeHead(404, { 'content-type': 'text/plain' });
  res.end(`Cannot ${req.method} ${url.pathname}`);
}

http.createServer((req, res) => {
  handle(req, res).catch(err => {
    res.writeHead(500, { 'content-type': 'text/plain' });
    res.end(err.stack);
  });
}).listen(PORT, () => console.log(`Invoicely on http://localhost:${PORT}`));
