from abc import ABC, abstractmethod

from host_manager.host import Host


class TestOracle(ABC):
    @abstractmethod
    def verify_deployment(self, host: Host):
        pass
