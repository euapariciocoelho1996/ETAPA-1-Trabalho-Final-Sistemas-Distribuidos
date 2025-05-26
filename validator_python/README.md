# Sistema de Validação e Classificação de Veículos

Este projeto implementa um sistema distribuído para validação e classificação de veículos, utilizando uma arquitetura baseada em serviços e comunicação em tempo real.

## 📁 Estrutura do Projeto

```
.
├── config/                 # Arquivos de configuração
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
├── vehicle_classifier.pkl  # Modelo treinado para classificação
├── requirements.txt        # Dependências do projeto
└── README.md              # Este arquivo
```

## 🚀 Funcionalidades Principais

- Sistema distribuído para validação de veículos
- Classificação automática de veículos
- Balanceamento de carga entre serviços
- Comunicação em tempo real via WebSocket
- Interface REST API para integração

## 🛠️ Tecnologias Utilizadas

- **FastAPI**: Framework web para APIs REST
- **WebSocket**: Comunicação em tempo real
- **OpenCV**: Processamento de imagens
- **Scikit-learn**: Machine Learning para classificação
- **Matplotlib**: Visualização de dados
- **NumPy**: Computação numérica
- **Python-dotenv**: Gerenciamento de variáveis de ambiente
- **PyYAML**: Manipulação de arquivos de configuração

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

## 📊 Componentes do Sistema

### Domain

- **abstract_proxy.py**: Classe base para implementação de proxies
- **load_balancer_proxy.py**: Implementação de balanceamento de carga
- **network_manager.py**: Gerenciamento de comunicação em rede
- **service.py**: Implementação base de serviços
- **service_proxy.py**: Proxy para comunicação entre serviços
- **source.py**: Fonte de dados e processamento

### Arquivos de Configuração

- Arquivos YAML na pasta `config/` para configuração do sistema
- Variáveis de ambiente para configurações sensíveis

### Modelo de Classificação

- `vehicle_classifier.pkl`: Modelo treinado para classificação de veículos

## 📈 Monitoramento e Performance

O sistema inclui gráficos de performance:
- `performance_graph.png`: Métricas gerais de performance
- `mrt_vs_services.png`: Análise de tempo de resposta vs serviços
- `processing_vs_network.png`: Comparação entre processamento e latência de rede

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes. 