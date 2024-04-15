import unittest
import socket
import threading
import time
from motd_server import MotdServer

CONFIG_FILE = 'config_random.json'


class TestMotdServer(unittest.TestCase):
    def setUp(self):
        self.server = MotdServer(CONFIG_FILE)
        self.config = MotdServer.parse_config(CONFIG_FILE)
        self.server_thread = threading.Thread(target=self.server.run)
        self.server_thread.daemon = True
        self.server_thread.start()

    def tearDown(self):
        self.server.stop()

    def test_connect(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(self.get_server_address())
        received_data = client_socket.recv(1024).decode(self.config["encoding"])
        client_socket.close()
        self.assertEqual(received_data, self.config["motd"])

    def get_server_address(self):
        server_host, server_port = self.config["server"]["host"], self.config["server"]["port"]
        while not server_port:
            time.sleep(0.1)
            server_port = self.server.get_listening_port()
        return server_host, server_port


if __name__ == '__main__':
    unittest.main()
