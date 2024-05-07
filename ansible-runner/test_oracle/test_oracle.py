from abc import ABC, abstractmethod

from host_manager.host import Host
from deployment_data import DeploymentData


class TestOracle(ABC):
    @abstractmethod
    def verify_deployment(self, host: Host, deployment_data: DeploymentData):
        pass
