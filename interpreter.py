from cmd import Cmd

from client import FtpClient


class FtpsInterpreter(Cmd):
    def __init__(self):
        Cmd.__init__(self)
        self.intro = 'Simple FTPS Client'
        self.prompt = 'ftps > '
        self._ftp_client = FtpClient()

    def do_connect(self, host):
        """
        Connect to the specified FTP(S) server.
        If no host is specified it'll default to localhost.
        """
        response = self._ftp_client.connect(host)
        print response
