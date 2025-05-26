// Serveur (camera_server.d)
import std.stdio;
import std.socket;
import std.concurrency;
import opencv;

void main() {
  auto server = new TcpListener(8485);
  server.start();

  while (true) {
    auto client = server.accept();
    auto capture = new VideoCapture(0);

    while (true) {
      Mat frame;
      capture.read(frame);
      auto jpegData = imencode(".jpg", frame);
      client.send(jpegData.length);
      client.send(jpegData);
    }
  }
}

// Client (camera_client.d)
import std.stdio;
import std.socket;
import std.concurrency;
import opencv;

void main() {
  auto client = new TcpSocket("127.0.0.1", 8485);
  client.connect();

  while (true) {
    int size;
    client.receive(size);
    auto jpegData = new ubyte[size];
    client.receive(jpegData);
    auto frame = imdecode(jpegData, IMREAD_COLOR);
    // Afficher l'image
  }
}
