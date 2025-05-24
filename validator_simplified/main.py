from domain.source import Source
from domain.service_proxy import ServiceProxy
from domain.load_balancer_proxy import LoadBalancerProxy
from domain.target_address import TargetAddress

def main():
    # Exemplo de uso
    target = TargetAddress("http://example.com", 8080)
    source = Source("http://localhost", 3000)
    
    # Criando um proxy de serviço
    service_proxy = ServiceProxy(target, source)
    
    # Criando um proxy de balanceamento de carga
    load_balancer = LoadBalancerProxy([target], source)
    
    print("Sistema iniciado com sucesso!")

if __name__ == "__main__":
    main() 