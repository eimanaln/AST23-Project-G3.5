class Host:
    def __init__(self, inventory_path: str, ip_addr: str, container_ip: str, host_id: str = None):
        # TODO: Add more attributes
        self.inventory_path: str = inventory_path
        self.ip_addr: str = ip_addr
        self.container_ip: str = container_ip
        self.host_id: str | None = host_id
