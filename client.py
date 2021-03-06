import socket
import errno


class FtpClient(object):
    """
    This class offers a simple interface to interact with an FTP server.

    Attributes:
    host (str): The host to which the client is connected to, if connected,
                None otherwise.
    user (str): The username of the logged in user, if logged in, None
                otherwise.
    """

    class ConnectionRefusedException(socket.error):
        """
        Exception raised when an FTP host refuses a connection.

        Args:
        host (str): Host that refused connection.

        Attributes:
        msg (str): Human readable string describing the exception.
        """
        def __init__(self, host):
            super(FtpClient.ConnectionRefusedException, self).__init__()
            self.msg = 'Connection to {}:{} failed. Connection refused.'\
                .format(host, FtpClient.PORT)

    class UnknownHostException(socket.gaierror):
        """
        Exception raised when an FTP host is unreachable.

        Args:
        host (str): Unreachable host.

        Attributes:
        msg (str): Human readable string describing the exception.
        """
        def __init__(self, host):
            super(FtpClient.UnknownHostException, self).__init__()
            self.msg = 'Connection to {}:{} failed. Host not reachable.'\
                .format(host, FtpClient.PORT)

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
        Exception raised when FTP commands are performed but the client
        is not currently connected to a host.

        Attributes:
        msg (str): Human readable string describing the exception.
        """
        def __init__(self):
            super(FtpClient.NotConnectedException, self).__init__()
            self.msg = 'Not connected.'

    class NotAuthenticatedException(Exception):
        """
        Exception raised when FTP commands are performed but the client
        is not currently authenticated for a user in the host.

        Attributes:
        msg (str): Human readable string describing the exception.
        """
        def __init__(self):
            super(FtpClient.NotAuthenticatedException, self).__init__()
            self.msg = 'Not authenticated.'

    class LocalIOException(IOError):
        """
        Exception raised when something goes wrong during local IO operations.

        Attributes:
        msg (str): Human readable string describing the exception.
        """
        def __init__(self, msg):
            super(FtpClient.LocalIOException, self).__init__()
            self.msg = 'Local IO error - {}'.format(msg)

    PORT = 21
    SOCKET_TIMEOUT_SECONDS = 5
    SOCKET_RCV_BYTES = 4096

    LIST_COMMAND = 'LIST'
    USER_COMMAND = 'USER'
    PASS_COMMAND = 'PASS'
    EPRT_COMMAND = 'EPRT'
    QUIT_COMMAND = 'QUIT'
    RETR_COMMAND = 'RETR'
    STOR_COMMAND = 'STOR'
    PWD_COMMAND = 'PWD'
    CWD_COMMAND = 'CWD'
    CDUP_COMMAND = 'CDUP'
    MKD_COMMAND = 'MKD'
    DELE_COMMAND = 'DELE'
    RMD_COMMAND = 'RMD'
    RNFR_COMMAND = 'RNFR'
    RNTO_COMMAND = 'RNTO'

    STATUS_230 = '230'
    STATUS_550 = '550'
    STATUS_530 = '530'

    def __init__(self, debug=False):
        self._debug = debug
        self._reset_sockets()

    def _log(self, info):
        if self._debug:
            print('debug: {}'.format(info))

    def _reset_sockets(self):
        self._reset_command_socket()
        self._reset_data_socket()
        self.host = None
        self.user = None

    def _reset_command_socket(self):
        if getattr(self, 'host', None) is not None:
            self._command_socket.close()
        self._command_socket = socket.socket()
        self._command_socket.settimeout(FtpClient.SOCKET_TIMEOUT_SECONDS)

    def _reset_data_socket(self):
        if getattr(self, '_data_socket_listening', False):
            self._data_socket.close()
        self._data_socket = socket.socket()
        self._data_socket_listening = False

    def _send_command(self, command, *args):
        for a in args:
            command = '{} {}'.format(command, a)
        try:
            self._log('sending command - {}'.format(command))
            self._command_socket.sendall('{}\r\n'.format(command))
        except socket.timeout:
            raise FtpClient.TimeoutException(self.host)

    def _receive_command_data(self):
        data = self._command_socket.recv(FtpClient.SOCKET_RCV_BYTES)
        self._log('received command data - {}'.format(data))
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
        self._data_socket_listening = True

    def _open_data_connection(self):
        if not self._data_socket_listening:
            self._open_data_socket()
        self._send_command(FtpClient.EPRT_COMMAND, '|1|{}|{}|'
                           .format(self._data_address, self._data_port))
        self._data_connection, address = self._data_socket.accept()
        self._log('opened data connection on {}'.format(address))
        data = self._receive_command_data()
        return data

    def _read_from_data_connection(self):
        total_data = ''
        while True:
            data = self._data_connection.recv(FtpClient.SOCKET_RCV_BYTES)
            total_data = total_data + data
            if not data:
                break
        self._data_connection.close()
        self._log('received data - {}'.format(total_data))
        return total_data

    def _write_to_data_connection(self, content):
        self._log('sending data - {}'.format(content))
        self._data_connection.sendall(content)
        self._data_connection.close()

    def connect(self, host=None):
        """
        Connect to an FTP server in the specified host.

        Args:
            host (str): The host to connect to. Falsy values
                        default to `localhost`. (Optional)

        Returns:
            Message from host.
        """
        host = host or 'localhost'

        if self.host is not None:
            self._reset_sockets()

        try:
            self._log('connecting to {}:{}'.format(host, FtpClient.PORT))
            self._command_socket.connect((host, FtpClient.PORT))
            self.host = host
        except socket.timeout:
            self._reset_sockets()
            raise FtpClient.TimeoutException(host)
        except socket.gaierror:
            self._reset_sockets()
            raise FtpClient.UnknownHostException(host)
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                raise FtpClient.ConnectionRefusedException(host)

        return self._receive_command_data()

    def login(self, user, password):
        """
        Login with specified user and password on the connected host.

        Args:
            user (str): The user.
            password (str): The password.

        Returns:
            Message from host.
        """
        self._check_is_connected()

        self._send_command(FtpClient.USER_COMMAND, user)
        self._receive_command_data()

        self._send_command(FtpClient.PASS_COMMAND, password)
        data = self._receive_command_data()

        if data.startswith(FtpClient.STATUS_230):
            self.user = user
        elif data.startswith(FtpClient.STATUS_530):
            self.user = None

        return data

    def logout(self):
        """
        Clear info about currently logged user on connected host.
        """
        self._check_is_connected()
        self._check_is_authenticated()
        self._log('logging out {}'.format(self.user))
        self.user = None

    def list(self, filename=None):
        """
        Perform LIST command on connected host.

        Args:
            filename (str): Name of file or directory to retrieve info
                            for. (Optional)

        Returns:
            Message and data from host.
        """
        self._check_is_connected()
        self._check_is_authenticated()

        data = self._open_data_connection()

        if filename is not None:
            self._send_command(FtpClient.LIST_COMMAND, filename)
        else:
            self._send_command(FtpClient.LIST_COMMAND)

        list_data = self._receive_command_data()
        data = data + list_data

        if not list_data.startswith(FtpClient.STATUS_550):
            data = data + self._read_from_data_connection()
            data = data + self._receive_command_data()

        return data

    def disconnect(self):
        """
        Perform QUIT command (disconnect) on connected host.

        Returns:
            Message from host.
        """
        self._check_is_connected()

        self._send_command(FtpClient.QUIT_COMMAND)
        data = self._receive_command_data()
        self._reset_sockets()

        return data

    def retrieve(self, filename, local_filename):
        """
        Perform RETR command on connected host.

        Args:
            filename (str): Name of file to retrieve.
            local_filename (str): Name of local file to create.

        Returns:
            If successful, the tuple containing the message from the host,
            and the file descriptor for the new file.
        """
        self._check_is_connected()
        self._check_is_authenticated()

        data = self._open_data_connection()

        self._send_command(FtpClient.RETR_COMMAND, filename)
        retr_data = self._receive_command_data()
        data = data + retr_data

        local_file = None
        if not retr_data.startswith(FtpClient.STATUS_550):
            content = self._read_from_data_connection()

            try:
                local_file = open(local_filename, 'w+')
                local_file.write(content)
                local_file.close()
            except IOError as e:
                raise FtpClient.LocalIOException(e.strerror)

            data = data + self._receive_command_data()

        return data, local_file

    def store(self, local_filename, filename):
        """
        Perform STOR command on connected host.

        Args:
            local_filename (str): Name of local file to send.
            filename (str): Name of remote file to create.

        Returns:
            Message from host.
        """
        self._check_is_connected()
        self._check_is_authenticated()

        data = self._open_data_connection()

        try:
            local_file = open(local_filename, 'r')
            self._send_command(FtpClient.STOR_COMMAND, filename)
            data = data + self._receive_command_data()
            self._write_to_data_connection(local_file.read())
            local_file.close()
        except IOError as e:
            raise FtpClient.LocalIOException(e.strerror)

        data = data + self._receive_command_data()

        return data

    def pwd(self):
        """
        Perform PWD command on connected host.

        Returns:
            Message from host.
        """
        self._check_is_connected()
        self._check_is_authenticated()

        self._send_command(FtpClient.PWD_COMMAND)
        data = self._receive_command_data()

        return data

    def cwd(self, directory):
        """
        Perform CWD command on connected host.

        Args:
            directory (str): Name of directory to work on.

        Returns:
            Message from host.
        """
        self._check_is_connected()
        self._check_is_authenticated()

        self._send_command(FtpClient.CWD_COMMAND, directory)
        data = self._receive_command_data()

        return data

    def cdup(self):
        """
        Perform CDUP command on connected host.

        Returns:
            Message from host.
        """
        self._check_is_connected()
        self._check_is_authenticated()

        self._send_command(FtpClient.CDUP_COMMAND)
        data = self._receive_command_data()

        return data

    def mkdir(self, directory):
        """
        Perform MKD command on connected host.

        Args:
            directory (str): Name of directory to create.

        Returns:
            Message from host.
        """
        self._check_is_connected()
        self._check_is_authenticated()

        self._send_command(FtpClient.MKD_COMMAND, directory)
        data = self._receive_command_data()

        return data

    def rm(self, filename):
        """
        Perform DELE command on connected host.

        Args:
            filename (str): Name of file to delete.

        Returns:
            Message from host.
        """
        self._check_is_connected()
        self._check_is_authenticated()

        self._send_command(FtpClient.DELE_COMMAND, filename)
        data = self._receive_command_data()

        return data

    def rmdir(self, directory):
        """
        Perform RMD command on connected host.

        Args:
            directory (str): Name of directory to delete.

        Returns:
            Message from host.
        """
        self._check_is_connected()
        self._check_is_authenticated()

        self._send_command(FtpClient.RMD_COMMAND, directory)
        data = self._receive_command_data()

        return data

    def rename(self, from_name, to_name):
        """
        Perform RNFR + RNTO (rename file or directory) command on connected
        host.

        Args:
            from_name (str): Original name of file or directory.
            to_name (str): New name for file or directory.

        Returns:
            Message from host.
        """
        self._check_is_connected()
        self._check_is_authenticated()

        self._send_command(FtpClient.RNFR_COMMAND, from_name)
        data = self._receive_command_data()

        if not data.startswith(FtpClient.STATUS_550):
            self._send_command(FtpClient.RNTO_COMMAND, to_name)
            data = data + self._receive_command_data()

        return data
