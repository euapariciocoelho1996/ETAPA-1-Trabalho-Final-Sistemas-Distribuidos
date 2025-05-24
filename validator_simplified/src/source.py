import time
import requests
import configparser
from datetime import datetime
import sys

def now():
    return time.time()

def load_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config['DEFAULT']

def main():
    try:
        config = load_config('configs/source.properties')
        lb1_url = config['lb1_url']
        rate = float(config['generation_rate'])
        results = []

        print(f"Iniciando Source...")
        print(f"Conectando ao LoadBalancer1 em: {lb1_url}")
        print(f"Taxa de geração: {rate} requisições/segundo")
        print(f"Número de requisições: {config['num_requests']}")

        for i in range(int(config['num_requests'])):
            try:
                payload = {
                    "data": f"request_{i}",
                    "timestamps": {"T0": now()}
                }
                print(f"\nEnviando requisição {i+1}...")
                resp = requests.post(f"{lb1_url}/process", json=payload)
                result = resp.json()
                result['timestamps']['T5'] = now()
                results.append(result['timestamps'])
                print(f"Requisição {i+1} completada em {result['timestamps']['T5'] - result['timestamps']['T0']:.2f} segundos")
                time.sleep(1/rate)
            except requests.exceptions.ConnectionError:
                print(f"Erro: Não foi possível conectar ao LoadBalancer1 em {lb1_url}")
                print("Verifique se o LoadBalancer1 está rodando.")
                sys.exit(1)
            except Exception as e:
                print(f"Erro ao processar requisição {i+1}: {str(e)}")
                continue

        # Salvar resultados para análise
        print("\nSalvando resultados em results.csv...")
        with open('results.csv', 'w') as f:
            f.write("T0,T1,T2,T3,T4,T5\n")
            for r in results:
                f.write(','.join(str(r.get(f"T{i}", "")) for i in range(6)) + "\n")
        print("Resultados salvos com sucesso!")

    except FileNotFoundError:
        print("Erro: Arquivo de configuração não encontrado.")
        print("Verifique se o arquivo configs/source.properties existe.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 