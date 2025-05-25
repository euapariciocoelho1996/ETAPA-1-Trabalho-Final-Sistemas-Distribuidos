import asyncio
import aiohttp
import time
import configparser
from datetime import datetime
import sys
import aioredis
import json

def now():
    return time.time()

def load_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config['DEFAULT']

async def send_request(session, lb1_url, request_id, rate):
    try:
        payload = {
            "data": f"request_{request_id}",
            "timestamps": {"T0": now()}
        }
        print(f"\nEnviando requisição {request_id+1}...")
        
        async with session.post(f"{lb1_url}/process", json=payload) as response:
            if response.status == 200:
                result = await response.json()
                result['timestamps']['T5'] = now()
                results.append(result['timestamps'])
                
                # Calcular e mostrar tempos intermediários
                ts = result['timestamps']
                t0 = float(ts.get('T0', 0))
                t1 = float(ts.get('T1', 0))
                t2 = float(ts.get('T2', 0))
                t3 = float(ts.get('T3', 0))
                t4 = float(ts.get('T4', 0))
                t5 = float(ts.get('T5', 0))
                
                # Calcular tempos de cada etapa
                delta_t1 = (t1-t0)*1000
                delta_t2 = (t2-t1)*1000
                delta_t3 = (t3-t2)*1000
                delta_t4 = (t4-t3)*1000
                delta_t5 = (t5-t4)*1000
                
                # Calcular média dos tempos
                media_tempos = (delta_t1 + delta_t2 + delta_t3 + delta_t4 + delta_t5) / 5
                
                print(f"T0 (Início no Source): {t0:.3f} | T1 (Chegada no LB01): {t1:.3f} | ΔT1 (Source -> LB01): {delta_t1:.2f} ms")
                print(f"T1 (Chegada no LB01): {t1:.3f} | T2 (Chegada no LB02): {t2:.3f} | ΔT2 (LB01 -> LB02): {delta_t2:.2f} ms")
                print(f"T2 (Chegada no LB02): {t2:.3f} | T3 (Chegada no Validator): {t3:.3f} | ΔT3 (LB02 -> Validator): {delta_t3:.2f} ms")
                print(f"T3 (Chegada no Validator): {t3:.3f} | T4 (Saída do Validator): {t4:.3f} | ΔT4 (Processamento): {delta_t4:.2f} ms")
                print(f"T4 (Saída do Validator): {t4:.3f} | T5 (Chegada no Source): {t5:.3f} | ΔT5 (Validator -> Source): {delta_t5:.2f} ms")
                print(f"Média dos tempos: {media_tempos:.2f} ms")
                return result['timestamps']
            else:
                print(f"Erro na requisição {request_id+1}: {response.status}")
                return None
    except Exception as e:
        print(f"Erro ao processar requisição {request_id+1}: {str(e)}")
        return None

async def main():
    try:
        config = load_config('configs/source.properties')
        lb1_url = config['lb1_url']
        rate = float(config['generation_rate'])
        num_requests = int(config['num_requests'])
        global results
        results = []

        print(f"Iniciando Source...")
        print(f"Conectando ao LoadBalancer1 em: {lb1_url}")
        print(f"Taxa de geração: {rate} requisições/segundo")
        print(f"Número de requisições: {num_requests}")

        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(num_requests):
                task = asyncio.create_task(send_request(session, lb1_url, i, rate))
                tasks.append(task)
                await asyncio.sleep(1/rate)  # Controla a taxa de envio

            # Aguarda todas as requisições serem enviadas
            await asyncio.gather(*tasks)

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
    asyncio.run(main()) 