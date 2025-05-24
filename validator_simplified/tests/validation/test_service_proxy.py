import pytest
from unittest.mock import Mock, patch
from domain.service_proxy import ServiceProxy
from domain.target_address import TargetAddress
from domain.source import Source

@pytest.fixture
def target():
    return TargetAddress("http://test.com", 8080)

@pytest.fixture
def source():
    return Source("http://localhost", 3000)

@pytest.fixture
def service_proxy(target, source):
    return ServiceProxy(target, source)

def test_service_proxy_initialization(target, source):
    proxy = ServiceProxy(target, source)
    assert proxy.target == target
    assert proxy.source == source

@patch('requests.request')
def test_forward_request(mock_request, service_proxy):
    # Configurar o mock
    mock_response = Mock()
    mock_response.json.return_value = {"status": "success"}
    mock_request.return_value = mock_response

    # Testar o forward_request
    result = service_proxy.forward_request("GET", "/api/test", {"data": "test"})

    # Verificar se a requisição foi feita corretamente
    mock_request.assert_called_once_with(
        "GET",
        "http://test.com:8080/api/test",
        json={"data": "test"}
    )
    assert result == {"status": "success"} 