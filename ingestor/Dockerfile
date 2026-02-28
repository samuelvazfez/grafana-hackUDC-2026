FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código (modular)
COPY config.py cache.py db.py iad.py alerter.py app.py ./
COPY fetchers/ ./fetchers/
COPY parsers/ ./parsers/

RUN mkdir -p /app/cache

# Usuario no-root
RUN useradd -r appuser && chown -R appuser /app
USER appuser

CMD ["python", "/app/app.py"]