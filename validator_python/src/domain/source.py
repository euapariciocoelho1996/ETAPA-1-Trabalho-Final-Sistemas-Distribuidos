import time
import yaml
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import numpy as np
from .load_balancer_proxy import LoadBalancerProxy
from .service_proxy import ServiceProxy
import logging

logger = logging.getLogger(__name__)

class Source:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.request_rate = self.config['source']['request_rate']
        self.target = self.config['source']['target']
        self.metrics_history: List[Dict[str, float]] = []
        
        # Inicializa os LoadBalancers (apenas para simulação de escolha)
        self.lb1 = LoadBalancerProxy(self.config['loadbalancer1']['services'])
        self.lb2 = LoadBalancerProxy(self.config['loadbalancer2']['services'])
        
        logger.info("=== Inicialização do Sistema ===")
        logger.info(f"Source (Nó 01) configurado com taxa de {self.request_rate} req/s")
        logger.info("LoadBalancer1 (Nó 02) configurado com serviços:")
        for service in self.config['loadbalancer1']['services']:
            logger.info(f"  - {service}")
        logger.info("LoadBalancer2 (Nó 03) configurado com serviços:")
        for service in self.config['loadbalancer2']['services']:
            logger.info(f"  - {service}")
        logger.info("===============================")

    def run_experiment(self, duration: int = 60):
        """
        Executa o experimento por um determinado tempo.
        """
        start_time = time.time()
        end_time = start_time + duration
        request_count = 0
        
        logger.info(f"\n=== Iniciando Experimento ({duration}s) ===")
        
        while time.time() < end_time:
            request_count += 1
            # Gera uma requisição
            request_data = {
                "timestamp": time.time(),
                "data": f"test_data_{request_count}"
            }
            
            # Registra o tempo inicial
            t1_start = time.time()
            
            # Envia a requisição (simulada)
            response = self.send_request(request_data, request_count)
            
            # Registra os tempos
            metrics = {
                "t1": response.get("t1", 0),
                "t2": response.get("t2", 0),
                "t3": response.get("t3", 0),
                "t4": response.get("t4", 0),
                "t5": response.get("t5", 0)
            }
            
            self.metrics_history.append(metrics)
            
            # Log a cada 10 requisições
            if request_count % 10 == 0:
                logger.info(f"\n=== Resumo da Requisição {request_count} ===")
                logger.info(f"Tempos:")
                logger.info(f"  T1 (Cliente->LB1): {metrics['t1']:.3f}s")
                logger.info(f"  T2 (LB1->Serviço): {metrics['t2']:.3f}s")
                logger.info(f"  T3 (Processamento): {metrics['t3']:.3f}s")
                logger.info(f"  T4 (Serviço->Cliente): {metrics['t4']:.3f}s")
                logger.info(f"  T5 (Tempo Total): {metrics['t5']:.3f}s")
                logger.info("=============================")
            
            # Aguarda o intervalo correto baseado na taxa de requisições
            time.sleep(1.0 / self.request_rate)

        logger.info(f"\n=== Experimento Concluído ===")
        logger.info(f"Total de requisições: {request_count}")
        self._print_summary()

    def _print_summary(self):
        """
        Imprime um resumo das métricas coletadas.
        """
        if not self.metrics_history:
            return

        t1_avg = np.mean([m["t1"] for m in self.metrics_history])
        t2_avg = np.mean([m["t2"] for m in self.metrics_history])
        t3_avg = np.mean([m["t3"] for m in self.metrics_history])
        t4_avg = np.mean([m["t4"] for m in self.metrics_history])
        t5_avg = np.mean([m["t5"] for m in self.metrics_history])

        logger.info("\n=== Resumo das Médias ===")
        logger.info(f"Tempo Médio T1 (Cliente->LB1): {t1_avg:.3f}s")
        logger.info(f"Tempo Médio T2 (LB1->Serviço): {t2_avg:.3f}s")
        logger.info(f"Tempo Médio T3 (Processamento): {t3_avg:.3f}s")
        logger.info(f"Tempo Médio T4 (Serviço->Cliente): {t4_avg:.3f}s")
        logger.info(f"Tempo Médio T5 (Tempo Total): {t5_avg:.3f}s")
        logger.info(f"MRT (Mean Response Time): {t5_avg:.3f}s")
        logger.info("===========================")

    def send_request(self, request_data: Dict[str, Any], request_num: int) -> Dict[str, Any]:
        """
        Envia uma requisição para o sistema (simulado) e registra os tempos.
        """
        # Simula tempos de processamento e rede
        t1 = 0.1 + np.random.normal(0, 0.02)  # Tempo de rede cliente->LB1
        t2_process = 0.05 + np.random.normal(0, 0.01) # Tempo LB1->Serviço e LB1 processamento
        t3_process = 0.2 + np.random.normal(0, 0.03)  # Tempo de processamento do Serviço
        t4_return = 0.1 + np.random.normal(0, 0.02)  # Tempo Serviço->Cliente

        # Simula seleção de serviços pelos LoadBalancers
        # Note: Em uma implementação real, LB1 enviaria para um Serviço1.x, que por sua vez enviaria para LB2, e então para um Serviço2.x.
        # Aqui, simulamos a escolha final para o log.
        lb1_service = np.random.choice(self.config['loadbalancer1']['services'])
        lb2_service = np.random.choice(self.config['loadbalancer2']['services'])

        # Log do fluxo simulado (a cada 10 requisições para não poluir demais o log)
        if request_num % 10 == 0:
            logger.info(f"---> Fluxo Simulado Req {request_num}:")
            logger.info(f"     Nó 01 (Source) -> Nó 02 (LB1) [~{t1:.3f}s]")
            logger.info(f"     Nó 02 (LB1) -> Serviço (escolhido: {lb1_service}) [~{t2_process:.3f}s]")
            # Em um fluxo real, o serviço 1.x processaria e enviaria para o LB2
            logger.info(f"     Serviço ({lb1_service}) -> Nó 03 (LB2) [Simulado no T3] ") # Simplified for simulation
            logger.info(f"     Nó 03 (LB2) -> Serviço (escolhido: {lb2_service}) [Simulado no T3] ") # Simplified for simulation
            logger.info(f"     Serviço ({lb2_service}) Processamento [~{t3_process:.3f}s]") # This is the T3
            logger.info(f"     Serviço ({lb2_service}) -> Nó 01 (Source) [~{t4_return:.3f}s]")
            logger.info("<---")

        t5 = t1 + t2_process + t3_process + t4_return

        return {
            "status": "success",
            "t1": max(0, t1),
            "t2": max(0, t2_process), # Reusing t2 for LB1->Service simulation
            "t3": max(0, t3_process), # Reusing t3 for Service Processing simulation
            "t4": max(0, t4_return),  # Reusing t4 for Service->Client return simulation
            "t5": max(0, t5),
            "lb1_service": lb1_service,
            "lb2_service": lb2_service
        }

    def generate_graphs(self):
        """
        Gera gráficos de desempenho.
        """
        # Prepara os dados
        times = np.array([m["t5"] for m in self.metrics_history])
        # Ajusta request_rates para ter o mesmo tamanho de times, representando a taxa ao longo do tempo
        request_rates_over_time = np.full(len(times), self.request_rate) # Assuming constant rate for now
        
        # Cria o gráfico
        plt.figure(figsize=(10, 6))
        plt.plot(request_rates_over_time, times, 'o-', label='MRT por Requisição', alpha=0.6)
        
        # Calcula e plota o MRT médio geral como uma linha horizontal
        if times.size > 0:
            mrt_medio_geral = np.mean(times)
            plt.axhline(y=mrt_medio_geral, color='r', linestyle='-', label=f'MRT Médio Geral: {mrt_medio_geral:.3f}s')
            logger.info(f"MRT Médio Geral calculado: {mrt_medio_geral:.3f}s")

        plt.xlabel('Taxa de Geração (req/s)') # Pode ser constante neste caso simulado
        plt.ylabel('Tempo de Resposta Total (s)') # Ajustado para Tempo Total para cada ponto
        plt.title('Tempo de Resposta por Requisição ao Longo do Experimento')
        plt.legend()
        plt.grid(True)
        
        # Salva o gráfico
        plt.savefig('performance_graph.png')
        plt.close()
        
        logger.info("\n=== Gráfico Gerado ===")
        logger.info("Arquivo: performance_graph.png")
        logger.info("=====================") 