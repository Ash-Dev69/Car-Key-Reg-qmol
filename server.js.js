const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;

// Target Local/Network Drive Path
const TARGET_DIR = 'U:\\Car Key register-Ashraf';
const TARGET_FILE = path.join(TARGET_DIR, 'Car_Key_Registry_Shared_Data.json');

const server = http.createServer((req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host}`);
  const pathname = parsedUrl.pathname;

  // 1. Serve your HTML file at the root route
  if (req.method === 'GET' && pathname === '/') {
    const htmlPath = path.join(__dirname, 'index.html_2.html');
    fs.readFile(htmlPath, (err, data) => {
      if (err) {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('HTML file not found');
      } else {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(data);
      }
    });
  } 
  // 2. API Endpoint to Read Data from U:\ drive
  else if (req.method === 'GET' && pathname === '/api/keys') {
    try {
      if (fs.existsSync(TARGET_FILE)) {
        const data = fs.readFileSync(TARGET_FILE, 'utf8');
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(data);
      } else {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ registry: [], nextNum: 0 }));
      }
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Failed to read from local drive' }));
    }
  } 
  // 3. API Endpoint to Write/Save Data directly to U:\ drive
  else if (req.method === 'POST' && pathname === '/api/keys') {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
    });
    req.on('end', () => {
      try {
        if (!fs.existsSync(TARGET_DIR)) {
          fs.mkdirSync(TARGET_DIR, { recursive: true });
        }
        fs.writeFileSync(TARGET_FILE, body, 'utf8');
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true, message: 'Saved successfully to targeted drive' }));
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Failed to write to local drive' }));
      }
    });
  } 
  else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT} (Using native Node.js)`);
});