from dataclasses import dataclass, field


@dataclass
class TestResult():
    passed: bool
    message: str = ''
    ports: list[str] = field(default_factory=list)
