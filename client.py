import errno
from socket import socket, error


class FtpClient(object):
    def __init__(self):
        self._socket = socket()

    def _reset_socket(self):
        print('Disconnecting from {}'
              .format(self._socket.getpeername()))
        self._socket.close()
        self._socket = socket()

    def connect(self, host='localhost'):
        print 'Connecting to {}'.format(host)
        try:
            self._socket.connect((host, 21))
        except error as (number, string):
            if number == errno.EISCONN:
                self._reset_socket()
                self._socket.connect((host, 21))
        data = self._socket.recv(4096)
        return repr(data)
