from dataclasses import dataclass
from typing import Generator

from ansible_runner import RunnerConfig


@dataclass
class DeploymentData():
    # TODO: Adapt as needed
    runner_config: RunnerConfig
    events: Generator
    stats: dict
