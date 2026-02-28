import os
import json
import time
import hashlib
from datetime import datetime, timezone
import requests
import psycopg2
from psycopg2.extras import Json

# MeteoSIX v5
METEOSIX_BASE_URL = os.getenv("METEOSIX_BASE_URL", "https://servizos.meteogalicia.gal/apiv5").rstrip("/")
METEOSIX_API_KEY = os.getenv("METEOSIX_API_KEY", "")

# Operación principal para el MVP
OPERATION = os.getenv("METEOSIX_OPERATION", "getNumericForecastInfo")

# Recomendado: pedir JSON explícitamente
METEOSIX_FORMAT = os.getenv("METEOSIX_FORMAT", "application/json")

# coords en formato "lon,lat;lon,lat;..."
# (máximo 20 puntos por petición)
COORDS_BATCH = os.getenv(
    "METEOSIX_COORDS",
    "-8.409,43.362;-8.546,42.880;-8.720,42.240;-7.556,43.012;-7.864,42.336;-8.644,42.431"
).strip()

# Cache local simple (archivo) para evitar muchas peticiones
CACHE_DIR = os.getenv("CACHE_DIR", "/app/cache")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", str(26 * 3600)))  # 26h
POLL_SECONDS = int(os.getenv("POLL_SECONDS", str(6 * 3600)))  # si actualiza 1/día, sobra

def db_conn():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "postgres"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
    )

def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

def cache_key(url: str, params: dict) -> str:
    # OJO: no metas espacios en params (el manual avisa que no están permitidos).
    key_raw = url + "?" + "&".join(f"{k}={params[k]}" for k in sorted(params.keys()))
    return hashlib.sha256(key_raw.encode("utf-8")).hexdigest()

def cache_path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{key}.json")

def read_cache(key: str):
    path = cache_path(key)
    if not os.path.exists(path):
        return None
    age = time.time() - os.stat(path).st_mtime
    if age > CACHE_TTL_SECONDS:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_cache(key: str, data: dict):
    path = cache_path(key)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def fetch_meteosix_forecast(coords_batch: str) -> dict:
    coords_batch = coords_batch.replace(" ", "")
    if not METEOSIX_API_KEY:
        raise RuntimeError("Falta METEOSIX_API_KEY en el entorno")

    url = f"{METEOSIX_BASE_URL}/{OPERATION}"

    # Params alineados con el manual:
    # - API_KEY obligatorio
    # - coords o locationIds (NO ambos)
    # - format opcional (aquí pedimos JSON)
    params = {
        "coords": coords_batch,            # "lon,lat;lon,lat;..."
        "format": METEOSIX_FORMAT,         # "application/json"
        "API_KEY": METEOSIX_API_KEY,
        "lang": os.getenv("METEOSIX_LANG", "gl"),
        # Si queréis limitar rango temporal, añadid startTime/endTime aquí
    }

    key = cache_key(url, params)
    cached = read_cache(key)
    if cached is not None:
        print("[CACHE HIT] MeteoSIX forecast batch")
        return cached

    print(f"[FETCH] {url}")
    r = requests.get(url, params=params, timeout=45)
    r.raise_for_status()
    data = r.json()
    write_cache(key, data)
    return data

def insert_raw_weather(conn, endpoint: str, coords_batch: str, payload: dict):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw_weather (ts_ingested, endpoint, coords_batch, payload)
            VALUES (NOW(), %s, %s, %s)
            """,
            (endpoint, coords_batch, Json(payload)),
        )
    conn.commit()

def main():
    ensure_cache_dir()

    # Nota manual: máximo 20 puntos por petición (si os pasáis, os dará error).
    coords_count = len([c for c in COORDS_BATCH.split(";") if c.strip()])
    if coords_count == 0:
        raise RuntimeError("METEOSIX_COORDS está vacío")
    if coords_count > 20:
        raise RuntimeError(f"Demasiados puntos en METEOSIX_COORDS ({coords_count}). Máximo 20.")

    print(f"[INGESTOR] starting... coords={coords_count}, poll={POLL_SECONDS}s")

    while True:
        try:
            payload = fetch_meteosix_forecast(COORDS_BATCH)
            conn = db_conn()
            insert_raw_weather(conn, OPERATION, COORDS_BATCH, payload)
            conn.close()
            print("[OK] inserted raw_weather batch")
        except Exception as e:
            print("[ERROR]", repr(e))

        print(f"[SLEEP] {POLL_SECONDS}s")
        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()