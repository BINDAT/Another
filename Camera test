import cv2
import imutils
import socket
import pickle
import struct

# Adresse IP et port du serveur
HOST = '127.0.0.1'  # Adresse IP locale (vous pouvez la changer si nécessaire)
PORT = 8485

# Création du socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(10)
conn, addr = server_socket.accept()

data = b""
payload_size = struct.calcsize(">L")

while True:
    while len(data) < payload_size:
        data += conn.recv(4096)

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]

    while len(data) < msg_size:
        data += conn.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    cv2.imshow('Camera distante', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

conn.close()
cv2.destroyAllWindows()
