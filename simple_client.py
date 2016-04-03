import socket

server_socket = socket.socket()

# listen for connections on provided port
server_socket.connect(('127.0.0.1', 8000))
server_socket.sendall(b'hello\n')
data = server_socket.recv(4096)
print('Received', repr(data))
server_socket.close()
