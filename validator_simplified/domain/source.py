import requests
from typing import Dict, Any, Optional

class Source:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._session = requests.Session()
    
    @property
    def url(self) -> str:
        return f"{self.host}:{self.port}"
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = f"{self.url}/{endpoint.lstrip('/')}"
        return self._session.request(method, url, json=data)
    
    def __str__(self) -> str:
        return self.url 