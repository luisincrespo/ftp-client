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
        if self._ftp_client.host is not None:
            self.prompt = 'ftp(s) {} > '.format(self._ftp_client.host)
        else:
            self.prompt = 'ftp(s) > '

    def do_connect(self, host):
        """Command to connect to an FTP(S) server in the specified host.

        Args:
            host (str): The host to connect to. If a falsy
                        value is passed it defaults to
                        `localhost`.
        """
        try:
            response = self._ftp_client.connect(host)
            print response
        except FtpClient.TimeoutException as e:
            print e.msg
        self._update_prompt()
