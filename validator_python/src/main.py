import os
from domain.source import Source
import logging
from datetime import datetime

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S,%f'[:-3]
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Obtém o caminho do diretório atual
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, '..', 'config', 'source.yaml')
        
        # Inicializa o Source
        logger.info("Inicializando o Source...")
        source = Source(config_path)
        
        # Executa o experimento por 30 segundos
        logger.info("Iniciando experimento...")
        source.run_experiment(duration=30)
        
        # Gera os gráficos
        logger.info("Gerando gráficos de desempenho...")
        source.generate_graphs()
        
        logger.info("Experimento concluído! Verifique o arquivo performance_graph.png")
        
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        raise

if __name__ == "__main__":
    main() 