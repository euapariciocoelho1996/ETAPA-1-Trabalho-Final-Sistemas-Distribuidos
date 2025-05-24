from typing import Dict, Any, Optional, List
import random
import requests
from .abstract_proxy import AbstractProxy
from .target_address import TargetAddress
from .source import Source

class LoadBalancerProxy(AbstractProxy):
    def __init__(self, targets: List[TargetAddress], source: Source):
        super().__init__(targets[0], source)  # Usando o primeiro target como padrão
        self.targets = targets
        self.current_index = 0
    
    def _get_next_target(self) -> TargetAddress:
        self.current_index = (self.current_index + 1) % len(self.targets)
        return self.targets[self.current_index]
    
    def forward_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        # Seleciona um target aleatoriamente para balanceamento de carga
        target = random.choice(self.targets)
        url = f"{target.url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, json=data)
        return response.json() 