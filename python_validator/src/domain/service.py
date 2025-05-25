import socket
import threading
import time
import random
from .abstract_proxy import AbstractProxy
from .load_balancer import TargetAddress
import configparser

class Service(AbstractProxy):
    def __init__(self, service_name: str, local_port: int, target_address, service_time: float, std: float, target_is_source: bool):
        super().__init__(service_name, local_port)
        self.target_address = target_address
        self.service_time = service_time
        self.std = std
        self.target_is_source = target_is_source
        self.processing = False

    def run(self):
        """Loop principal do serviço"""
        try:
            # Criar servidor para receber conexões
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(('localhost', self.local_port))
            server.listen(5)
            
            print(f"Serviço {self.proxy_name} iniciado na porta {self.local_port}")
            
            while self.running:
                try:
                    client, addr = server.accept()
                    threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
                except:
                    break
                    
        except Exception as e:
            print(f"Erro no Serviço {self.proxy_name}: {e}")
        finally:
            server.close()

    def handle_client(self, client: socket.socket):
        """Processa mensagens do cliente"""
        while self.running:
            try:
                data = client.recv(1024).decode()
                if not data:
                    break
                    
                if data == "ping":
                    response = "free" if not self.processing else "busy"
                    client.send(response.encode())
                else:
                    # Adicionar timestamp de chegada
                    data = f"{data};{int(time.time() * 1000)};"
                    self.process_message(data)
                    
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")
                break
        client.close()

    def process_message(self, message: str):
        """Processa uma mensagem"""
        self.processing = True
        try:
            # Simular tempo de processamento
            processing_time = random.gauss(self.service_time, self.std)
            time.sleep(processing_time / 1000)  # Converter para segundos
            
            # Adicionar timestamp de saída
            message = f"{message}{int(time.time() * 1000)};"
            
            # Enviar para o próximo destino
            if not self.target_is_source:
                print(f"Enviando mensagem para {self.target_address.ip}:{self.target_address.port}")
                self.send_to_next_target(message)
                
        except Exception as e:
            print(f"Erro no processamento: {e}")
        finally:
            self.processing = False

    def send_to_next_target(self, message: str):
        """Envia mensagem para o próximo destino"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.target_address.ip, self.target_address.port))
            sock.send(message.encode())
            sock.close()
            print(f"Mensagem enviada com sucesso para {self.target_address.ip}:{self.target_address.port}")
        except Exception as e:
            print(f"Erro ao enviar para próximo destino ({self.target_address.ip}:{self.target_address.port}): {e}")

    @classmethod
    def from_config(cls, config_path: str, port: int) -> 'Service':
        """Cria um Service a partir de um arquivo de configuração"""
        config = configparser.ConfigParser()
        config.read(config_path)
        
        target_address = TargetAddress(
            config['SERVICE']['serviceTargetIp'],
            int(config['SERVICE']['serviceTargetPort'])
        )
        
        return cls(
            service_name=f"service_{port}",
            local_port=port,
            target_address=target_address,
            service_time=float(config['SERVICE']['serviceTime']),
            std=float(config['SERVICE']['std']),
            target_is_source=config['SERVICE'].getboolean('targetIsSource')
        ) 