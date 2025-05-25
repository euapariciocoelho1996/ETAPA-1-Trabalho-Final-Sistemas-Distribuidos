"""
Sistema Distribuído de Validação com 3 Nós

Estrutura do Sistema:
1. Nó 01 (Source) - Gera requisições e compila resultados
2. Nó 02 (LoadBalancer1 + Services) - Primeiro nível de processamento
3. Nó 03 (LoadBalancer2 + Services) - Segundo nível de processamento

Fluxo de Dados:
Source -> LoadBalancer1 -> Service1.1/1.2 -> LoadBalancer2 -> Service2.1/2.2 -> Source
"""

import threading
import time
import configparser
import requests
from domain.load_balancer import LoadBalancer
from domain.service import Service
import matplotlib.pyplot as plt
import csv

def start_services():
    """
    Inicializa todos os componentes do sistema distribuído:
    - Nó 02: Service1.1 (porta 5002) e Service1.2 (porta 5003)
    - Nó 03: Service2.1 (porta 5004) e Service2.2 (porta 5005)
    - LoadBalancer1: Distribui requisições para os serviços do Nó 02
    - LoadBalancer2: Distribui requisições para os serviços do Nó 03
    """
    # Iniciar serviços do primeiro nível (Nó 02)
    service1_1 = Service.from_config('configs/service.properties', 5002)
    service1_2 = Service.from_config('configs/service.properties', 5003)
    
    # Iniciar serviços do segundo nível (Nó 03)
    service2_1 = Service.from_config('configs/service.properties', 5004)
    service2_2 = Service.from_config('configs/service.properties', 5005)
    
    # Iniciar load balancers
    lb1 = LoadBalancer.from_config('configs/loadbalancer1.properties')  # Nó 02
    lb2 = LoadBalancer.from_config('configs/loadbalancer2.properties')  # Nó 03
    
    # Iniciar todos os componentes em threads separadas
    threads = [
        threading.Thread(target=service1_1.start),
        threading.Thread(target=service1_2.start),
        threading.Thread(target=service2_1.start),
        threading.Thread(target=service2_2.start),
        threading.Thread(target=lb1.start),
        threading.Thread(target=lb2.start)
    ]
    
    for thread in threads:
        thread.daemon = True
        thread.start()
    
    return threads

def run_experiment():
    """
    Nó 01 (Source): 
    - Gera requisições com timestamps
    - Envia para LoadBalancer1
    - Recebe resultados
    - Calcula tempos de resposta
    - Gera gráficos de performance
    """
    # Carregar configuração do source (Nó 01)
    config = configparser.ConfigParser()
    config.read('configs/source.properties')
    
    lb1_url = config['DEFAULT']['lb1_url']
    rate = float(config['DEFAULT']['generation_rate'])
    num_requests = int(config['DEFAULT']['num_requests'])
    
    results = []
    
    print(f"Iniciando experimento...")
    print(f"Conectando ao LoadBalancer1 em: {lb1_url}")
    print(f"Taxa de geração: {rate} requisições/segundo")
    print(f"Número de requisições: {num_requests}")
    
    for i in range(num_requests):
        try:
            # Preparar payload com timestamp inicial (Nó 01 - Source)
            payload = {
                "data": f"request_{i}",
                "timestamps": {"T0": time.time()}
            }
            
            print(f"\nEnviando requisição {i+1}...")
            # Enviar para LoadBalancer1 (Nó 02)
            resp = requests.post(f"{lb1_url}/process", json=payload)
            result = resp.json()
            
            # Adicionar timestamp final (Nó 01 - Source)
            result['timestamps']['T5'] = time.time()
            results.append(result['timestamps'])
            
            # Calcular e mostrar tempos intermediários
            ts = result['timestamps']
            t0 = float(ts.get('T0', 0))  # Nó 01 - Source
            t1 = float(ts.get('T1', 0))  # Nó 02 - LoadBalancer1
            t2 = float(ts.get('T2', 0))  # Nó 02 - Service1.1/1.2
            t3 = float(ts.get('T3', 0))  # Nó 03 - LoadBalancer2
            t4 = float(ts.get('T4', 0))  # Nó 03 - Service2.1/2.2
            t5 = float(ts.get('T5', 0))  # Nó 01 - Source (retorno)
            
            # Mostrar tempos de cada etapa do processamento
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
    print("\nSalvando resultados em results.csv...")
    with open('results.csv', 'w') as f:
        f.write("T0,T1,T2,T3,T4,T5\n")
        for r in results:
            f.write(','.join(str(r.get(f"T{i}", "")) for i in range(6)) + '\n')
    print("Resultados salvos com sucesso!")
    gerar_grafico_mrt('results.csv', 'mrt_graph.png')

def gerar_grafico_mrt(results_path='results.csv', output_path='mrt_graph.png'):
    """
    Gera gráfico de tempo médio de resposta (MRT) para todas as requisições
    """
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
    """
    Função principal que:
    1. Inicia todos os componentes do sistema
    2. Executa o experimento
    3. Mantém o sistema rodando até interrupção
    """
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