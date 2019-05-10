from enum import Enum


class TestType(str, Enum):
    CLOSE = 'close'
    OPEN = 'open'


class AttemptStatus(str, Enum):
    PENDING = 'pending'
    NOT_PASSED = 'not passed'
    PASSED = 'passed'
