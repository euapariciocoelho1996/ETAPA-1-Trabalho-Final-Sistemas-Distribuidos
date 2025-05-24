import pytest
from domain.target_address import TargetAddress
from domain.source import Source

@pytest.fixture
def base_target():
    return TargetAddress("http://test.com", 8080)

@pytest.fixture
def base_source():
    return Source("http://localhost", 3000)

@pytest.fixture
def multiple_targets():
    return [
        TargetAddress("http://test1.com", 8080),
        TargetAddress("http://test2.com", 8080),
        TargetAddress("http://test3.com", 8080)
    ] 