from flask import Flask, request, jsonify
import requests
import time
import configparser
from typing import List, Dict, Any
import threading

class LoadBalancer:
    def __init__(self, port: int, services: List[str], next_lb_url: str = None):
        self.port = port
        self.services = services
        self.next_lb_url = next_lb_url
        self.current_service = 0
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.route('/process', methods=['POST'])
        def process():
            data = request.json
            timestamps = data.get('timestamps', {})
            
            # Registrar T1 ou T3
            if not timestamps.get('T1'):
                timestamps['T1'] = time.time()
            else:
                timestamps['T3'] = time.time()
            
            # Selecionar próximo serviço
            service_url = self.services[self.current_service]
            self.current_service = (self.current_service + 1) % len(self.services)
            
            try:
                # Enviar para o serviço
                response = requests.post(f"{service_url}/process", json={'timestamps': timestamps})
                result = response.json()
                
                # Se houver próximo load balancer, enviar para ele
                if self.next_lb_url:
                    result = requests.post(f"{self.next_lb_url}/process", json=result).json()
                
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def start(self):
        self.app.run(host='0.0.0.0', port=self.port)
    
    @classmethod
    def from_config(cls, config_path: str):
        config = configparser.ConfigParser()
        config.read(config_path)
        
        port = int(config['DEFAULT']['port'])
        services = [
            config['DEFAULT']['service1_url'],
            config['DEFAULT']['service2_url']
        ]
        next_lb_url = config['DEFAULT'].get('lb2_url', None)
        
        return cls(port, services, next_lb_url) 