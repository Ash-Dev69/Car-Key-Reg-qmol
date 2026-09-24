const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// In-memory data store for the server API sync
let serverData = {
  registry: [],
  nextNum: 1
};

app.use(express.json({ limit: '10mb' }));
app.use(express.static(path.join(__dirname)));

// API endpoints used by your frontend code
app.get('/api/keys', (req, res) => {
  res.json(serverData);
});

app.post('/api/keys', (req, res) => {
  if (req.body && req.body.registry) {
    serverData.registry = req.body.registry;
    serverData.nextNum = req.body.nextNum || serverData.nextNum;
    res.json({ success: true });
  } else {
    res.status(400).json({ error: 'Invalid data payload' });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running! Access your app at: http://localhost:${PORT}`);
});