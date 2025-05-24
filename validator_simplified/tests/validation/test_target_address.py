import pytest
from domain.target_address import TargetAddress

def test_target_address_initialization():
    target = TargetAddress("http://test.com", 8080)
    assert target.host == "http://test.com"
    assert target.port == 8080

def test_target_address_url():
    target = TargetAddress("http://test.com", 8080)
    assert target.url == "http://test.com:8080"

def test_target_address_str():
    target = TargetAddress("http://test.com", 8080)
    assert str(target) == "http://test.com:8080" 