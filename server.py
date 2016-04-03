import time
import socket
import select
from collections import defaultdict

# so we dont sit on accept if we only have existing connections sending us data
socket.setdefaulttimeout(1)

PORT = 8000


def main():
    listen_socket = socket.socket()

    # listen for connections on provided port
    listen_socket.bind(('0.0.0.0', PORT))

    listen_socket.listen(1)

    # list of sockets ready to send to
    read_list = set()
    # list of sockets that we've got a full string from and are ready to send back
    write_list = set()

    # key: socket, value: pending data
    socket_data = defaultdict(bytes)

    while(True):
        try:
            conn, address = listen_socket.accept()
        except socket.timeout:
            # if it times out dont care, just select from the list of known connections
            pass
        else:
            print('New connection:', conn.getpeername())
            read_list.add(conn)

        # select errors on windows if all lists are empty so need to shortcut :(
        if not read_list and not write_list:
            # clumsy way to avoid thrashing
            time.sleep(1)
            continue

        # dont care about errors
        readables, writeables, errorables = select.select(list(read_list), list(write_list), [])
        print('read', [x.getpeername() for x in readables])
        print('write', [x.getpeername() for x in writeables])

        for readable in readables:
            print('receiving from', readable.getpeername())
            try:
                socket_data[readable] += readable.recv(4096)
                from pprint import pprint; pprint(socket_data)
            except ConnectionError as cre:
                print('Remote socket closed:', readable.getpeername())
                read_list.remove(readable)
                readable.close()

            # if there's at least one
            if b'\n' in socket_data[readable]:
                write_list.add(readable)

        for writeable in writeables:
            received_data = socket_data[writeable]

            # slice received_data at the rightmost line feed - send everything before it
            last_lf = received_data.rfind(b'\n')+1
            data_to_send = received_data[:last_lf]
            # the last element of the array will be incomplete (or empty bytestr which is fine too)
            socket_data[writeable] = received_data[last_lf:]
            print('sending', data_to_send, 'to', writeable.getpeername())
            writeable.sendall(data_to_send)
            write_list.remove(writeable)


if __name__ == '__main__':
    main()
