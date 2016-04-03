"""
Sends some data, then just waits around for an hour
"""
import socket
import time

server_socket = socket.socket()

# listen for connections on provided port
server_socket.connect(('127.0.0.1', 8000))
server_socket.sendall(b'hello\n')
time.sleep(3600)
server_socket.close()
