class ContainerConfiguration:
    def __init__(self, image: str, name: str, mount_path: str, post_init_commands: list[str] = []):
        self.image: str = image
        self.name: str = name
        self.mount_path: str = mount_path
        self.post_init_commands : list[str] = post_init_commands
