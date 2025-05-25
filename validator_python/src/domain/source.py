import time
import yaml
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import numpy as np
from .load_balancer_proxy import LoadBalancerProxy
from .service_proxy import ServiceProxy
import logging
from datetime import datetime

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
                "t1_source_lb1": response.get("t1_source_lb1", 0),
                "t2_lb1_service": response.get("t2_lb1_service", 0),
                "t3_service_lb2": response.get("t3_service_lb2", 0),
                "t4_lb2_service": response.get("t4_lb2_service", 0),
                "t_processamento": response.get("t_processamento", 0),
                "t5_service_source": response.get("t5_service_source", 0),
                "t5_total": response.get("t5_total", 0),
                "average_intermediate": response.get("average_intermediate", 0)
            }
            
            self.metrics_history.append(metrics)
            
            # Log a cada 10 requisições
            if request_count % 10 == 0:
                logger.info(f"\n=== Resumo da Requisição {request_count} ===")
                logger.info(f"Tempos:")
                logger.info(f"  T1 (Source -> LB1): {metrics['t1_source_lb1']:.3f}s")
                logger.info(f"  T2 (LB1 -> Serviço): {metrics['t2_lb1_service']:.3f}s")
                logger.info(f"  T3 (Serviço S1 -> LB2): {metrics['t3_service_lb2']:.3f}s")
                logger.info(f"  T4 (LB2 -> Serviço): {metrics['t4_lb2_service']:.3f}s")
                logger.info(f"  T5 (Processamento Serviço): {metrics['t_processamento']:.3f}s")
                logger.info(f"  T5 (Serviço S2 -> Source): {metrics['t5_service_source']:.3f}s")
                logger.info(f"  T5 (Tempo Total): {metrics['t5_total']:.3f}s")
                logger.info(f"  Média dos Tempos Intermediários: {metrics['average_intermediate']:.3f}s")
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

        # Atualiza para usar as novas chaves das métricas
        t1_avg = np.mean([m["t1_source_lb1"] for m in self.metrics_history])
        t2_avg = np.mean([m["t2_lb1_service"] for m in self.metrics_history])
        t3_lb2_avg = np.mean([m["t3_service_lb2"] for m in self.metrics_history])
        t4_service_avg = np.mean([m["t4_lb2_service"] for m in self.metrics_history])
        t5_return_avg = np.mean([m["t5_service_source"] for m in self.metrics_history])
        t_process_avg = np.mean([m["t_processamento"] for m in self.metrics_history])
        t5_total_avg = np.mean([m["t5_total"] for m in self.metrics_history])
        average_intermediate_avg = np.mean([m["average_intermediate"] for m in self.metrics_history])

        logger.info("\n=== Resumo das Médias ===")
        # Atualiza as labels para corresponderem ao fluxo e diagrama
        logger.info(f"Tempo Médio T1 (Source -> LB1): {t1_avg:.3f}s")
        logger.info(f"Tempo Médio T2 (LB1 -> Serviço): {t2_avg:.3f}s")
        logger.info(f"Tempo Médio (Serviço S1 -> LB2): {t3_lb2_avg:.3f}s") # Correspondente a T3 no diagrama
        logger.info(f"Tempo Médio (LB2 -> Serviço S2): {t4_service_avg:.3f}s") # Correspondente a T4 no diagrama
        logger.info(f"Tempo Médio (Processamento Serviço S2): {t_process_avg:.3f}s") # Tempo de processamento real
        logger.info(f"Tempo Médio T5 (Serviço S2 -> Source): {t5_return_avg:.3f}s") # Correspondente a T5 no diagrama
        logger.info(f"MRT (Tempo Total da Requisição): {t5_total_avg:.3f}s")
        logger.info(f"Média dos Tempos Intermediários: {average_intermediate_avg:.3f}s")
        logger.info("===========================")

    def send_request(self, request_data: Dict[str, Any], request_num: int) -> Dict[str, Any]:
        """
        Envia uma requisição para o sistema (simulado) e registra os tempos.
        """
        # Simula tempos de processamento e rede
        # Estes são agora as *durações simuladas* para os segmentos
        duration_source_lb1 = 0.1 + np.random.normal(0, 0.02)  # T1 no diagrama
        duration_lb1_service = 0.05 + np.random.normal(0, 0.01) # T2 no diagrama
        duration_service_process = 0.2 + np.random.normal(0, 0.03)  # Tempo de processamento TOTAL do Serviço S2
        # Dividindo o tempo do diagrama T3 e T4, que incluem trânsito e uma parte do processamento
        duration_service_lb2 = 0.05 + np.random.normal(0, 0.01) # Simula tempo S1 -> LB2 (Diagrama T3)
        duration_lb2_service = 0.05 + np.random.normal(0, 0.01) # Simula tempo LB2 -> S2 (Diagrama T4)
        duration_service_return = 0.1 + np.random.normal(0, 0.02)  # T5 no diagrama

        # Simula seleção de serviços pelos LoadBalancers
        lb1_service = np.random.choice(self.config['loadbalancer1']['services'])
        lb2_service = np.random.choice(self.config['loadbalancer2']['services'])

        # Log do fluxo simulado (a cada 10 requisições para não poluir demais o log)
        if request_num % 10 == 0:
            logger.info(f"---> Fluxo Simulado Req {request_num}:")

            # M1: Source envia requisição
            m1_time = time.time()
            current_time_str = datetime.fromtimestamp(m1_time).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
            # Log Source -> LB1 (usando T1 = duração simulada Source->LB1)
            logger.info(f"{current_time_str} - domain.source - INFO -      Nó 01 (Source) -> Nó 02 (LB1) [~{duration_source_lb1:.3f}s]")

            # M2: Requisição chega no LB1
            m2_time = m1_time + duration_source_lb1
            current_time_str = datetime.fromtimestamp(m2_time).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
            # Log LB1 -> Serviço S1 (usando T2 = duração simulada LB1->Serviço)
            logger.info(f"{current_time_str} - domain.source - INFO -      Nó 02 (LB1) -> Serviço (escolhido: {lb1_service}) [~{duration_lb1_service:.3f}s]")

            # M3: Requisição chega no S01 (Serviço) e envia para LB2
            m3_time = m2_time + duration_lb1_service
            current_time_str = datetime.fromtimestamp(m3_time).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
            # Log Serviço S1 -> LB2 (usando duração simulada Serviço->LB2, Diagrama T3)
            logger.info(f"{current_time_str} - domain.source - INFO -      Serviço ({lb1_service}) -> Nó 03 (LB2) [~{duration_service_lb2:.3f}s]")

            # M4: Requisição chega no LB2 e envia para Serviço S2
            m4_time = m3_time + duration_service_lb2
            current_time_str = datetime.fromtimestamp(m4_time).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
            # Log LB2 -> Serviço S2 (usando duração simulada LB2->Serviço, Diagrama T4)
            logger.info(f"{current_time_str} - domain.source - INFO -      Nó 03 (LB2) -> Serviço (escolhido: {lb2_service}) [~{duration_lb2_service:.3f}s]")

            # M5: Requisição chega no S02 (Serviço) e processa
            m5_time = m4_time + duration_lb2_service # M5 é quando chega no S2
            current_time_str = datetime.fromtimestamp(m5_time).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
            # Log Processamento no Serviço S2 (usando duração simulada de processamento total)
            logger.info(f"{current_time_str} - domain.source - INFO -      Serviço ({lb2_service}) Processamento [~{duration_service_process:.3f}s]")

            # M6: Serviço (S02) termina processamento e envia resposta de volta
            m6_time = m5_time + duration_service_process # M6 é quando o processamento termina no S2
            current_time_str = datetime.fromtimestamp(m6_time).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
             # Log Serviço S2 -> Source (usando T5 = duração simulada Serviço->Source)
            logger.info(f"{current_time_str} - domain.source - INFO -      Serviço ({lb2_service}) -> Nó 01 (Source) [~{duration_service_return:.3f}s]")


            logger.info("<---")

            # Loga a média dos tempos intermediários para esta requisição
            sum_intermediate_times = duration_source_lb1 + duration_lb1_service + duration_service_lb2 + duration_lb2_service + duration_service_process + duration_service_return
            average_intermediate_times = sum_intermediate_times / 6.0
            logger.info(f"{current_time_str} - domain.source - INFO -      Média dos Tempos Intermediários: {average_intermediate_times:.3f}s")

        # O tempo total (T5 no resumo original) é a soma das durações simuladas dos segmentos principais
        total_time_simulated = duration_source_lb1 + duration_lb1_service + duration_service_lb2 + duration_lb2_service + duration_service_process + duration_service_return

        # Calcula a média dos tempos intermediários para retorno no dicionário (fora do if)
        sum_intermediate_times = duration_source_lb1 + duration_lb1_service + duration_service_lb2 + duration_lb2_service + duration_service_process + duration_service_return
        average_intermediate_times = sum_intermediate_times / 6.0

        return {
            "status": "success",
            "t1_source_lb1": max(0, duration_source_lb1), # Tempo Source -> LB1 (Diagrama T1)
            "t2_lb1_service": max(0, duration_lb1_service), # Tempo LB1 -> Serviço S1 (Diagrama T2)
            "t3_service_lb2": max(0, duration_service_lb2), # Tempo Serviço S1 -> LB2 (Diagrama T3)
            "t4_lb2_service": max(0, duration_lb2_service), # Tempo LB2 -> Serviço S2 (Diagrama T4)
            "t_processamento": max(0, duration_service_process), # Tempo de Processamento Serviço S2
            "t5_service_source": max(0, duration_service_return),  # Tempo Serviço S2 -> Source (Diagrama T5)
            "t5_total": max(0, total_time_simulated), # Tempo Total da Requisição
            "average_intermediate": max(0, average_intermediate_times), # Média dos tempos intermediários
            "lb1_service": lb1_service,
            "lb2_service": lb2_service
        }

    def generate_graphs(self):
        """
        Gera gráficos de desempenho.
        """
        # Prepara os dados
        times = np.array([m["t5_total"] for m in self.metrics_history])
        
        # Calcula o MRT médio geral (em segundos)
        if times.size > 0:
            mrt_medio_geral_seg = np.mean(times)
            mrt_medio_geral_ms = mrt_medio_geral_seg * 1000 # Converte para milissegundos
            logger.info(f"MRT Médio Geral calculado: {mrt_medio_geral_seg:.3f}s ({mrt_medio_geral_ms:.3f}ms)")
            
            # Número de serviços (hardcoded baseado na análise de source.yaml)
            num_services = 4 # Ajuste conforme a sua configuração real, se diferente

            # Cria o gráfico: MRT (ms) vs. Número de Serviços
            plt.figure(figsize=(10, 6))
            plt.plot(num_services, mrt_medio_geral_ms, 'bo', label='Experimento') # Plota um ponto único

            # Adiciona rótulos e título
            plt.xlabel('Número de Serviços')
            plt.ylabel('MRT (ms)')
            plt.title('Tempo Médio de Resposta (MRT) vs. Número de Serviços')
            plt.legend()
            plt.grid(True)
            
            # Define os limites do eixo X para melhor visualização do ponto único
            plt.xlim(0, 5) # Exemplo de limite, ajuste se necessário
            plt.ylim(0, mrt_medio_geral_ms * 1.2) # Ajusta limite Y um pouco acima do ponto

            # Salva o gráfico
            plt.savefig('performance_graph.png')
            plt.close()
            
            logger.info("\n=== Gráfico Gerado ===")
            logger.info("Arquivo: performance_graph.png")
            logger.info("=====================")
        else:
            logger.warning("Não há dados de métricas para gerar o gráfico.") 