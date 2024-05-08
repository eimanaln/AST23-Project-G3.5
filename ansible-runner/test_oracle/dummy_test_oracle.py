from .deployment_data import DeploymentData
from host_manager.host import Host
from .test_oracle import TestOracle
from .test_result import TestResult


class DummyTestOracle(TestOracle):
    def verify_deployment(self, host: Host, deployment_data: DeploymentData) -> TestResult:
        return TestResult(True, "Deployment verified successfully")