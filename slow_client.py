"""
Waits two seconds between sending each character
"""
import socket
import time

server_socket = socket.socket()

# listen for connections on provided port
server_socket.connect(('127.0.0.1', 8000))
for c in b'hello\n':
    time.sleep(1)
    server_socket.sendall(bytes([c]))
server_socket.close()
