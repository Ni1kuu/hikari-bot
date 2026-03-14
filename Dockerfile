# Base Python 3.13 slim
FROM python:3.13-slim

# Atualiza e instala ffmpeg e dependências básicas
RUN apt-get update && apt-get install -y ffmpeg curl git && apt-get clean

# Cria diretório do bot
WORKDIR /app

# Copia todos os arquivos do projeto para dentro do container
COPY . /app

# Atualiza pip e instala dependências do requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Comando para iniciar o bot
CMD ["python", "kaoribot.py"]
