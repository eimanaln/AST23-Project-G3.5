import os
import docker
from docker.models.containers import Container


class ContainerConfiguration:
    def __init__(self, image: str, name: str, mount_path: str):
        self.image: str = image
        self.name: str = name
        self.mount_path: str = mount_path


# 2. Create a Docker client
client = docker.from_env()
running_containers: list[Container] = []


def create_container_folder(folder_path: str):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder {folder_path} created")
    else:
        print(f"Folder {folder_path} already exists")


def launch_container(config: ContainerConfiguration) -> Container:
    create_container_folder(config.mount_path)
    container = client.containers.run(
        config.image,
        detach=True,
        name=config.name,
        volumes={config.mount_path: {"bind": "/mnt", "mode": "rw"}},
        privileged=True,
        command="/bin/bash",
        tty=True
    )
    print(f"Container {config.name} launched with ID {container.id}")
    return container


def launch_all_containers(container_configs: list[ContainerConfiguration]):
    # Launch the containers
    # tty and command are used to keep the container running: https://stackoverflow.com/a/54623344/14684936
    for config in container_configs:
        container = launch_container(config)
        running_containers.append(container)


# Function to stop all containers
def stop_all_containers():
    print("Stopping containers...")
    for container in running_containers:
        container.stop()
    print("Containers stopped.")
