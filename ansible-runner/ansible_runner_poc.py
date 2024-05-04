from ansible_runner import Runner, RunnerConfig
import os

from host_manager.docker_container_manager.docker_container_manager import DockerContainerManager
from host_manager.docker_container_manager.container_configuration import ContainerConfiguration

if __name__ == "__main__":
    BASE_PATH = os.getcwd()
    full_path = os.path.join(BASE_PATH, "demo")
    container_path = os.path.join(full_path, "containers")
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    # Define the configurations for the containers
    container_configs: list[ContainerConfiguration] = [
        ContainerConfiguration(image="ubuntu:18.04", name="ubuntu_18", mount_path=f"{container_path}/ubuntu_18",
                               post_init_commands=["apt-get update", "apt-get install -y python3",
                                                   "ln -s /usr/bin/python3 /usr/bin/python"]),
        ContainerConfiguration(image="ubuntu:22.04", name="ubuntu_22", mount_path=f"{container_path}/ubuntu_22",
                               post_init_commands=["apt-get update", "apt-get install -y python3",
                                                   "ln -s /usr/bin/python3 /usr/bin/python"]),
        # ContainerConfiguration(image="fedora", name="fedora", mount_path=f"{container_path}/fedora")
    ]
    manager = DockerContainerManager(container_configs=container_configs)

    playbook_path = os.path.join(full_path, "deploy.yml")
    for host in manager.host_generator():
        inventory_path = host.inventory_path
        print(inventory_path)
        rc = RunnerConfig(
            private_data_dir=full_path,
            playbook=playbook_path,
            inventory=inventory_path
        )
        rc.prepare()
        r = Runner(config=rc)
        r.run()
        print("{}: {}".format(r.status, r.rc))
        for each_host_event in r.events:
            print(each_host_event['event'])
        print("Final status:")
        print(r.stats)
        manager.destroy_host(host)

