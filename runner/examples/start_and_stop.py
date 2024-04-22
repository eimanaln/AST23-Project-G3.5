import os

from runner.container_runner import launch_all_containers, stop_all_containers
from runner.container_configuration import ContainerConfiguration

if __name__ == "__main__":
    BASE_PATH = os.getcwd()
    # Define the configurations for the containers
    container_configs: list[ContainerConfiguration] = [
        ContainerConfiguration(image="ubuntu:18.04", name="ubuntu_18", mount_path=f"{BASE_PATH}/ubuntu_18", post_init_commands=["apt-get update", "apt-get install -y python3", "ln -s /usr/bin/python3 /usr/bin/python"]),
        #ContainerConfiguration(image="ubuntu:22.04", name="ubuntu_22", mount_path=f"{BASE_PATH}/ubuntu_22"),
        #ContainerConfiguration(image="fedora", name="fedora", mount_path=f"{BASE_PATH}/fedora")
    ]
    launch_all_containers(container_configs)
    stop_all_containers()