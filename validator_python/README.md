# Validator Python

Este é um projeto Python que implementa um sistema de proxy com balanceamento de carga.

## Estrutura do Projeto

```
validator_python/
├── src/
│   ├── domain/
│   │   ├── abstract_proxy.py
│   │   ├── load_balancer_proxy.py
│   │   └── service_proxy.py
│   └── main.py
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

## Instalação

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

## Uso

Para executar o exemplo principal:

```bash
python src/main.py
```

## Funcionalidades

- `AbstractProxy`: Classe base abstrata para implementação de proxies
- `LoadBalancerProxy`: Implementa balanceamento de carga usando algoritmo round-robin
- `ServiceProxy`: Implementa proxy para serviços individuais

## Testes

Para executar os testes:

```bash
pytest
``` 