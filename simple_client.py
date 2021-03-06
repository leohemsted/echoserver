"""
Sends 'hello\n' to server and expects to receive it back
"""
import socket

server_socket = socket.socket()

# listen for connections on provided port
server_socket.connect(('127.0.0.1', 8000))
server_socket.sendall(b'hello\n')
print(server_socket.recv(4096))
server_socket.close()
