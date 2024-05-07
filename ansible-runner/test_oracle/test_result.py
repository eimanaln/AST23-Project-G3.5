class TestResult():
    def __init__(self, passed: bool, message: str = ''):
        self.passed = passed
        self.message = message