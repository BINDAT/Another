// Serveur (CameraServer.cs)
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Net;
using System.Net.Sockets;
using System.Runtime.InteropServices;
using OpenCvSharp;

public class CameraServer
{
    public static void Main(string[] args)
    {
        TcpListener server = new TcpListener(IPAddress.Any, 8485);
        server.Start();
        TcpClient client = server.AcceptTcpClient();
        NetworkStream stream = client.GetStream();

        VideoCapture capture = new VideoCapture(0);

        while (true)
        {
            Mat frame = new Mat();
            capture.Read(frame);

            byte[] imageData = ImageToBytes(frame);
            byte[] sizeData = BitConverter.GetBytes(imageData.Length);
            stream.Write(sizeData, 0, sizeData.Length);
            stream.Write(imageData, 0, imageData.Length);
        }
    }

    private static byte[] ImageToBytes(Mat image)
    {
        using (var memoryStream = new System.IO.MemoryStream())
        {
            image.ToBitmap().Save(memoryStream, ImageFormat.Jpeg);
            return memoryStream.ToArray();
        }
    }
}

// Client (CameraClient.cs)
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Net.Sockets;
using OpenCvSharp;

public class CameraClient
{
    public static void Main(string[] args)
    {
        TcpClient client = new TcpClient("127.0.0.1", 8485);
        NetworkStream stream = client.GetStream();

        while (true)
        {
            byte[] sizeData = new byte[4];
            stream.Read(sizeData, 0, sizeData.Length);
            int size = BitConverter.ToInt32(sizeData, 0);

            byte[] imageData = new byte[size];
            stream.Read(imageData, 0, imageData.Length);

            Image image = BytesToImage(imageData);
            // Afficher l'image dans une fenêtre
        }
    }

    private static Image BytesToImage(byte[] bytes)
    {
        using (var memoryStream = new System.IO.MemoryStream(bytes))
        {
            return Image.FromStream(memoryStream);
        }
    }
}
