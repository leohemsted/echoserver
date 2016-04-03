"""
Connects, but never sends anything. Closes after a minute
"""
import socket
import time

server_socket = socket.socket()

# listen for connections on provided port
server_socket.connect(('127.0.0.1', 8000))
time.sleep(60)
server_socket.close()
