from abc import ABC, abstractmethod

from host_manager.host import Host
from .deployment_data import DeploymentData
from .test_result import TestResult



class TestOracle(ABC):
    @abstractmethod
    def verify_deployment(self, host: Host, deployment_data: DeploymentData) -> TestResult:
        pass

    @abstractmethod
    def verify_play_reacap(self, host: Host, deployment_data: DeploymentData) -> TestResult:
        pass
