from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .source import Source
from .target_address import TargetAddress

class AbstractProxy(ABC):
    def __init__(self, target: TargetAddress, source: Source):
        self.target = target
        self.source = source
    
    @abstractmethod
    def forward_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        pass
    
    def __str__(self) -> str:
        return f"Proxy({self.target} -> {self.source})" 