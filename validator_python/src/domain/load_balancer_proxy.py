from typing import Dict, Any, List
from .abstract_proxy import AbstractProxy
import random

class LoadBalancerProxy(AbstractProxy):
    def __init__(self, target_addresses: List[str]):
        super().__init__(target_addresses[0])  # Endereço principal
        self.target_addresses = target_addresses
        self.current_index = 0

    def get_next_target(self) -> str:
        """
        Implementa o algoritmo round-robin para seleção do próximo servidor.
        """
        target = self.target_addresses[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.target_addresses)
        return target

    def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa a requisição usando o algoritmo de balanceamento de carga.
        """
        self.increment_request_count()
        target = self.get_next_target()
        
        # Simula o processamento da requisição
        response = {
            "status": "success",
            "target": target,
            "request_count": self.request_count,
            "data": request_data
        }
        
        return response 