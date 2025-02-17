import cv2
import imutils
import socket
import pickle
import struct
import time

# Adresse IP et port du serveur
HOST = '127.0.0.1'  # Adresse IP locale (vous pouvez la changer si nécessaire)
PORT = 8485

# Création du socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Capture vidéo
vid = cv2.VideoCapture(0)

while(vid.isOpened()):
    ret, frame = vid.read()
    if not ret:
        break

    frame = imutils.resize(frame, width=360)
    frame = cv2.flip(frame, 1)
    data = pickle.dumps(cv2.imencode('.jpg', frame)[1].tobytes(), 0)
    size = len(data)

    client_socket.sendall(struct.pack(">L", size) + data)

    time.sleep(0.01)

vid.release()
client_socket.close()
