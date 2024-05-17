from dataclasses import dataclass, field


@dataclass
class TestResult():
    passed: bool
    message: str = ''
