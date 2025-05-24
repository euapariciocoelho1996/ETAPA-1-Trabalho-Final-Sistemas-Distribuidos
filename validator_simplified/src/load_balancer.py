from flask import Flask, request, jsonify
import requests
import random
import time
import configparser

app = Flask(__name__)

def now():
    return time.time()

def load_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config['DEFAULT']

config = load_config('configs/loadbalancer1.properties')
services = config['services'].split(',')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    data['timestamps']['T1'] = now()
    print(f"\nRecebida requisição em T1: {data['timestamps']['T1']}")
    
    # Escolher serviço (round-robin, random, etc)
    service_url = random.choice(services)
    print(f"Encaminhando para serviço: {service_url}")
    
    try:
        resp = requests.post(f"{service_url}/process", json=data)
        print(f"Resposta recebida do serviço: {resp.status_code}")
        return jsonify(resp.json())
    except requests.exceptions.ConnectionError:
        print(f"Erro: Não foi possível conectar ao serviço {service_url}")
        print("Verifique se o serviço está rodando.")
        return jsonify({"error": "Service unavailable"}), 503
    except Exception as e:
        print(f"Erro ao processar requisição: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(f"Iniciando LoadBalancer1 na porta {config['port']}...")
    print(f"Serviços disponíveis: {', '.join(services)}")
    app.run(host='0.0.0.0', port=int(config['port'])) 