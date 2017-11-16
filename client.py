from socket import socket, timeout


class FtpClient(object):
    """
    FTP client that can be used for both non-secure and secure connections.

    Attributes:
    host (str): The host to which the client is connected to, if connected,
                None otherwise.
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
                  .format(self.host, FtpClient.PORT))
            self._socket.close()
        self._socket = socket()
        self._socket.settimeout(FtpClient.SOCKET_TIMEOUT_SECONDS)
        self.host = None

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

        if self.host is not None:
            self._reset_socket(drop_existing=True)
            return self.connect(host)

        try:
            print 'Connecting to {}:{}'.format(host, FtpClient.PORT)
            self._socket.connect((host, FtpClient.PORT))
            self.host = host
        except timeout:
            raise FtpClient.TimeoutException(host)

        data = self._socket.recv(FtpClient.SOCKET_RCV_BYTES)
        return data
