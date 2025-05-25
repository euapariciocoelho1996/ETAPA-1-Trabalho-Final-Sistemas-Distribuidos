from flask import Flask, request, jsonify
import asyncio
import time
import configparser
from threading import Thread

app = Flask(__name__)

def now():
    return time.time()

def load_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config['DEFAULT']

# Fila de processamento
processing_queue = asyncio.Queue()

async def process_request(request_data):
    data = request_data
    data['timestamps']['T2'] = now()
    print(f"\nRecebida requisição em T2: {data['timestamps']['T2']}")
    
    # Simular processamento pesado
    print("Iniciando processamento...")
    await asyncio.sleep(2)  # Simula processamento assíncrono
    print("Processamento concluído")
    
    data['timestamps']['T3'] = now()
    print(f"Enviando resposta em T3: {data['timestamps']['T3']}")
    return data

async def worker():
    while True:
        try:
            # Pega uma requisição da fila
            request_data = await processing_queue.get()
            result = await process_request(request_data)
            # Coloca o resultado na fila de respostas
            await response_queue.put(result)
            processing_queue.task_done()
        except Exception as e:
            print(f"Erro no worker: {str(e)}")

@app.route('/process', methods=['POST'])
async def process():
    data = request.json
    # Adiciona a requisição à fila
    await processing_queue.put(data)
    return jsonify({"status": "accepted"})

async def start_workers(num_workers=2):
    workers = []
    for _ in range(num_workers):
        worker_task = asyncio.create_task(worker())
        workers.append(worker_task)
    return workers

def run_flask():
    app.run(host='0.0.0.0', port=int(config['port']))

if __name__ == "__main__":
    try:
        config = load_config('configs/service.properties')
        port = int(config['port'])
        print(f"Iniciando Service na porta {port}...")
        
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
            print("Encerrando Service...")
            for worker in workers:
                worker.cancel()
            loop.close()
            
    except Exception as e:
        print(f"Erro ao iniciar o Service: {str(e)}") 