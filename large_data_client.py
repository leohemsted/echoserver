"""
Sends a 5kb message
"""
import socket

server_socket = socket.socket()

# listen for connections on provided port
server_socket.connect(('127.0.0.1', 8000))
server_socket.sendall(b'hello' * 1000 + b'\n')
data = server_socket.recv(4096)
server_socket.close()
