from cmd import Cmd

from client import FtpClient


class FtpsInterpreter(Cmd):
    """
    FTP command line utility that supports non-secure and secure connections.
    """
    def __init__(self):
        Cmd.__init__(self)
        self.intro = 'FTP(S) Client'
        self.prompt = 'ftp(s) > '
        self._ftp_client = FtpClient()

    def _update_prompt(self):
        prompt = 'ftp(s)'
        if self._ftp_client.host is not None:
            prompt = '{} {}'.format(prompt, self._ftp_client.host)
            if self._ftp_client.user is not None:
                prompt = '{} ({})'.format(prompt, self._ftp_client.user)
        self.prompt = '{} > '.format(prompt)

    def _perform_ftp_command(self, command, *args):
        method = getattr(self._ftp_client, command)
        try:
            response = method(*args)
        except FtpClient.TimeoutException as e:
            response = e.msg
        except FtpClient.NotConnectedException as e:
            response = e.msg
            response = ('{}\nPlease connect to an FTP(S) server using'
                        ' the `connect` command').format(response)
        except FtpClient.NotAuthenticatedException as e:
            response = e.msg
            response = ('{}\nPlease authenticate using the `login` command.')\
                .format(response)
        except FtpClient.LocalIOException as e:
            response = e.msg
            response = ('{}\nSomething went wrong trying to {} the file,'
                        ' please try again.').format(response, command)
        return response

    def do_connect(self, host):
        """
        Command to connect to an FTP(S) server in the specified host.

        Args:
            host (str): The host to connect to.
        """
        response = self._perform_ftp_command('connect', host)
        print response
        self._update_prompt()

    def do_login(self, *args):
        """
        Command to login with user and password in the connected FTP(S) host.
        """
        user = ''
        while not user:
            user = raw_input('User: ')
        password = ''
        while not password:
            password = raw_input('Password: ')

        response = self._perform_ftp_command('login', user, password)
        print response
        self._update_prompt()

    def do_logout(self, *args):
        """
        Command to logout the current user from the connected FTP(S) host.
        """
        response = self._perform_ftp_command('logout')
        print response
        self._update_prompt()

    def do_list(self, filename):
        """
        Command to perform LIST command on the connected FTP(S) host.

        Args:
            filename (str): Name of file or directory to retrieve info for.
        """
        response = self._perform_ftp_command('list', filename)
        print response

    def do_disconnect(self, *args):
        """
        Command to disconnect from connected FTP(S) host.
        """
        response = self._perform_ftp_command('disconnect')
        print response
        self._update_prompt()

    def do_retrieve(self, *args):
        """
        Command to retrieve a file from the connected FTP(S) host and store
        it locally.
        """
        filename = ''
        while not filename:
            filename = raw_input('Remote file: ')
        local_filename = ''
        while not local_filename:
            local_filename = raw_input('Local file: ')

        response = self._perform_ftp_command('retrieve', filename,
                                             local_filename)
        print response

    def do_store(self, *args):
        """
        Command to send a local file to the connected FTP(S) host.
        """
        local_filename = ''
        while not local_filename:
            local_filename = raw_input('Local file: ')
        filename = ''
        while not filename:
            filename = raw_input('Remote file: ')

        response = self._perform_ftp_command('store', local_filename,
                                             filename)
        print response

    def do_pwd(self, *args):
        """
        Command to retrieve the current directory on the connected FTP(S) host.
        """
        response = self._perform_ftp_command('pwd')
        print response
