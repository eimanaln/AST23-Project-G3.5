import os
import docker
from docker.models.containers import Container

# 2. Create a Docker client
client = docker.from_env()
BASE_PATH = os.getcwd()
# 3. Define the configurations for the containers
container_configs = [
    {"image": "ubuntu:18.04", "name": "ubuntu_18", "mount_path": f"{BASE_PATH}/ubuntu_18"},
    {"image": "ubuntu:22.04", "name": "ubuntu_22", "mount_path": f"{BASE_PATH}/ubuntu_22"},
    {"image": "fedora", "name": "fedora", "mount_path": f"{BASE_PATH}/fedora"}
]
running_containers: list[Container] = []


def create_container_folder(folder_name: str):
    folder_path = os.path.join(BASE_PATH, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder {folder_name} created at {folder_path}")
    else:
        print(f"Folder {folder_name} already exists at {folder_path}")


def launch_container(config) -> Container:
    container = client.containers.run(
        config["image"],
        detach=True,
        name=config["name"],
        volumes={config["mount_path"]: {"bind": "/mnt", "mode": "rw"}},
        privileged=True,
        command="/bin/bash",
        tty=True
    )
    print(f"Container {config['name']} launched with ID {container.id}")
    return container


def launch_all_containers():
    # Launch the containers
    # tty and command are used to keep the container running: https://stackoverflow.com/a/54623344/14684936
    for config in container_configs:
        create_container_folder(config['name'])
        container = launch_container(config)
        running_containers.append(container)


# Function to stop all containers
def stop_all_containers():
    print("Stopping containers...")
    for container in running_containers:
        container.stop()
    print("Containers stopped.")
