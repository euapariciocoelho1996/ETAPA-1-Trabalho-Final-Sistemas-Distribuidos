import threading
import time
import configparser
import requests
from domain.load_balancer import LoadBalancer
from domain.service import Service
import matplotlib.pyplot as plt
import csv
import os

# Obter o diretório base do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGS_DIR = os.path.join(BASE_DIR, 'src', 'configs')

def start_services():
    """Inicia todos os componentes do sistema"""
    threads = []
    
    # Iniciar serviços do primeiro nível
    service1_1 = Service.from_config(os.path.join(CONFIGS_DIR, 'service.properties'), 5002)
    service1_2 = Service.from_config(os.path.join(CONFIGS_DIR, 'service.properties'), 5003)
    
    # Iniciar serviços do segundo nível
    service2_1 = Service.from_config(os.path.join(CONFIGS_DIR, 'service.properties'), 5004)
    service2_2 = Service.from_config(os.path.join(CONFIGS_DIR, 'service.properties'), 5005)
    
    # Iniciar todos os serviços primeiro
    threads.extend([
        service1_1.start(),
        service1_2.start(),
        service2_1.start(),
        service2_2.start()
    ])
    
    # Aguardar os serviços iniciarem
    time.sleep(2)
    
    # Iniciar load balancers depois
    lb1 = LoadBalancer.from_config(os.path.join(CONFIGS_DIR, 'loadbalancer1.properties'))
    lb2 = LoadBalancer.from_config(os.path.join(CONFIGS_DIR, 'loadbalancer2.properties'))
    
    threads.extend([
        lb1.start(),
        lb2.start()
    ])
    
    return threads

def run_experiment():
    """Executa o experimento"""
    # Carregar configuração do source
    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIGS_DIR, 'source.properties'))
    
    lb1_url = f"http://localhost:{config['DEFAULT']['variatingServices.variatedServerLoadBalancerPort']}"
    rate = float(config['DEFAULT']['variatingServices.arrivalDelay'])
    num_requests = int(config['DEFAULT']['maxConsideredMessagesExpected'])
    
    results = []
    
    print(f"Iniciando experimento...")
    print(f"Conectando ao LoadBalancer1 em: {lb1_url}")
    print(f"Taxa de geração: {rate} requisições/segundo")
    print(f"Número de requisições: {num_requests}")
    
    for i in range(num_requests):
        try:
            # Preparar payload com timestamp inicial
            payload = {
                "data": f"request_{i}",
                "timestamps": {"T0": time.time()}
            }
            
            print(f"\nEnviando requisição {i+1}...")
            resp = requests.post(f"{lb1_url}/process", json=payload)
            result = resp.json()
            
            # Adicionar timestamp final
            result['timestamps']['T5'] = time.time()
            results.append(result['timestamps'])
            
            # Calcular e mostrar tempos intermediários
            ts = result['timestamps']
            t0 = float(ts.get('T0', 0))
            t1 = float(ts.get('T1', 0))
            t2 = float(ts.get('T2', 0))
            t3 = float(ts.get('T3', 0))
            t4 = float(ts.get('T4', 0))
            t5 = float(ts.get('T5', 0))
            
            print(f"T0 (Início no Source): {t0:.3f} | T1 (Chegada no LB01): {t1:.3f} | ΔT1 (Source -> LB01): {(t1-t0)*1000:.2f} ms")
            print(f"T2 (Saída do LB01 / Chegada no S01): {t2:.3f} | ΔT2 (LB01 -> S01): {(t2-t1)*1000:.2f} ms")
            print(f"T3 (Saída do S01 / Chegada no LB02): {t3:.3f} | ΔT3 (S01 -> LB02): {(t3-t2)*1000:.2f} ms")
            print(f"T4 (Saída do LB02 / Chegada no S02): {t4:.3f} | ΔT4 (LB02 -> S02): {(t4-t3)*1000:.2f} ms")
            print(f"T5 (Saída do S02 / Fim no Source): {t5:.3f} | ΔT5 (S02 -> Source): {(t5-t4)*1000:.2f} ms")
            print(f"TEMPO TOTAL (Source -> S02 -> Source): {(t5-t0)*1000:.2f} ms")
            
            # Aguardar conforme a taxa de geração
            time.sleep(1/rate)
            
        except Exception as e:
            print(f"Erro ao processar requisição {i+1}: {str(e)}")
            continue
    
    # Salvar resultados
    results_path = os.path.join(BASE_DIR, 'results.csv')
    print("\nSalvando resultados em results.csv...")
    with open(results_path, 'w') as f:
        f.write("T0,T1,T2,T3,T4,T5\n")
        for r in results:
            f.write(','.join(str(r.get(f"T{i}", "")) for i in range(6)) + '\n')
    print("Resultados salvos com sucesso!")
    generate_mrt_graph(results_path, os.path.join(BASE_DIR, 'mrt_graph.png'))

def generate_mrt_graph(results_path='results.csv', output_path='mrt_graph.png'):
    """Gera gráfico do MRT"""
    mrt_list = []
    with open(results_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                t0 = float(row['T0'])
                t5 = float(row['T5'])
                mrt = (t5 - t0) * 1000  # em ms
                mrt_list.append(mrt)
            except Exception:
                continue
    
    if not mrt_list:
        print('Nenhum dado para gerar gráfico.')
        return
        
    plt.figure(figsize=(8,6))
    plt.plot(range(1, len(mrt_list)+1), mrt_list, marker='o', color='blue', label='MRT')
    plt.xlabel('Número da Requisição')
    plt.ylabel('MRT (ms)')
    plt.title('Tempo Médio de Resposta por Requisição')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    print(f'Gráfico salvo em {output_path}')

def main():
    """Função principal"""
    # Iniciar todos os componentes
    threads = start_services()
    
    # Aguardar um pouco para garantir que todos os componentes iniciaram
    time.sleep(2)
    
    # Executar o experimento
    run_experiment()
    
    # Manter o programa rodando
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando o sistema...")

if __name__ == "__main__":
    main() 