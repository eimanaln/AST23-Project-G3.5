class Host:
    def __init__(self, inventory_path: str, id: str = None):
        # TODO: Add more attributes
        self.inventory_path: str = inventory_path
        self.id: str | None = id
