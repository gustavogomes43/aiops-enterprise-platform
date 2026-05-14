import time
import random
from datetime import datetime
import redis
import json

# Conecta ao Redis que você vai subir
r = redis.Redis(host='localhost', port=6379, db=0)

def generate_fake_metrics():
    print("🚀 Iniciando geração de métricas com anomalias...")
    while True:
        # Métrica normal (CPU entre 20-40%)
        val = random.uniform(20, 40)
        
        # Injetar anomalia aleatória (Pico de 90%+)
        if random.random() > 0.9:
            val = random.uniform(90, 100)
            print(f"⚠️  Injetando ANOMALIA: {val:.2f}%")
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "value": val,
            "metric": "cpu_usage_percent"
        }
        
        # Envia para o Redis para sua IA ler
        r.lpush('metrics:queue', json.dumps(data))
        r.ltrim('metrics:queue', 0, 99) # Mantém apenas as últimas 100
        
        time.sleep(1)

if __name__ == "__main__":
    generate_fake_metrics()