import os
import shutil
from typing import Generator
import socket

import docker

from host_manager.docker_container_manager.container_configuration import ContainerConfiguration
from host_manager.host import Host
from host_manager.host_manager import HostManager


class DockerContainerManager(HostManager):
    def __init__(self, container_configs: list[ContainerConfiguration] = [], working_directory: str = None):
        # Create a Docker client
        self.client = docker.from_env()
        self.running_containers: dict[str, ContainerConfiguration] = {}
        self.container_configs = container_configs
        self.working_directory = os.getcwd() if not working_directory else working_directory
        self.network_name = "test_network"

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
        
    def create_docker_network(self, subnet):
        try:
            # Check if the network already exists
            networks = self.client.networks.list()
            for net in networks:
                if net.name == self.network_name:
                    print(f"Network '{self.network_name}' already exists.")
                    return net  # Return existing network

            # If the network does not exist, create it
            ipam_pool = docker.types.IPAMPool(
                subnet=subnet
            )
            ipam_config = docker.types.IPAMConfig(
                pool_configs=[ipam_pool]
            )
            network = self.client.networks.create(
                self.network_name,
                driver="bridge",
                ipam=ipam_config
            )
            print(f"Created network '{self.network_name}' with ID {network.id}")
            return network
        except docker.errors.APIError as e:
            print(f"Failed to create or check network: {e}")

        

    def launch_container(self, config: ContainerConfiguration) -> Host:

        self.create_docker_network(subnet="192.168.1.0/24")
        container = self.find_container(config.name)
        if not container:
            self.create_container_folder(config.mount_path)
            container = self.client.containers.run(
                image=config.image,
                detach=True,
                name=config.name,
                network=self.network_name,
                volumes={config.mount_path: {"bind": "/mnt", "mode": "rw"}},
                privileged=True,
                ports={"80/tcp": 8080},
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
        inventory_path = self.create_inventory_file(config.name)
        container.reload() # Reload the container to get the IP address
        container_IP_addr = container.attrs['NetworkSettings']['Networks'][self.network_name]['IPAddress']
        IP_addr = self.get_host_ip()
        return Host(inventory_path=inventory_path, id=container.id, container_ip=container_IP_addr, IP_addr=IP_addr)

    def create_inventory_file(self, container_name: str) -> str:
        directory_path = os.path.join(self.working_directory, 'tmp')
        print(directory_path)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        inventory_path = os.path.join(directory_path, f"{container_name}_inventory.ini")
        with open(inventory_path, "w") as f:
            f.write(f"[cont]\n")
            f.write(f"{container_name}\n")
            f.write(f"[cont:vars]\n")
            f.write("ansible_connection=docker")
        print(f"Inventory file {inventory_path} created.")
        return inventory_path

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

    def get_host_ip(self):
        try:
            # Attempt to connect to an arbitrary public IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Google's DNS server
                IP = s.getsockname()[0]
            return IP
        except Exception as e:
            print(f"Error: {e}")
            return None

