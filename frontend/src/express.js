// server.js
const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(bodyParser.json());

app.post('/api/login', (req, res) => {
  const { account, passwd } = req.body;
  const userFilePath = path.join(__dirname, 'userdata', `${account}.json`);

  if (fs.existsSync(userFilePath)) {
    const userData = JSON.parse(fs.readFileSync(userFilePath, 'utf8'));
    if (userData.password === passwd) {
      res.json({ success: true, userData });
    } else {
      res.json({ success: false });
    }
  } else {
    res.json({ success: false });
  }
});

app.listen(5000, () => {
  console.log('Server is running on port 5000');
});
