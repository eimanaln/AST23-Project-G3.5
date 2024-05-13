class Host:
    def __init__(self, inventory_path: str, IP_addr: str, container_ip: str, id: str = None):
        # TODO: Add more attributes
        self.inventory_path: str = inventory_path
        self.IP_addr: str = IP_addr
        self.container_ip: str = container_ip
        self.id: str | None = id
