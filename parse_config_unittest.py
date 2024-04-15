import unittest
from motd_server import MotdServer

CONFIG_FILE = "config_random.json"


class TestParseConfig(unittest.TestCase):
    def test_parse_config(self):
        server = MotdServer(CONFIG_FILE)
        config = server.parse_config(CONFIG_FILE)
        expected_config = {
            "motd": "That is the question",
            "encoding": "utf-8",
            "server": {
                "host": "localhost",
                "port": 0
            }
        }

        self.assertEqual(config, expected_config)


if __name__ == '__main__':
    unittest.main()
