import os
import docker
from docker.models.containers import Container

from runner.container_configuration import ContainerConfiguration

class DockerContainerManager:
    def __init__(self):
        # Create a Docker client
        self.client = docker.from_env()
        self.running_containers = []

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

    def launch_container(self, config: ContainerConfiguration) -> Container:
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
        self.running_containers.append(container)
        return container

    def launch_all_containers(self, container_configs: list[ContainerConfiguration]):
        # Launch the containers
        # tty and command are used to keep the container running: https://stackoverflow.com/a/54623344/14684936
        for config in container_configs:
            container = self.launch_container(config)
            self.running_containers.append(container)

    def stop_all_containers(self):
        print("Stopping containers...")
        for container in self.running_containers:
            container.stop()
        print("Containers stopped.")
