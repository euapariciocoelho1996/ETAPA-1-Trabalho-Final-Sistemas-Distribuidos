import pytest
from unittest.mock import Mock, patch
from domain.source import Source

@pytest.fixture
def source():
    return Source("http://localhost", 3000)

def test_source_initialization():
    source = Source("http://test.com", 8080)
    assert source.host == "http://test.com"
    assert source.port == 8080
    assert source.url == "http://test.com:8080"

@patch('requests.Session')
def test_make_request(mock_session_class, source):
    # Configurar o mock da sessão
    mock_session = Mock()
    mock_session_class.return_value = mock_session
    mock_response = Mock()
    mock_session.request.return_value = mock_response

    # Substituir a sessão real pelo mock
    source._session = mock_session

    # Testar o make_request
    response = source.make_request("GET", "/api/test", {"data": "test"})

    # Verificar se a requisição foi feita corretamente
    mock_session.request.assert_called_once_with(
        "GET",
        "http://localhost:3000/api/test",
        json={"data": "test"}
    )
    assert response == mock_response 