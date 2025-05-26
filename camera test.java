// Serveur (CameraServer.java)
import java.io.*;
import java.net.*;
import org.opencv.core.Mat;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.videoio.VideoCapture;

public class CameraServer {
  public static void main(String[] args) throws IOException {
    ServerSocket serverSocket = new ServerSocket(8485);
    Socket clientSocket = serverSocket.accept();
    OutputStream out = clientSocket.getOutputStream();

    System.loadLibrary(org.opencv.core.Core.NATIVE_LIBRARY_NAME);
    VideoCapture vCap = new VideoCapture(0);

    while (true) {
      Mat frame = new Mat();
      vCap.read(frame);
      Imgcodecs.imencode(".jpg", frame, buffer);
      byte[] imageBytes = buffer.array();
      out.write(imageBytes);
    }
  }
}

// Client (CameraClient.java)
import java.io.*;
import java.net.*;
import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;

public class CameraClient {
  public static void main(String[] args) throws IOException {
    Socket socket = new Socket("127.0.0.1", 8485);
    InputStream in = socket.getInputStream();

    while (true) {
      BufferedImage image = ImageIO.read(in);
      // Afficher l'image dans une fenêtre
    }
  }
}
