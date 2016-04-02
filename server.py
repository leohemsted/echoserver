import socket
import select
from collections import defaultdict

# so we dont sit on accept if we only have existing connections sending us data
socket.setdefaulttimeout(0)

PORT = 8000


def main():
    listen_socket = socket.socket()

    # listen for connections on provided port
    listen_socket.bind(('0.0.0.0', PORT))

    listen_socket.listen(0)

    # list of sockets ready to send to
    read_list = set()
    # list of sockets that we've got a full string from and are ready to send back
    write_list = set()

    # key: socket, value: pending data
    pending_data = defaultdict(bytes)

    while(True):
        print('Waiting for connection')
        try:
            conn, address = listen_socket.accept()
        except socket.timeout:
            # if it times out dont care, just select from the list of known connections
            pass
        else:
            read_list.add(conn)


        # dont care about errors
        readables, writeables, errorables = select.select(list(read_list), list(write_list), [])

        for readable in readables:
            pending_data[readable] += readable.recv(4096)
            pending_data.split('\n')

        from pprint import pprint
        pprint(pending_data)


if __name__ == '__main__':
    main()
