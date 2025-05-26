# PASID-VALIDATOR - ETAPA 1 - Sistema de Validação de Desempenho em Sistemas Distribuídos

Este projeto é o trabalho final da disciplina de Sistemas Distribuídos, implementando uma versão em Python do PASID-VALIDATOR, uma ferramenta para validação de desempenho em sistemas distribuídos.

## 📺 Vídeo Explicativo
[Assista ao vídeo explicativo do projeto](https://youtu.be/Fv1OZV-fvcU)

## 📁 Estrutura do Projeto

```
.
├── config/                 # Arquivos de configuração
│   ├── loadbalancer1.properties
│   ├── loadbalancer2.properties
│   └── source.properties
├── data/                   # Dados e recursos
├── src/                    # Código fonte principal
│   ├── domain/            # Componentes principais do sistema
│   │   ├── abstract_proxy.py
│   │   ├── load_balancer_proxy.py
│   │   ├── network_manager.py
│   │   ├── service.py
│   │   ├── service_proxy.py
│   │   └── source.py
│   ├── main.py            # Ponto de entrada da aplicação
│   └── start_services.py  # Script para iniciar os serviços
├── requirements.txt        # Dependências do projeto
└── README.md              # Este arquivo
```

## 📄 Descrição Detalhada dos Arquivos

### Arquivos de Configuração (`config/`)

#### `loadbalancer1.properties`
- Configurações do primeiro balanceador de carga
- Define parâmetros como:
  - Porta de escuta
  - Política de balanceamento
  - Timeout de conexão
  - Endereços dos serviços gerenciados

#### `loadbalancer2.properties`
- Configurações do segundo balanceador de carga
- Similar ao primeiro, mas com parâmetros específicos para o segundo nível
- Inclui configurações de:
  - Distribuição de carga
  - Prioridades de serviços
  - Métricas de monitoramento

#### `source.properties`
- Configurações do gerador de solicitações
- Define:
  - Taxa de geração de requisições
  - Endereços dos balanceadores
  - Parâmetros de simulação
  - Configurações de coleta de métricas

### Código Fonte (`src/`)

#### `main.py`
- Ponto de entrada principal da aplicação
- Inicializa todos os componentes
- Configura o ambiente de execução
- Gerencia o ciclo de vida da aplicação

#### `start_services.py`
- Script para inicialização dos serviços
- Configura a rede entre os serviços
- Define variáveis de ambiente
- Gerencia a ordem de inicialização dos serviços

### Componentes do Domínio (`src/domain/`)

#### `abstract_proxy.py`
- Classe base abstrata para implementação de proxies
- Define a interface comum para todos os proxies
- Implementa métodos base de comunicação
- Gerencia conexões e timeouts

#### `load_balancer_proxy.py`
- Implementação do balanceador de carga
- Algoritmo de distribuição de requisições
- Monitoramento de saúde dos serviços
- Gerenciamento de filas e prioridades

#### `network_manager.py`
- Gerenciamento de comunicação em rede
- Implementa protocolos de comunicação
- Gerencia conexões WebSocket
- Trata reconexões e falhas de rede

#### `service.py`
- Implementação base de serviços
- Define interface comum para todos os serviços
- Gerencia ciclo de vida do serviço
- Implementa métricas de desempenho

#### `service_proxy.py`
- Proxy para comunicação entre serviços
- Gerencia conexões entre serviços
- Implementa retry e circuit breaker
- Coleta métricas de comunicação

#### `source.py`
- Implementação do gerador de solicitações
- Gera carga de trabalho controlada
- Coleta métricas de desempenho
- Gera relatórios e gráficos

### Outros Arquivos

#### `requirements.txt`
- Lista de dependências do projeto
- Versões específicas de cada pacote
- Inclui:
  - FastAPI para APIs REST
  - WebSocket para comunicação em tempo real
  - Matplotlib para gráficos
  - Outras bibliotecas de suporte

#### `README.md`
- Documentação principal do projeto
- Instruções de instalação e uso
- Descrição da arquitetura
- Guia de contribuição

## 🎯 Objetivo

O PASID-VALIDATOR é uma ferramenta desenvolvida para validar modelos de Stochastic Petri Net (SPN) através de experimentos práticos. O objetivo é verificar se o modelo teórico representa adequadamente o sistema real, comparando comportamentos previstos com dados observados.

## 🔄 Fluxo do Sistema

O sistema é composto por três nós principais:

1. **Nó 01 - Source**
   - Responsável por gerar solicitações
   - Coleta e compila resultados
   - Calcula métricas de validação

2. **Nó 02 - LoadBalancer1 e Serviços**
   - Balanceador de carga primário
   - Distribui solicitações entre Service1.1 e Service1.2
   - Gerencia processamento inicial

3. **Nó 03 - LoadBalancer2 e Serviços**
   - Balanceador de carga secundário
   - Distribui solicitações entre Service2.1 e Service2.2
   - Realiza processamento adicional

## ⏱️ Métricas de Tempo

O sistema coleta diversos timestamps para análise de desempenho:

- **MRT (Mean Response Time)**: Tempo médio de resposta
- **T1**: Tempo de chegada da solicitação no servidor
- **T2**: Tempo de processamento e envio da resposta
- **T3, T4, T5**: Tempos intermediários de processamento

## 🛠️ Tecnologias Utilizadas

- **FastAPI**: Framework web para APIs REST
- **WebSocket**: Comunicação em tempo real
- **Python-dotenv**: Gerenciamento de variáveis de ambiente
- **PyYAML**: Manipulação de arquivos de configuração
- **Matplotlib**: Geração de gráficos de desempenho

## 📋 Pré-requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

## 🔧 Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🚀 Executando o Projeto

1. Inicie os serviços:
```bash
python src/start_services.py
```

2. Execute a aplicação principal:
```bash
python src/main.py
```

