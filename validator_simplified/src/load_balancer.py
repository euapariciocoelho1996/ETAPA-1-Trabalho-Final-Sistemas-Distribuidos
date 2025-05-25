from flask import Flask, request, jsonify
import asyncio
import aiohttp
import random
import time
import configparser
import aioredis
import json
from threading import Thread

app = Flask(__name__)

def now():
    return time.time()

def load_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config['DEFAULT']

config = load_config('configs/loadbalancer1.properties')
services = [config['service1_url'], config['service2_url']]
redis_url = config.get('redis_url', 'redis://localhost:6379')

# Fila de requisições
request_queue = asyncio.Queue()
# Fila de respostas
response_queue = asyncio.Queue()

async def process_request(request_data):
    data = request_data
    data['timestamps']['T1'] = now()
    print(f"\nRecebida requisição em T1: {data['timestamps']['T1']}")
    
    # Escolher serviço (round-robin, random, etc)
    service_url = random.choice(services)
    print(f"Encaminhando para serviço: {service_url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{service_url}/process", json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    result['timestamps']['T4'] = now()
                    print(f"Resposta recebida do serviço: {response.status}")
                    return result
                else:
                    print(f"Erro do serviço: {response.status}")
                    return {"error": "Service error", "status": response.status}
    except Exception as e:
        print(f"Erro ao processar requisição: {str(e)}")
        return {"error": str(e)}

async def worker():
    while True:
        try:
            # Pega uma requisição da fila
            request_data = await request_queue.get()
            result = await process_request(request_data)
            # Coloca o resultado na fila de respostas
            await response_queue.put(result)
            request_queue.task_done()
        except Exception as e:
            print(f"Erro no worker: {str(e)}")

@app.route('/process', methods=['POST'])
async def process():
    data = request.json
    # Adiciona a requisição à fila
    await request_queue.put(data)
    return jsonify({"status": "accepted"})

async def start_workers(num_workers=3):
    workers = []
    for _ in range(num_workers):
        worker_task = asyncio.create_task(worker())
        workers.append(worker_task)
    return workers

def run_flask():
    app.run(host='0.0.0.0', port=int(config['port']))

if __name__ == "__main__":
    print(f"Iniciando LoadBalancer1 na porta {config['port']}...")
    print(f"Serviços disponíveis: {', '.join(services)}")
    
    # Inicia os workers em uma thread separada
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    workers = loop.run_until_complete(start_workers())
    
    # Inicia o Flask em uma thread separada
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Encerrando LoadBalancer...")
        for worker in workers:
            worker.cancel()
        loop.close() 