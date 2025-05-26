# Serveur (camera_server.rb)
require 'socket'
require 'opencv'

server = TCPServer.new('127.0.0.1', 8485)
client = server.accept

# ... (code pour la capture vidéo avec OpenCV et l'envoi des données)

# Client (camera_client.rb)
require 'socket'
require 'opencv'

socket = TCPSocket.new('127.0.0.1', 8485)

# ... (code pour la réception des données et l'affichage avec OpenCV)
