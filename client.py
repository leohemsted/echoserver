import socket
import time


IP = '127.0.0.1'
PORT = 8000

server_socket = socket.socket()

# listen for connections on provided port
server_socket.connect((IP, PORT))
print('connected, snoozing')
time.sleep(5)
server_socket.sendall(b'Hello,')
print('sent first bit, snoozing')
time.sleep(5)
server_socket.sendall(b' World\n')
print('sent last bit')
data = server_socket.recv(4096)
server_socket.close()
print('Received', repr(data))
