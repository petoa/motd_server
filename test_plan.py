import sys
import os
import re

from testplan import test_plan
from testplan.testing.multitest import MultiTest, testsuite, testcase
from testplan.testing.multitest.driver.app import App
from testplan.testing.multitest.driver.tcp import TCPClient
from testplan.report.testing.styles import Style, StyleEnum
from testplan.common.utils.context import context

OUTPUT_STYLE = Style(StyleEnum.ASSERTION_DETAIL, StyleEnum.ASSERTION_DETAIL)


@testsuite
class FixedPortSuite:

    @testcase
    def fixed_port_connection(self, env, result):
        result.log(f"Configured listening port: {env.motd.extracts['config_port']}")
        result.log(f"Actual listening port: {env.motd.extracts['port']}")
        result.equal(env.motd.extracts['config_port'], env.motd.extracts['port'],
                     description="Config port and actual listening port is matching")
        env.client.connect()
        result.log(f"Client connecting to port: {env.client.server_port}")
        result.equal(int(env.motd.extracts['port']), env.client.server_port,
                     description="Server's listening port and client's target port is matching")
        result.equal(env.motd.extracts["motd_msg"], env.client.receive_text(),
                     description="Message received from MOTD server")


@testsuite
class RandomPortSuite:

    @testcase
    def random_port_connection(self, env, result):
        result.log(f"Configured listening port: {env.motd.extracts['config_port']}")
        result.log(f"Actual listening port: {env.motd.extracts['port']}")
        result.not_equal(env.motd.extracts['config_port'], env.motd.extracts['port'],
                         description="Config port and actual listening port is different")
        env.client.connect()
        result.log(f"Client connecting to port: {env.client.server_port}")
        result.equal(int(env.motd.extracts['port']), env.client.server_port,
                     description="Server's listening port and client's target port is matching")
        result.equal(env.motd.extracts["motd_msg"], env.client.receive_text(),
                     description="Message received from MOTD server")


def create_test(name, suite, config):
    test = MultiTest(
        name=name,
        suites=[suite],
        environment=[
            App(
                name="motd",
                pre_args=[sys.executable],
                binary=os.path.join(os.path.dirname(os.path.abspath(__file__)), "motd_server.py"),
                args=[f"etc/{config}"],
                log_regexps=[
                    re.compile(r"Config Port: (?P<config_port>\d+)"),
                    re.compile(r"Listen Port: (?P<port>\d+)"),
                    re.compile(r"MOTD: (?P<motd_msg>.*)")
                ],
                install_files=[os.path.join(os.path.dirname(os.path.abspath(__file__)), config)]
            ),
            TCPClient(
                name="client",
                host="localhost",
                port=context("motd", "{{extracts['port']}}")
            )
        ]
    )
    return test


@test_plan(
    name="MOTDServer",
    pdf_path="report.pdf",
    stdout_style=OUTPUT_STYLE,
    pdf_style=OUTPUT_STYLE,
)
def main(plan):
    plan.add(create_test("FixedPortTest", FixedPortSuite(), "config_fix.json"))
    plan.add(create_test("RandomPortTest", RandomPortSuite(), "config_random.json"))


if __name__ == '__main__':
    res = main()
    print("Exiting code: {}".format(res.exit_code))
    sys.exit(res.exit_code)
