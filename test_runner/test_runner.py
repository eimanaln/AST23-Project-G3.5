import os
import time
from ansible_runner import RunnerConfig, Runner
from test_runner.test_oracle.deployment_data import DeploymentData
from host_manager.host_manager import HostManager
from test_runner.test_oracle.test_oracle import TestOracle
import csv

OKGREEN = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'


class TestRunner():
    def __init__(self, host_manager: HostManager, test_oracle: TestOracle, playbook_path: str,
                 private_data_dir: str = None):
        self.host_manager: HostManager = host_manager
        self.test_oracle: TestOracle = test_oracle
        self.playbook_path: str = playbook_path
        self.private_data_dir: str = private_data_dir if private_data_dir else os.getcwd()

    def run_test(self):
        total_generator_time = 0
        total_run_time = 0
        total_deployment_time = 0
        num_runs = 0

        start_generator_time = time.time()

        output_file = "time_measurements.csv"
        write_header = not os.path.exists(output_file)
        with open(output_file, mode='a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            if write_header:
                csv_writer.writerow(['Generator Time', 'Run Time', 'Verification Time'])
            for host in self.host_manager.host_generator():
                end_generator_time = time.time()
                total_generator_time += end_generator_time - start_generator_time

                start_deployment_time = time.time()
                inventory_path = host.inventory_path
                rc = RunnerConfig(
                    private_data_dir=self.private_data_dir,
                    playbook=self.playbook_path,
                    inventory=inventory_path
                )
                rc.prepare()
                r = Runner(config=rc)
                r.run()
                end_run_time = time.time()

                deployment_data = DeploymentData(runner_config=rc, events=r.events, stats=r.stats)

                start_verification_time = time.time()
                test_result = self.test_oracle.verify_deployment(host, deployment_data)
                end_deployment_time = time.time()

                if test_result.passed:
                    print(OKGREEN + "Test passed:" + ENDC)
                else:
                    print(FAIL + "Test failed:" + test_result.message + ENDC)

                print('Test-Output: ' + test_result.message)

                self.host_manager.destroy_host(host)

                total_run_time += end_run_time - start_deployment_time
                total_deployment_time += end_deployment_time - start_verification_time
                num_runs += 1
                start_generator_time = time.time()


            if num_runs > 0:
                avg_generator_time = total_generator_time / num_runs
                avg_run_time = total_run_time / num_runs
                avg_verification_time = total_deployment_time / num_runs
                csv_writer.writerow([avg_generator_time, avg_run_time, avg_verification_time])
