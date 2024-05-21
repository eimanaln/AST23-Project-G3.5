import os

from test_runner.test_runner import TestRunner
from test_runner.test_oracle.aliveness_oracle import AlivenessOracle
from test_runner.test_oracle.recap_oracle import RecapOracle
from test_runner.test_oracle.vulnerability_oracle import VulnerabilityOracle

from host_manager.docker_container_manager.docker_container_manager import DockerContainerManager, \
    ContainerConfiguration

if __name__ == "__main__":
    BASE_PATH = os.getcwd()
    full_path = os.path.join(BASE_PATH, "demo")
    container_path = os.path.join(full_path, "containers")
    if not os.path.exists(full_path):
        os.makedirs(full_path)
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
        # ContainerConfiguration(image="fedora", name="fedora", mount_path=f"{container_path}/fedora")
    ]
    for oracle in [AlivenessOracle(), RecapOracle(), VulnerabilityOracle()]:
        manager = DockerContainerManager(container_configs=container_configs)
        playbook_path = os.path.join(full_path, "deploy.yml")
        test_runner = TestRunner(host_manager=manager, playbook_path=playbook_path, test_oracle=oracle)
        test_runner.run_test()

