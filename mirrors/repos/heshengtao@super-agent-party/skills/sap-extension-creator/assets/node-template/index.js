/**
 * SAP Extension — Node.js Template
 * 
 * Supports both:
 * 1. Node service mode:  node index.js <port>  (managed by SAP)
 * 2. Static file mode:   node index.js         (open index.html in browser)
 */
const path = require('path');
const fs = require('fs');
const EXT_DIR = __dirname;
const HTML_FILE = path.join(EXT_DIR, 'index.html');

/* ---- Mode 1: Node service (SAP-managed) ---- */
if (process.argv[2]) {
  const PORT = parseInt(process.argv[2], 10);
  const express = require('express');
  const app = express();

  // Serve all static assets from extension directory
  app.use(express.static(EXT_DIR));

  // Root → index.html
  app.get('/', (req, res) => res.sendFile(HTML_FILE));

  // Health check for SAP readiness polling
  app.get('/health', (req, res) => res.json({ status: 'ok' }));

  // TODO: Add custom API routes here
  // app.get('/api/data', (req, res) => { ... });

  app.listen(PORT, '127.0.0.1', () => {
    const msg = `[ext] Node service ready at http://127.0.0.1:${PORT}`;
    console.log(msg);
    fs.writeFileSync(path.join(EXT_DIR, 'port.log'), String(PORT));
  });
  return;
}

/* ---- Mode 2: Standalone / double-click ---- */
const { spawn } = require('child_process');
const BROWSER = process.platform === 'darwin' ? 'open'
              : process.platform === 'win32' ? 'start'
              : 'xdg-open';
spawn(BROWSER, [HTML_FILE], { shell: true, stdio: 'ignore' });
console.log('[ext] Opening in browser:', HTML_FILE);
