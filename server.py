import logging
import socket
import select

# so we dont sit on accept if we only have existing connections sending us data
socket.setdefaulttimeout(0)

PORT = 8000

logging.basicConfig(level=logging.INFO)


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
    socket_data = {}

    while(True):
        try:
            conn, address = listen_socket.accept()
        except BlockingIOError:
            # if it times out dont care, just select from the list of known connections
            pass
        else:
            logging.info('New connection: %s', conn.getpeername())
            read_list.add(conn)
            socket_data[conn] = b''

        # select errors on windows if all lists are empty so need to shortcut :(
        if not read_list and not write_list:
            continue

        # dont care about errors
        readables, writeables, errorables = select.select(list(read_list), list(write_list), [], 0)
        if readables:
            logging.debug('read %s', [x.getpeername() for x in readables])
        if writeables:
            logging.debug('write %s', [x.getpeername() for x in writeables])

        for writeable in writeables:
            received_data = socket_data[writeable]

            # slice received_data at the rightmost line feed - send everything before it
            last_lf = received_data.rfind(b'\n')+1
            data_to_send = received_data[:last_lf]
            # the last element of the array will be incomplete (or empty bytestr which is fine too)
            socket_data[writeable] = received_data[last_lf:]
            logging.info('Sending %s to %s', data_to_send, writeable.getpeername())
            writeable.sendall(data_to_send)
            write_list.remove(writeable)

        for readable in readables:
            try:
                inbound_data = readable.recv(4096)
                socket_data[readable] += inbound_data
                logging.debug('Received %s from %s', inbound_data, readable.getpeername())

                # sockets are readable but non-blocking return 0, adapted from
                # http://stackoverflow.com/a/5640189/2075437
                if len(inbound_data) == 0:
                    raise ConnectionError('Socket closed')
            except ConnectionError:
                logging.info('Remote socket closed: %s', readable.getpeername())
                read_list.remove(readable)
                del socket_data[readable]
                readable.close()
            else:
                # if there's at least one
                if b'\n' in socket_data[readable]:
                    write_list.add(readable)



if __name__ == '__main__':
    main()
