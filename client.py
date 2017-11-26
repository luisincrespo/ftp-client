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

    PORT = 21
    SOCKET_TIMEOUT_SECONDS = 5
    SOCKET_RCV_BYTES = 4096

    LIST_COMMAND = 'LIST'
    USER_COMMAND = 'USER'
    PASS_COMMAND = 'PASS'
    EPRT_COMMAND = 'EPRT'
    QUIT_COMMAND = 'QUIT'

    def __init__(self, debug=False):
        self._debug = debug
        self._reset_sockets()

    def _reset_sockets(self, drop_existing=False):
        if drop_existing:
            self._command_socket.close()
            self._data_socket.close()
        self._command_socket = socket.socket()
        self._command_socket.settimeout(FtpClient.SOCKET_TIMEOUT_SECONDS)
        self.host = None
        self.user = None
        self._data_socket = socket.socket()
        self._data_connection = None

    def _log(self, info):
        if self._debug:
            print('debug: {}'.format(info))

    def _send_command(self, command, *args):
        for a in args:
            command = '{} {}'.format(command, a)
        try:
            self._log('sending command - {}'.format(command))
            self._command_socket.sendall('{}\r\n'.format(command))
        except socket.timeout:
            raise FtpClient.TimeoutException(self.host)

    def _receive_data(self, data_connection=False):
        if data_connection:
            data = self._data_connection.recv(FtpClient.SOCKET_RCV_BYTES)
        else:
            data = self._command_socket.recv(FtpClient.SOCKET_RCV_BYTES)
        self._log('received data - {}'.format(data))
        return data

    def _check_is_connected(self):
        if self.host is None:
            raise FtpClient.NotConnectedException()

    def _check_is_authenticated(self):
        if self.user is None:
            raise FtpClient.NotAuthenticatedException()

    def _open_data_socket(self):
        self._data_address, self._data_port = \
            self._command_socket.getsockname()
        self._data_port = self._data_port + 1
        self._data_socket.bind(('', self._data_port))
        self._data_socket.listen(1)

    def _open_data_connection(self):
        if self._data_connection is None:
            self._open_data_socket()
        self._send_command(FtpClient.EPRT_COMMAND, '|1|{}|{}|'
                           .format(self._data_address, self._data_port))
        self._data_connection, address = self._data_socket.accept()
        self._log('opened data connection on {}'.format(address))
        data = self._receive_data()
        return data

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
            self._reset_sockets(drop_existing=True)
            return self.connect(host)

        try:
            self._command_socket.connect((host, FtpClient.PORT))
            self.host = host
        except socket.timeout:
            self._reset_sockets(drop_existing=True)
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

        if data.startswith('230'):
            self.user = user
        elif data.startswith('530'):
            self.user = None

        return data

    def logout(self):
        """
        Clear info about currently logged user on connected host.
        """
        self._check_is_connected()
        self._check_is_authenticated()
        self.user = None

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

        data = self._open_data_connection()

        if filename is not None:
            self._send_command(FtpClient.LIST_COMMAND, filename)
        else:
            self._send_command(FtpClient.LIST_COMMAND)

        list_data = self._receive_data()
        data = data + list_data

        if not list_data.startswith('550'):
            data = data + self._receive_data(data_connection=True)
            data = data + self._receive_data()

        return data

    def disconnect(self):
        """
        Perform QUIT command (disconnect) on connected host.

        Returns:
            Good bye message from host if connected.
        """
        self._check_is_connected()

        self._send_command(FtpClient.QUIT_COMMAND)
        data = self._receive_data()
        self._reset_sockets(drop_existing=True)

        return data
