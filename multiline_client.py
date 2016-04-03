"""
Sends two lines of data (with a hiccup halfway through the second line)
"""
import socket
import time

server_socket = socket.socket()

# listen for connections on provided port
server_socket.connect(('127.0.0.1', 8000))
server_socket.sendall(b'hello\nwor')
time.sleep(2)
server_socket.sendall(b'ld\n')
# make sure server has processed
time.sleep(1)
print(server_socket.recv(4096))
server_socket.close()
