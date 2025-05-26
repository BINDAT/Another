# Serveur (camera_server.R)
library(imager)
library(sockets)

server <- socketServer(port = 8485, function(client) {
  cap <- VideoCapture(0)
  while (TRUE) {
    frame <- readFrame(cap)
    img <- im(frame)
    jpeg_data <- jpeg(img, quality = 80)
    client$write(as.integer(length(jpeg_data)), type = "integer")
    client$write(jpeg_data, type = "raw")
  }
})

# Client (camera_client.R)
library(imager)
library(sockets)

client <- socketClient("127.0.0.1", 8485)
while (TRUE) {
  size <- client$read(4, type = "integer")
  jpeg_data <- client$read(size, type = "raw")
  img <- load.image(jpeg_data, "jpeg")
  plot(img)
}
