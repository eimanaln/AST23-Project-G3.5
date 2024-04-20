import os
import docker

# 1. Create folders to be mounted by the containers
folders = ["ubuntu_18", "ubuntu_22", "fedora"]

for folder in folders:
    folder_path = os.path.join(os.getcwd(), folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder {folder} created at {folder_path}")
    else:
        print(f"Folder {folder} already exists at {folder_path}")

# 2. Create a Docker client 
client = docker.from_env() 

# 3. Define the configurations for the containers and launch 

container_configs = [
    {"image": "ubuntu:18.04", "name": "ubuntu_18", "mount_path": f"{os.getcwd()}/ubuntu_18"},
    {"image": "ubuntu:22.04", "name": "ubuntu_22", "mount_path": f"{os.getcwd()}/ubuntu_22"},
    {"image": "fedora", "name": "fedora", "mount_path": f"{os.getcwd()}/fedora"}
]

# Launch the containers
# tty and command are used to keep the container running: https://stackoverflow.com/a/54623344/14684936 
for config in container_configs:
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