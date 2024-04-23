import ansible_runner
import os

from runner.container_runner import DockerContainerManager
from runner.container_configuration import ContainerConfiguration

if __name__ == "__main__":
    BASE_PATH = os.getcwd()
    manager = DockerContainerManager()
    # Define the configurations for the containers
    container_configs: list[ContainerConfiguration] = [
        ContainerConfiguration(image="ubuntu:18.04", name="ubuntu_18", mount_path=f"{BASE_PATH}/ubuntu_18",
                               post_init_commands=["apt-get update", "apt-get install -y python3",
                                                   "ln -s /usr/bin/python3 /usr/bin/python"]),
        ContainerConfiguration(image="ubuntu:22.04", name="ubuntu_22", mount_path=f"{BASE_PATH}/ubuntu_22",
                               post_init_commands=["apt-get update", "apt-get install -y python3",
                                                   "ln -s /usr/bin/python3 /usr/bin/python"]),
        ContainerConfiguration(image="fedora", name="fedora", mount_path=f"{BASE_PATH}/fedora")
    ]
    manager.launch_all_containers(container_configs=container_configs)
    r = ansible_runner.run(private_data_dir='.', playbook='deploy.yml', inventory='inventory.ini')
    print("{}: {}".format(r.status, r.rc))
    # successful: 0
    for each_host_event in r.events:
        print(each_host_event['event'])
    print("Final status:")
    print(r.stats)
    manager.stop_all_containers()
