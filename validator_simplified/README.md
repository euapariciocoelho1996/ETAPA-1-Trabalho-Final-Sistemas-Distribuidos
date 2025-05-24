# PASID-VALIDATOR (Python Version)

Este projeto é uma versão em Python do PASID-VALIDATOR, um sistema distribuído cliente-servidor para validação de modelos SPN através de experimentos de coleta de tempos.

## Estrutura do Projeto

```
pasid_validator/
│
├── src/
│   ├── source.py
│   ├── load_balancer.py
│   ├── service.py
│   └── utils.py
│
├── configs/
│   ├── source.properties
│   ├── loadbalancer1.properties
│   └── loadbalancer2.properties
│
├── tests/
│   └── ...
│
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- Flask
- requests
- configparser

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Executando o Source

O Source gera requisições periodicamente e envia para o LoadBalancer1. Ele coleta os tempos de ida e volta e salva os resultados em `results.csv`.

```bash
python src/source.py
```

### Executando o LoadBalancer1

O LoadBalancer1 recebe requisições do Source, marca timestamp, repassa para um dos serviços e retorna a resposta.

```bash
python src/load_balancer.py
```

### Executando o Service

O Service recebe requisições, marca timestamp de chegada, simula um processamento pesado e marca timestamp de saída.

```bash
python src/service.py
```

## Próximos Passos

- **Entrega 02**: Coloque cada componente em um container Docker, use um serviço real pesado (ex: um modelo de IA em Python).
- **Entrega 03**: Use os dados coletados para gerar gráficos e escrever o artigo. 