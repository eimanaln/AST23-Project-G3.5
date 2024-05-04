import os
import shutil
from typing import Generator

import docker
from docker.models.containers import Container

from runner.container_configuration import ContainerConfiguration
from runner.host import Host


class DockerContainerManager:
    def __init__(self, contaier_configs: list[ContainerConfiguration] = []):
        # Create a Docker client
        self.client = docker.from_env()
        self.running_containers: dict[str, ContainerConfiguration] = {}
        self.container_configs = contaier_configs

    def create_container_folder(self, folder_path: str):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Folder {folder_path} created")
        else:
            print(f"Folder {folder_path} already exists")

    def find_container(self, container_name: str):
        try:
            return self.client.containers.get(container_name)
        except docker.errors.NotFound:
            return None

    def launch_container(self, config: ContainerConfiguration) -> Host:
        container = self.find_container(config.name)
        if not container:
            self.create_container_folder(config.mount_path)
            container = self.client.containers.run(
                image=config.image,
                detach=True,
                name=config.name,
                volumes={config.mount_path: {"bind": "/mnt", "mode": "rw"}},
                privileged=True,
                command="/bin/bash",
                tty=True
            )
            for command in config.post_init_commands:
                print(container.exec_run(cmd=command))
            print(f"Container {config.name} launched with ID {container.id}")
        else:
            container.start()
            print(f"Container {config.name} already exists.")
        self.running_containers[container.id] = config
        # TODO: Return host with correct inventory file
        return Host(inventory_path='example', id=container.id)

    def destroy_host(self, host: Host):
        host_id = host.id
        container = self.find_container(host_id)
        config = self.running_containers[host_id]
        if container:
            container.stop()
            print(f"Container {host_id} stopped.")
        else:
            print(f"Container {host_id} not found.")
        shutil.rmtree(config.mount_path, ignore_errors=True)
        print(f"Folder {config.mount_path} deleted.")

    def host_generator(self) -> Generator[Host, None, None]:
        for container in self.container_configs:
            yield self.launch_container(container)
