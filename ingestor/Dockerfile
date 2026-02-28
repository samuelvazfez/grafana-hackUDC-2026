FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias (una vez, en build)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar el código
COPY app.py /app/app.py

# Cache dir
RUN mkdir -p /app/cache

CMD ["python", "/app/app.py"]