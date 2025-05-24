from flask import Flask, request, jsonify
import time
import configparser

app = Flask(__name__)

def now():
    return time.time()

def load_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config['DEFAULT']

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    data['timestamps']['T2'] = now()
    print(f"\nRecebida requisição em T2: {data['timestamps']['T2']}")
    
    # Simular processamento pesado
    print("Iniciando processamento...")
    time.sleep(2)  # ou chame um modelo de IA real aqui
    print("Processamento concluído")
    
    data['timestamps']['T3'] = now()
    print(f"Enviando resposta em T3: {data['timestamps']['T3']}")
    return jsonify(data)

if __name__ == "__main__":
    try:
        config = load_config('configs/service.properties')
        port = int(config['port'])
        print(f"Iniciando Service na porta {port}...")
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Erro ao iniciar o Service: {str(e)}") 