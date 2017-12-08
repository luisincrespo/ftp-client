import os
from cmd import Cmd

from client import FtpClient


class FtpInterpreter(Cmd):
    """
    FTP client command line utility.
    """
    def __init__(self, debug=False):
        Cmd.__init__(self)
        self.intro = ('FTP Client. Start typing help or ? to see available '
                      'commands.')
        self.prompt = 'FTP > '
        self._ftp_client = FtpClient(debug=debug)

    def _update_prompt(self):
        prompt = 'FTP'
        if self._ftp_client.host is not None:
            prompt = '{} {}'.format(prompt, self._ftp_client.host)
            if self._ftp_client.user is not None:
                prompt = '{} ({})'.format(prompt, self._ftp_client.user)
        self.prompt = '{} > '.format(prompt)

    def _perform_ftp_command(self, command, *args):
        method = getattr(self._ftp_client, command)
        try:
            response = method(*args)
        except (FtpClient.TimeoutException,
                FtpClient.UnknownHostException) as e:
            response = e.msg
        except FtpClient.NotConnectedException as e:
            response = e.msg
            response = ('{}\nPlease connect to an FTP server using'
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

    def emptyline(self):
        pass

    def do_connect(self, host):
        """
        Command to connect to an FTP server in the specified host.

        Args:
            host (str): The host to connect to.
        """
        response = self._perform_ftp_command('connect', host)
        print response
        self._update_prompt()

    def do_login(self, *args):
        """
        Command to login with user and password in the connected FTP host.
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
        Command to logout the current user from the connected FTP host.
        """
        self._perform_ftp_command('logout')
        self._update_prompt()

    def do_list(self, filename):
        """
        Command to perform LIST command on the connected FTP host.

        Args:
            filename (str): Name of file or directory to retrieve info for.
        """
        response = self._perform_ftp_command('list', filename)
        print response

    def do_disconnect(self, *args):
        """
        Command to disconnect from connected FTP host.
        """
        response = self._perform_ftp_command('disconnect')
        print response
        self._update_prompt()

    def do_retrieve(self, *args):
        """
        Command to retrieve a file from the connected FTP host and store
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

        local_file = None
        if isinstance(response, tuple):
            response, local_file = response

        print response
        if local_file is not None:
            local_path = os.path.realpath(local_file.name)
            print 'Local file created: {}'.format(local_path)

    def do_store(self, *args):
        """
        Command to send a local file to the connected FTP host.
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
        Command to retrieve the current directory on the connected FTP host.
        """
        response = self._perform_ftp_command('pwd')
        print response

    def do_cwd(self, directory):
        """
        Command to change current directory on the connected FTP host.

        Args:
            directory (str): Name of directory to work on.
        """
        response = self._perform_ftp_command('cwd', directory)
        print response

    def do_cdup(self, *args):
        """
        Command to set parent directory as current working directory
        on the connected FTP host.
        """
        response = self._perform_ftp_command('cdup')
        print response

    def do_mkdir(self, directory):
        """
        Command to create directory on the connected FTP host.

        Args:
            directory (str): Name of directory to create.
        """
        response = self._perform_ftp_command('mkdir', directory)
        print response

    def do_rm(self, filename):
        """
        Command to remove file on the connected FTP host.

        Args:
            filename (str): Name of file to delete.
        """
        response = self._perform_ftp_command('rm', filename)
        print response

    def do_rmdir(self, directory):
        """
        Command to remove directory on the connected FTP host.

        Args:
            directory (str): Name of directory to delete.
        """
        response = self._perform_ftp_command('rmdir', directory)
        print response

    def do_rename(self, *args):
        """
        Command to rename a file or directory on the connected FTP host.
        """
        original_filename = ''
        while not original_filename:
            original_filename = raw_input('Name of original remote file: ')
        new_filename = ''
        while not new_filename:
            new_filename = raw_input('New name for remote file: ')

        response = self._perform_ftp_command('rename', original_filename,
                                             new_filename)
        print response
