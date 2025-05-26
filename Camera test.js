// Serveur (server.js)
const cv = require('opencv4nodejs');
const express = require('express');
const app = express();
const server = require('http').createServer(app);
const io = require('socket.io')(server);

app.get('/', (req, res) => res.sendFile(__dirname + '/index.html'));

io.on('connection', socket => {
  const vCap = new cv.VideoCapture(0);
  setInterval(() => {
    let frame = vCap.read();
    frame = frame.resize(320, 240);
    const image = cv.imencode('.jpg', frame).toString('base64');
    socket.emit('frame', image);
  }, 30);
});

server.listen(3000, () => console.log('Serveur démarré sur le port 3000'));

// Client (index.html)
<!DOCTYPE html>
<html>
<head>
  <title>Caméra distante</title>
</head>
<body>
  <img id="video" src="" />
  <script src="/socket.io/socket.io.js"></script>
  <script>
    const socket = io();
    const video = document.getElementById('video');
    socket.on('frame', image => {
      video.src = `data:image/jpeg;base64,${image}`;
    });
  </script>
</body>
</html>
