import errno
from socket import socket, error, timeout


class FtpClient(object):
    """
    FTP client that can be used for both non-secure and secure connections.
    """

    class TimeoutException(timeout):
        """
        Exception raised when the FTP client socket connection has timed out.

        Args:
        host (str): Host for which the connection timed out.

        Attributes:
        msg (str): Human readable string describing the exception.
        """
        def __init__(self, host):
            super(FtpClient.TimeoutException, self).__init__()
            self.msg = 'Connection to {}:{} timed out'.format(host,
                                                              FtpClient.PORT)

    PORT = 21
    SOCKET_TIMEOUT_SECONDS = 5
    SOCKET_RCV_BYTES = 4096

    def __init__(self):
        self._reset_socket()

    def _reset_socket(self, drop_existing=False):
        if drop_existing:
            print('Dropping existing connection to {}:{}'
                  .format(*self._socket.getpeername()))
            self._socket.close()
        self._socket = socket()
        self._socket.settimeout(FtpClient.SOCKET_TIMEOUT_SECONDS)

    def connect(self, host):
        """Connect to an FTP(S) server in the specified host.

        Args:
            host (str): The host to connect to. If a falsy
                        value is passed it defaults to
                        `localhost`.

        Returns:
            The welcome message from the host if successful.
        """
        host = host or 'localhost'
        try:
            print 'Connecting to {}:{}'.format(host, FtpClient.PORT)
            self._socket.connect((host, FtpClient.PORT))
        except timeout:
            raise FtpClient.TimeoutException(host)
        except error as (number, string):
            if number == errno.EISCONN:
                self._reset_socket(drop_existing=True)
                self.connect(host)

        data = self._socket.recv(FtpClient.SOCKET_RCV_BYTES)
        return data
