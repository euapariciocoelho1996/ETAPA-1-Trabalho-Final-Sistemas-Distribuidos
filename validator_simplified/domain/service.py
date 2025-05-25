from flask import Flask, request, jsonify
import time
import configparser
import threading
from queue import Queue
import logging

class Service:
    def __init__(self, port: int, processing_time: float = 1.0):
        self.port = port
        self.processing_time = processing_time
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
        self.logger = logging.getLogger(f'Service_{port}')
    
    def _process_request(self, data):
        timestamps = data.get('timestamps', {})
        
        # Registrar T2 ou T4
        if not timestamps.get('T2'):
            timestamps['T2'] = time.time()
        else:
            timestamps['T4'] = time.time()
        
        # Simular processamento
        time.sleep(self.processing_time)
        
        return {'timestamps': timestamps}
    
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
                self.logger.error(f"Erro ao processar requisição: {str(e)}")
    
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
    def from_config(cls, config_path: str, port: int):
        config = configparser.ConfigParser()
        config.read(config_path)
        
        processing_time = float(config['DEFAULT'].get('processing_time', 1.0))
        return cls(port, processing_time) 