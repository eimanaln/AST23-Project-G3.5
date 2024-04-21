from runner.container_runner import launch_all_containers, stop_all_containers, ContainerConfig

if __name__ == "__main__":
    # 3. Define the configurations for the containers
    container_configs: list[ContainerConfig] = [
        ContainerConfig(image="ubuntu:18.04", name="ubuntu_18", mount_path=f"{BASE_PATH}/ubuntu_18"),
        ContainerConfig(image="ubuntu:22.04", name="ubuntu_22", mount_path=f"{BASE_PATH}/ubuntu_22"),
        ContainerConfig(image="fedora", name="fedora", mount_path=f"{BASE_PATH}/fedora")
    ]
    launch_all_containers(container_configs)
    stop_all_containers()