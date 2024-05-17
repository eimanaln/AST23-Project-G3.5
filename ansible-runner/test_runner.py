import os

from ansible_runner import RunnerConfig, Runner
from test_oracle.deployment_data import DeploymentData

from host_manager.host_manager import HostManager
from test_oracle.test_oracle import TestOracle


class TestRunner():
    def __init__(self, host_manager: HostManager, test_oracle: TestOracle, playbook_path: str, private_data_dir: str = None):
        self.host_manager: HostManager = host_manager
        self.test_oracle: TestOracle = test_oracle
        self.playbook_path: str = playbook_path
        self.private_data_dir: str = private_data_dir if private_data_dir else os.getcwd()

    def run_test(self):
        for host in self.host_manager.host_generator():
            inventory_path = host.inventory_path
            print(inventory_path)
            rc = RunnerConfig(
                private_data_dir=self.private_data_dir,
                playbook=self.playbook_path,
                inventory=inventory_path
            )
            rc.prepare()
            r = Runner(config=rc)
            r.run()
            deployment_data = DeploymentData(runner_config=rc, events=r.events, stats=r.stats)
            test_result = self.test_oracle.verify_deployment(host, deployment_data)
            if test_result.passed:
                print("Test passed: \n" + test_result.message)
            else:
                print("Test failed: \n" + test_result.message)

            test_result = self.test_oracle.verify_deployment(host, deployment_data)
            if test_result.passed:
                print("Test passed: \n" + test_result.message)
            else:
                print("Test failed: \n")
                for port in test_result.ports:
                    print(port)

            self.host_manager.destroy_host(host)