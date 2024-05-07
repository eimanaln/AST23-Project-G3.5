from abc import ABC, abstractmethod

from deployment_data import DeploymentData
from host_manager.host import Host
from test_result import TestResult


class TestOracle(ABC):
    @abstractmethod
    def verify_deployment(self, host: Host, deployment_data: DeploymentData) -> TestResult:
        pass
