import socket
import threading
import time
from typing import List, Optional

class AbstractProxy:
    def __init__(self, proxy_name: str, local_port: int):
        self.proxy_name = proxy_name
        self.local_port = local_port
        self.queue = []
        self.connection_destiny_sockets = []
        self.target_address = None
        self.running = True

    def start(self):
        """Inicia o proxy em uma nova thread"""
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()
        return thread

    def run(self):
        """Método principal que deve ser implementado pelas classes filhas"""
        raise NotImplementedError

    def create_connection_with_destiny(self):
        """Cria conexão com o destino"""
        raise NotImplementedError

    def has_something_to_process(self) -> bool:
        """Verifica se há algo para processar na fila"""
        return len(self.queue) > 0

    def is_destiny_free(self, socket: socket.socket) -> bool:
        """Verifica se o destino está livre"""
        try:
            socket.send(b"ping")
            response = socket.recv(1024).decode()
            return response == "free"
        except:
            return False

    def send_message_to_destiny(self, message: str, socket: socket.socket):
        """Envia mensagem para o destino"""
        try:
            socket.send(message.encode())
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

    def stop(self):
        """Para o proxy"""
        self.running = False
        for socket in self.connection_destiny_sockets:
            try:
                socket.close()
            except:
                pass 