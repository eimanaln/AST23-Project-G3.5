import logging
import os
import shutil
import uuid
from socket import socket, AF_INET, SOCK_DGRAM
from typing import Generator

import docker
from docker.client import DockerClient
from docker.errors import APIError, NotFound
from docker.models.containers import Container
from docker.models.networks import Network
from docker.types.networks import IPAMPool, IPAMConfig

from host_manager.host import Host
from host_manager.host_manager import HostManager


class ContainerConfiguration:
    def __init__(self, image: str, name: str, mount_path: str, post_init_commands: list[str] = []):
        self.image: str = image
        self.name: str = name
        self.mount_path: str = mount_path
        self.post_init_commands: list[str] = post_init_commands


class DockerContainerManager(HostManager):
    def __init__(self, container_configs: list[ContainerConfiguration] = [], working_directory: str = None):
        # Create a Docker client
        self.client: DockerClient = docker.from_env()
        self.running_containers: dict[str, ContainerConfiguration] = {}
        self.container_configs: list[ContainerConfiguration] = container_configs
        self.working_directory: str = os.getcwd() if not working_directory else working_directory
        self.network_name: str = "test_network"
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        # Create a file handler
        log_id = uuid.uuid4().hex[:8]  # Generate a unique ID
        self.log_file = os.path.join(self.working_directory, f'container_manager_{log_id}.log')
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)
        # Create a formatter and set the formatter for the handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # Add the handler to the logger
        logger.addHandler(fh)
        return logger

    def _log(self, message):
        self.logger.info(message)

    def _log_and_print(self, message):
        self._log(message)
        print(message)

    def destroy_host(self, host: Host) -> None:
        host_id = host.host_id
        container = self._find_container(host_id)
        config = self.running_containers[host_id]
        if container:
            container.stop()
            container.remove()
            self._log(f"Container {host_id} stopped.")
        else:
            self._log(f"Container {host_id} not found.")
        shutil.rmtree(config.mount_path, ignore_errors=True)
        self._log(f"Folder {config.mount_path} deleted.")

    def host_generator(self) -> Generator[Host, None, None]:
        for container in self.container_configs:
            yield self._launch_container(container)

    def _create_container_folder(self, folder_path: str) -> None:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            self._log(f"Folder {folder_path} created")
        else:
            self._log(f"Folder {folder_path} already exists")

    def _find_container(self, container_name: str) -> Container or None:
        try:
            return self.client.containers.get(container_name)
        except NotFound:
            return None

    def _create_docker_network(self, subnet) -> Network:
        try:
            # Check if the network already exists
            networks = self.client.networks.list()
            for net in networks:
                if net.name == self.network_name:
                    self._log(f"Network '{self.network_name}' already exists.")
                    return net  # Return existing network

            # If the network does not exist, create it
            ipam_pool = IPAMPool(subnet=subnet)
            ipam_config = IPAMConfig(pool_configs=[ipam_pool])
            network = self.client.networks.create(
                self.network_name,
                driver="bridge",
                ipam=ipam_config
            )
            self._log(f"Created network '{self.network_name}' with ID {network.host_id}")
            return network
        except APIError as e:
            self._log_and_print(f"Failed to create or check network: {e}")

    def _launch_container(self, config: ContainerConfiguration) -> Host:
        self._create_docker_network(subnet="192.168.1.0/24")
        container = self._find_container(config.name)
        if not container:
            self._create_container_folder(config.mount_path)
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
            command_failed = False
            for command in config.post_init_commands:
                exec_result = container.exec_run(cmd=command)
                if exec_result.exit_code != 0:
                    command_failed = True
                    print(f"Failed to execute command: {command}")
                self._log(exec_result)
            if command_failed:
                print(f"Some commands failed. See logs for more details. ({self.logger.name})")
            self._log_and_print(f"Container {config.name} launched with ID {container.id}")
        else:
            container.start()
            self._log(f"Container {config.name} already exists.")
        self.running_containers[container.id] = config
        inventory_path = self._create_inventory_file(config.name)
        container.reload()  # Reload the container to get the IP address
        container_ip_addr = container.attrs['NetworkSettings']['Networks'][self.network_name]['IPAddress']
        ip_addr = self._get_host_ip()
        return Host(inventory_path=inventory_path, host_id=container.id, container_ip=container_ip_addr,
                    ip_addr=ip_addr)

    def _create_inventory_file(self, container_name: str) -> str:
        directory_path = os.path.join(self.working_directory, 'inventory_files')
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        inventory_path = os.path.join(directory_path, f"{container_name}_inventory.ini")
        with open(inventory_path, "w") as f:
            f.write(f"[cont]\n")
            f.write(f"{container_name}\n")
            f.write(f"[cont:vars]\n")
            f.write("ansible_connection=docker")
        self._log(f"Inventory file {inventory_path} created.")
        return inventory_path

    def _get_host_ip(self) -> str or None:
        try:
            # Attempt to connect to an arbitrary public IP
            with socket(AF_INET, SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Google's DNS server
                ip = s.getsockname()[0]
            return ip
        except Exception as e:
            print(f"Error: {e}")
            return None
