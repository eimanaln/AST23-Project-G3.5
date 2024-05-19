from .deployment_data import DeploymentData
from host_manager.host import Host
from .test_oracle import TestOracle
from .test_result import TestResult


class RecapOracle(TestOracle):
    def verify_play_reacap(self, host: Host, deployment_data: DeploymentData) -> TestResult:

        stats = deployment_data.stats

        unreachable = stats.get('dark', {}) # dark means unreachable
        failed = stats.get('failures', {})
        ignored = stats.get('ignored', {})

        if not unreachable and not failed and not ignored:
            return TestResult(True, "Deployment successful with no unreachable, failed, or ignored tasks")
        else:
            message_parts = []
            if unreachable:
                message_parts.append(f"Unreachable: {len(unreachable)}")
            if failed:
                message_parts.append(f"Failed: {len(failed)}")
            if ignored:
                message_parts.append(f"Ignored: {len(ignored)}")
            message = "Deployment issues detected: " + ", ".join(message_parts)
            return TestResult(False, message)
