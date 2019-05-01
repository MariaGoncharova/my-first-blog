from enum import Enum


class TestType(str, Enum):
    CLOSE = 'close'
    OPEN = 'open'
