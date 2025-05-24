import pytest
from unittest.mock import Mock, patch
from domain.load_balancer_proxy import LoadBalancerProxy
from domain.target_address import TargetAddress
from domain.source import Source

@pytest.fixture
def targets():
    return [
        TargetAddress("http://test1.com", 8080),
        TargetAddress("http://test2.com", 8080),
        TargetAddress("http://test3.com", 8080)
    ]

@pytest.fixture
def source():
    return Source("http://localhost", 3000)

@pytest.fixture
def load_balancer(targets, source):
    return LoadBalancerProxy(targets, source)

def test_load_balancer_initialization(targets, source):
    proxy = LoadBalancerProxy(targets, source)
    assert proxy.targets == targets
    assert proxy.source == source
    assert proxy.current_index == 0

def test_get_next_target(load_balancer, targets):
    # Testa a rotação dos targets
    assert load_balancer._get_next_target() == targets[1]
    assert load_balancer._get_next_target() == targets[2]
    assert load_balancer._get_next_target() == targets[0]

@patch('requests.request')
def test_forward_request(mock_request, load_balancer):
    # Configurar o mock
    mock_response = Mock()
    mock_response.json.return_value = {"status": "success"}
    mock_request.return_value = mock_response

    # Testar o forward_request
    result = load_balancer.forward_request("GET", "/api/test", {"data": "test"})

    # Verificar se a requisição foi feita corretamente
    mock_request.assert_called_once()
    assert result == {"status": "success"}
    
    # Verificar se o URL usado está entre os targets disponíveis
    called_url = mock_request.call_args[0][1]
    assert any(target.url in called_url for target in load_balancer.targets) 