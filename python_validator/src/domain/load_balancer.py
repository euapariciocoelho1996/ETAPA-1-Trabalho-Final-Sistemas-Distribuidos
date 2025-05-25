import socket
import threading
import time
from typing import List, Dict
from .abstract_proxy import AbstractProxy
import configparser
import os

class TargetAddress:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

class LoadBalancer(AbstractProxy):
    def __init__(self, config_path: str):
        # Carregar configurações
        config = configparser.ConfigParser()
        config.read(config_path)
        
        super().__init__(
            proxy_name=config['SERVER']['loadBalancerName'],
            local_port=int(config['SERVER']['loadBalancerPort'])
        )
        
        self.queue_max_size = int(config['SERVER']['queueLoadBalancerMaxSize'])
        self.service_addresses = []
        self.services = []
        
        # Configurações dos serviços
        self.service_target_ip = config['SERVICE']['serviceTargetIp']
        self.service_target_port = int(config['SERVICE']['serviceTargetPort'])
        self.service_time = float(config['SERVICE']['serviceTime'])
        self.service_time_std = float(config['SERVICE']['std'])
        self.target_is_source = config['SERVICE'].getboolean('targetIsSource')
        
        # Criar serviços
        self.create_services()
        
        # Aguardar um pouco para os serviços iniciarem
        time.sleep(2)
        
        # Criar conexões com os serviços
        self.create_connection_with_destiny()

    def create_services(self):
        """Cria os serviços configurados"""
        # Portas fixas para os serviços
        if self.local_port == 3000:  # LoadBalancer1
            service_ports = [5002, 5003]
        else:  # LoadBalancer2
            service_ports = [5004, 5005]
        
        for port in service_ports:
            target = TargetAddress("localhost", port)
            self.service_addresses.append(target)

    def create_connection_with_destiny(self):
        """Cria conexões com os serviços"""
        for target in self.service_addresses:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((target.ip, target.port))
                self.connection_destiny_sockets.append(sock)
                print(f"Conectado ao serviço em {target.ip}:{target.port}")
            except Exception as e:
                print(f"Erro ao conectar com serviço {target.ip}:{target.port}: {e}")

    def run(self):
        """Loop principal do load balancer"""
        try:
            # Criar servidor para receber conexões
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(('localhost', self.local_port))
            server.listen(5)
            
            # Thread para receber conexões
            threading.Thread(target=self.accept_connections, args=(server,), daemon=True).start()
            
            # Thread para processar a fila
            threading.Thread(target=self.process_queue, daemon=True).start()
            
            print(f"LoadBalancer {self.proxy_name} iniciado na porta {self.local_port}")
            
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            print(f"Erro no LoadBalancer: {e}")
        finally:
            server.close()

    def accept_connections(self, server: socket.socket):
        """Aceita novas conexões"""
        while self.running:
            try:
                client, addr = server.accept()
                threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
            except:
                break

    def handle_client(self, client: socket.socket):
        """Processa mensagens do cliente"""
        while self.running:
            try:
                data = client.recv(1024).decode()
                if not data:
                    break
                    
                if data == "ping":
                    response = "free" if len(self.queue) < self.queue_max_size else "busy"
                    client.send(response.encode())
                else:
                    # Adicionar timestamp de chegada
                    data = f"{data};{int(time.time() * 1000)};"
                    self.queue.append(data)
                    print(f"Requisição adicionada à fila do {self.proxy_name}")
                    
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")
                break
        client.close()

    def process_queue(self):
        """Processa a fila de mensagens"""
        while self.running:
            if self.has_something_to_process():
                message = self.queue[0]
                sent = False
                
                for socket in self.connection_destiny_sockets:
                    if self.is_destiny_free(socket):
                        print(f"Enviando requisição para serviço em {socket.getpeername()}")
                        self.send_message_to_destiny(message, socket)
                        self.queue.pop(0)
                        sent = True
                        break
                
                if not sent:
                    time.sleep(0.1)
            else:
                time.sleep(0.1)

    @classmethod
    def from_config(cls, config_path: str) -> 'LoadBalancer':
        """Cria um LoadBalancer a partir de um arquivo de configuração"""
        return cls(config_path) 