from flask import Flask, request, jsonify
import requests
import time
import configparser
from typing import List, Dict, Any
import threading
from queue import Queue
import logging

class LoadBalancer:
    def __init__(self, port: int, services: List[str], next_lb_url: str = None):
        self.port = port
        self.services = services
        self.next_lb_url = next_lb_url
        self.current_service = 0
        self.app = Flask(__name__)
        self.request_queue = Queue()
        self._setup_routes()
        self._start_worker()
        
        # Configurar logging
        logging.basicConfig(
            filename='log.txt',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(f'LoadBalancer_{port}')
    
    def _check_service_availability(self, service_url: str) -> bool:
        try:
            response = requests.get(f"{service_url}/status")
            if response.status_code == 200:
                status = response.json()
                return status.get('is_available', False)
            return False
        except Exception as e:
            self.logger.error(f"Erro ao verificar status do serviço {service_url}: {str(e)}")
            return False
    
    def _find_available_service(self) -> str:
        # Tenta encontrar um serviço disponível, começando do último usado
        start_index = self.current_service
        for _ in range(len(self.services)):
            service_url = self.services[self.current_service]
            if self._check_service_availability(service_url):
                return service_url
            self.current_service = (self.current_service + 1) % len(self.services)
            if self.current_service == start_index:
                break
        return None
    
    def _process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        timestamps = data.get('timestamps', {})
        
        # Registrar T1 ou T3
        if not timestamps.get('T1'):
            timestamps['T1'] = time.time()
        else:
            timestamps['T3'] = time.time()
        
        # Encontrar serviço disponível
        service_url = self._find_available_service()
        if not service_url:
            raise Exception("Nenhum serviço disponível no momento")
        
        try:
            # Enviar para o serviço
            self.logger.info(f"Enviando requisição para serviço: {service_url}")
            response = requests.post(f"{service_url}/process", json={'timestamps': timestamps})
            result = response.json()
            
            # Se houver próximo load balancer, enviar para ele
            if self.next_lb_url:
                self.logger.info(f"Enviando requisição para próximo load balancer: {self.next_lb_url}")
                result = requests.post(f"{self.next_lb_url}/process", json=result).json()
            
            return result
        except Exception as e:
            self.logger.error(f"Erro ao processar requisição: {str(e)}")
            raise
    
    def _worker(self):
        while True:
            try:
                # Pegar requisição da fila
                request_data = self.request_queue.get()
                if request_data is None:
                    break
                
                # Processar requisição
                result = self._process_request(request_data)
                
                # Atualizar resultado na fila
                self.request_queue.task_done()
                
                self.logger.info(f"Requisição processada com sucesso: {result}")
                
            except Exception as e:
                self.logger.error(f"Erro no worker: {str(e)}")
    
    def _start_worker(self):
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()
    
    def _setup_routes(self):
        @self.app.route('/process', methods=['POST'])
        def process():
            try:
                data = request.json
                self.logger.info(f"Nova requisição recebida: {data}")
                
                # Adicionar requisição à fila
                self.request_queue.put(data)
                
                # Processar requisição
                result = self._process_request(data)
                
                return jsonify(result)
            except Exception as e:
                self.logger.error(f"Erro ao receber requisição: {str(e)}")
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