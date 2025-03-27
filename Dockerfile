FROM python:3.10-slim

WORKDIR /code

# Instalar dependências do sistema necessárias para PyAudio
RUN apt-get update && apt-get install -y \
    gcc \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY app.py .

# Comando para rodar o app
CMD ["python", "app.py"]