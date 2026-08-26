FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y curl zstd && \
    curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=0.32.14 sh && \
    apt-get clean

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x entrypoint.sh

ENV OLLAMA_HOST=0.0.0.0
EXPOSE 8080
CMD ["./entrypoint.sh"]