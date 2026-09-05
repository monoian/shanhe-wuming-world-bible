/* Dependency-free static preview. Production is the checked-in HTML on GitHub Pages. */
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const args = process.argv.slice(2);
const arg = (key, fallback) => args.includes(key) ? args[args.indexOf(key) + 1] : fallback;
const port = Number(arg('--port', '4173'));
const host = arg('--host', '0.0.0.0');
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.webp': 'image/webp' };
http.createServer((req, res) => {
  let requestPath;
  try { requestPath = decodeURIComponent(new URL(req.url, 'http://localhost').pathname); }
  catch (_) { res.writeHead(400); res.end('Bad request'); return; }
  const file = path.resolve(root, '.' + requestPath + (requestPath.endsWith('/') ? 'index.html' : ''));
  if (!file.startsWith(root + path.sep) || requestPath.split('/').some(x => x === '.git' || x === 'node_modules')) {
    res.writeHead(403); res.end('Forbidden'); return;
  }
  fs.readFile(file, (err, bytes) => {
    if (err) { res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }); res.end('Not found'); return; }
    res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' });
    res.end(req.method === 'HEAD' ? undefined : bytes);
  });
}).listen(port, host, () => console.log(`Static guide ready on port ${port}`));
