from typing import Dict, Any, Optional
import requests
from .abstract_proxy import AbstractProxy

class ServiceProxy(AbstractProxy):
    def forward_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.target.url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, json=data)
        return response.json() 