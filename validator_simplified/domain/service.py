from flask import Flask, request, jsonify
import time
import configparser
import threading

class Service:
    def __init__(self, port: int, processing_time: float = 1.0):
        self.port = port
        self.processing_time = processing_time
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.route('/process', methods=['POST'])
        def process():
            data = request.json
            timestamps = data.get('timestamps', {})
            
            # Registrar T2 ou T4
            if not timestamps.get('T2'):
                timestamps['T2'] = time.time()
            else:
                timestamps['T4'] = time.time()
            
            # Simular processamento
            time.sleep(self.processing_time)
            
            return jsonify({'timestamps': timestamps})
    
    def start(self):
        self.app.run(host='0.0.0.0', port=self.port)
    
    @classmethod
    def from_config(cls, config_path: str, port: int):
        config = configparser.ConfigParser()
        config.read(config_path)
        
        processing_time = float(config['DEFAULT'].get('processing_time', 1.0))
        return cls(port, processing_time) 