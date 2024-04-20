import docker

# Function to stop all containers
def stop_containers():
    print("Stopping containers...")
    client = docker.from_env()
    for container in client.containers.list():
        container.stop()
    print("Containers stopped.")

if __name__ == "__main__":
    stop_containers()
