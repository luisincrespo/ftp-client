import unittest
import socket
from mock import patch, MagicMock

from client import FtpClient


class TestFtpClient(unittest.TestCase):
    @patch('client.socket.socket')
    def setUp(self, mock_socket):
        self.my_socket_mock = MagicMock()
        mock_socket.return_value = self.my_socket_mock
        self.ftp_client = FtpClient()

    def test_initializes_socket_with_timeout(self):
        self.my_socket_mock.settimeout.assert_called_with(5)

    def test_connect_defaults_to_localhost(self):
        self.ftp_client.connect('')
        self.my_socket_mock.connect.assert_called_with(('localhost', 21))

    def test_connect_to_specified_host(self):
        self.ftp_client.connect('foo')
        self.my_socket_mock.connect.assert_called_with(('foo', 21))

    def test_connect_returns_data_from_host(self):
        self.my_socket_mock.recv.return_value = 'bar'
        data = self.ftp_client.connect('foo')
        self.my_socket_mock.connect.assert_called_with(('foo', 21))
        self.assertEqual(data, 'bar')

    def test_connect_raises_timeout_exception_on_socket_timeout(self):
        self.my_socket_mock.connect.side_effect = socket.timeout()
        with self.assertRaises(FtpClient.TimeoutException):
            self.ftp_client.connect('foo')

    @patch('client.socket.socket')
    def test_connect_drops_existing_connection(self, mock_socket):
        self.ftp_client.connect('foo')
        self.my_socket_mock.connect.assert_called_with(('foo', 21))

        self.my_new_socket_mock = MagicMock()
        mock_socket.return_value = self.my_new_socket_mock

        self.ftp_client.connect('bar')
        self.my_socket_mock.close.assert_called()
        self.my_new_socket_mock.connect.assert_called_with(('bar', 21))

    @patch('client.socket.socket')
    def test_keeps_track_of_current_host(self, mock_socket):
        self.ftp_client.connect('foo')
        self.assertEqual(self.ftp_client.host, 'foo')

        self.ftp_client.connect('bar')
        self.assertEqual(self.ftp_client.host, 'bar')


if __name__ == '__main__':
    unittest.main()
