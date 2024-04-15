import socket
import json
import sys
import logging

logging.basicConfig(stream=sys.stdout, format="%(message)s")


class MotdServer:
    def __init__(self, config_file):
        config = self.parse_config(config_file)
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.INFO)
        self._host = config["server"]["host"]
        self._port = config["server"]["port"]
        self._motd = config["motd"]
        self._logger.info(f"MOTD: {self._motd}")
        self._encoding = config["encoding"]
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((self._host, self._port))

    @staticmethod
    def parse_config(filename):
        with open(filename, 'r') as f:
            config = json.load(f)
        return config

    def run(self):
        self._server_socket.listen(10)
        self._logger.info(f"[STARTING] Server listening on {self._server_socket.getsockname()}")
        self._logger.info(f"Config Port: {self._port}")
        self._logger.info(f"Listen Port: {self.get_listening_port()}")
        try:
            while True:
                conn, addr = self._server_socket.accept()
                conn.send(self._motd.encode(self._encoding))
                self._logger.info(f"[SENDING] Message of the day sent to client {addr}")
                conn.close()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self._server_socket.close()
        self._logger.info("[STOPPING] Server stopped")

    def get_listening_port(self):
        return self._server_socket.getsockname()[1]


if __name__ == "__main__":
    _, config_file = sys.argv
    server = MotdServer(config_file)
    server.run()
