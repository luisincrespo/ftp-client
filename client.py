import socket


class FtpClient(object):
    """
    FTP client that can be used for both non-secure and secure connections.

    Attributes:
    host (str): The host to which the client is connected to, if connected,
                None otherwise.
    """

    class TimeoutException(socket.timeout):
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

    class NotConnectedException(Exception):
        """
        Exception raised when FTP(S) commands are performed but the client
        is not currently connected to a host.
        """
        def __init__(self):
            super(FtpClient.NotConnectedException, self).__init__()
            self.msg = 'Not connected.'

    class NotAuthenticatedException(Exception):
        """
        Exception raised when FTP(S) commands are performed but the client
        is not currently authenticated for a user in the host.
        """
        def __init__(self):
            super(FtpClient.NotAuthenticatedException, self).__init__()
            self.msg = 'Not authenticated.'

    class AuthenticationException(Exception):
        """
        Exception raised when an authentication in the FTP(S) host fails.
        """
        def __init__(self):
            super(FtpClient.AuthenticationException, self).__init__()
            self.msg = 'Authentication failed.'

    PORT = 21
    SOCKET_TIMEOUT_SECONDS = 5
    SOCKET_RCV_BYTES = 4096

    LIST_COMMAND = 'LIST'
    USER_COMMAND = 'USER'
    PASS_COMMAND = 'PASS'

    def __init__(self):
        self._reset_socket()

    def _reset_socket(self, drop_existing=False):
        if drop_existing:
            print('Dropping existing connection to {}:{}'
                  .format(self.host, FtpClient.PORT))
            self._socket.close()
        self._socket = socket.socket()
        self._socket.settimeout(FtpClient.SOCKET_TIMEOUT_SECONDS)
        self.host = None
        self.user = None

    def _send_command(self, command, *args):
        for a in args:
            command = '{} {}'.format(command, a)
        try:
            self._socket.sendall('{}\r\n'.format(command))
        except socket.timeout:
            raise FtpClient.TimeoutException(self.host)

    def _receive_data(self):
        return self._socket.recv(FtpClient.SOCKET_RCV_BYTES)

    def _check_is_connected(self):
        if self.host is None:
            raise FtpClient.NotConnectedException()

    def _check_is_authenticated(self):
        if self.user is None:
            raise FtpClient.NotAuthenticatedException()

    def connect(self, host=None):
        """
        Connect to an FTP(S) server in the specified host.

        Args:
            host (str): The host to connect to. Falsy values
                        default to `localhost`. (Optional)

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
        except socket.timeout:
            raise FtpClient.TimeoutException(host)

        return self._receive_data()

    def login(self, user, password):
        """
        Login with specified user and password on the connected host.

        Args:
            user (str): The user.
            password (str): The password.

        Returns:
            The success message from the host if successful.
        """
        self._check_is_connected()

        self._send_command(FtpClient.USER_COMMAND, user)
        self._receive_data()

        self._send_command(FtpClient.PASS_COMMAND, password)
        data = self._receive_data()

        if data.startswith('530'):
            raise FtpClient.AuthenticationException()

        self.user = user
        return data

    def list(self, filename=None):
        """
        Perform LIST command on connected host.

        Args:
            filename (str): Name of file or directory to retrieve info
                            for. (Optional)

        Returns:
            Information about the specified file or directory, or the current
            directory if not specified.
        """
        self._check_is_connected()
        self._check_is_authenticated()

        if filename is not None:
            self._send_command(FtpClient.LIST_COMMAND, filename)
        else:
            self._send_command(FtpClient.LIST_COMMAND)

        return self._receive_data()
