import os

from test_runner.test_runner import TestRunner
from test_runner.test_oracle.aliveness_oracle import AlivenessOracle
from test_runner.test_oracle.recap_oracle import RecapOracle
from test_runner.test_oracle.vulnerability_oracle import VulnerabilityOracle

from host_manager.docker_container_manager import DockerContainerManager, \
    ContainerConfiguration

if __name__ == "__main__":
    BASE_PATH = os.getcwd()
    full_path = os.path.join(BASE_PATH, "temporary_test_data")
    container_path = os.path.join(full_path, "containers")
    artifacts_path = os.path.join(full_path, "artifacts")
    playbook_path = os.path.join(BASE_PATH, "test_resources", "deploy_apache.yml")
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    if not os.path.exists(container_path):
        os.makedirs(container_path)

    # Define the configurations for the containers
    container_configs: list[ContainerConfiguration] = [
        ContainerConfiguration(image="ubuntu:18.04", name="ubuntu_18", mount_path=f"{container_path}/ubuntu_18",
                               post_init_commands=["apt-get update", "apt-get install -y python3 sudo ufw",
                                                    "ln -s /usr/bin/python3 /usr/bin/python", "sudo ufw enable",
                                                    "sudo ufw allow 80/tcp"]),
        ContainerConfiguration(image="ubuntu:22.04", name="ubuntu_22", mount_path=f"{container_path}/ubuntu_22",
                               post_init_commands=["apt-get update", "apt-get install -y python3 sudo ufw",
                                                   "ln -s /usr/bin/python3 /usr/bin/python", "sudo ufw enable",
                                                   "sudo ufw allow 80/tcp"]),
        ContainerConfiguration(image="fedora:39", name="fedora", mount_path=f"{container_path}/fedora",
                               post_init_commands=["dnf update -y", "dnf install -y python3 sudo systemd",
                                    "ln -s /usr/bin/python3 /usr/bin/python", "setsid /usr/sbin/init &"])
    ]
    # Run tests on the Apache server 
    for oracle in [AlivenessOracle(), RecapOracle(), VulnerabilityOracle()]:
        manager = DockerContainerManager(container_configs=container_configs, working_directory=container_path)
        test_runner = TestRunner(host_manager=manager, playbook_path=playbook_path, test_oracle=oracle, private_data_dir=artifacts_path)
        test_runner.run_test()

    # Run tests on the Nginx server
    playbook_path = os.path.join(BASE_PATH, "test_resources", "deploy_nginx.yml")
    for oracle in [AlivenessOracle(), RecapOracle(), VulnerabilityOracle()]:
        manager = DockerContainerManager(container_configs=container_configs, working_directory=container_path)
        test_runner = TestRunner(host_manager=manager, playbook_path=playbook_path, test_oracle=oracle, private_data_dir=artifacts_path)
        test_runner.run_test()


