import logging
import socket
import select


logging.basicConfig(level=logging.INFO)

class EchoServer:
    def __init__(self, port):
        self.listen_socket = socket.socket()

        # so we dont sit on accept if we only have existing connections sending us data
        self.listen_socket.setblocking(False)

        # listen for connections on provided port
        self.listen_socket.bind(('0.0.0.0', port))

        # traditional windows value is 5: http://tangentsoft.net/wskfaq/advanced.html#backlog
        self.listen_socket.listen(1)

        # list of sockets ready to send to
        self.read_list = set()
        # list of sockets that we've got a full string from and are ready to send back
        self.write_list = set()

        # key: socket, value: pending data
        self.socket_data = {}

    def run(self):
        while(True):
            try:
                conn, address = self.listen_socket.accept()
            except BlockingIOError:
                # if there's nothing to accept dont care, cos existing connections might still have data
                pass
            else:
                logging.info('New connection: %s', conn.getpeername())
                self.read_list.add(conn)
                self.socket_data[conn] = b''

            # select errors on windows if all lists are empty so need to shortcut :(
            if not self.read_list and not self.write_list:
                continue

            readables, writeables, errorables = select.select(list(self.read_list), list(self.write_list), [], 0)

            if readables:
                logging.debug('read %s', [x.getpeername() for x in readables])
            if writeables:
                logging.debug('write %s', [x.getpeername() for x in writeables])

            for writeable in writeables:
                self.write_data(writeable)

            for readable in readables:
                self.read_data(readable)

    def write_data(self, writeable):
        received_data = self.socket_data[writeable]

        # slice received_data at the rightmost line feed - send everything before it
        last_lf = received_data.rfind(b'\n') + 1
        data_to_send = received_data[:last_lf]
        # the last element of the array will be incomplete (or empty bytestr which is fine too)
        self.socket_data[writeable] = received_data[last_lf:]
        logging.info('Sending %s to %s', data_to_send, writeable.getpeername())
        writeable.sendall(data_to_send)
        self.write_list.remove(writeable)

    def read_data(self, readable):
        try:
            inbound_data = readable.recv(4096)
            # sockets are readable but non-blocking return 0, see http://stackoverflow.com/a/5640189/2075437
            if len(inbound_data) == 0:
                raise ConnectionError('Socket closed')
        except ConnectionError:
            logging.info('Remote socket closed: %s', readable.getpeername())
            self.read_list.remove(readable)
            del self.socket_data[readable]
            readable.close()
        else:
            self.socket_data[readable] += inbound_data
            logging.debug('Received %s from %s', inbound_data, readable.getpeername())
            # if there's at least one
            if b'\n' in self.socket_data[readable]:
                self.write_list.add(readable)


if __name__ == '__main__':
    EchoServer(port=8000).run()
