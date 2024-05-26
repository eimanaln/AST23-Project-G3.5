import os

from ansible_runner import RunnerConfig, Runner
from test_runner.test_oracle.deployment_data import DeploymentData

from host_manager.host_manager import HostManager
from host_manager.host import Host
from test_runner.test_oracle.test_oracle import TestOracle

OKGREEN = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'

class TestRunner():
    def __init__(self, host_manager: HostManager, test_oracles: list[TestOracle], playbook_path: str, private_data_dir: str = None):
        self.host_manager: HostManager = host_manager
        self.test_oracles: list[TestOracle] = test_oracles
        self.playbook_path: str = playbook_path
        self.private_data_dir: str = private_data_dir if private_data_dir else os.getcwd()

    def run_tests(self):
        for host in self.host_manager.host_generator():
            inventory_path = host.inventory_path
            rc = RunnerConfig(
                private_data_dir=self.private_data_dir,
                playbook=self.playbook_path,
                inventory=inventory_path
            )
            rc.prepare()
            r = Runner(config=rc)
            r.run()
            deployment_data = DeploymentData(runner_config=rc, events=r.events, stats=r.stats)
            self._run_oracles(host, deployment_data)

            self.host_manager.destroy_host(host)

    def _run_oracles(self, host: Host, deployment_data: DeploymentData):
        for oracle in self.test_oracles:
            test_result = oracle.verify_deployment(host, deployment_data)
            if test_result.passed:
                print(OKGREEN + "Test passed:" + ENDC)
            else:
                print(FAIL + "Test failed:" + test_result.message + ENDC)

            print('Test-Output: ' + test_result.message)
