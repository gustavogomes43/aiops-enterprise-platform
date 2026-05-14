# Use uma imagem leve do Python
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema para o Prophet e compilação
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos
COPY requirements.txt .
COPY requirements-test.txt .

# Instala todas as libs de IA e Observabilidade
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação e dos motores de IA
COPY src/ ./src/
COPY aiops/ ./aiops/

# Expõe a porta do FastAPI e do Prometheus
EXPOSE 8000
EXPOSE 9091

# Comando para rodar a API
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]