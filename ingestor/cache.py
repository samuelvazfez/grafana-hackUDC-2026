"""Cache local basada en ficheros JSON con TTL."""
import os
import json
import time
import hashlib
from config import CACHE_DIR, CACHE_TTL_SECONDS

def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

def cache_key(url: str, params: dict) -> str:
    """SHA-256 de url+params excluyendo claves secretas (API_KEY, api_key)."""
    safe = {k: v for k, v in params.items() if k.lower() not in ("api_key",)}
    raw = url + "?" + "&".join(f"{k}={safe[k]}" for k in sorted(safe))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def cache_path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{key}.json")

def read_cache(key: str, ttl: int = None):
    """Lee caché si existe y no ha expirado. ttl en segundos (por defecto usa CACHE_TTL_SECONDS)."""
    ttl = ttl or CACHE_TTL_SECONDS
    path = cache_path(key)
    if not os.path.exists(path):
        return None
    age = time.time() - os.stat(path).st_mtime
    if age > ttl:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_cache(key: str, data):
    """Escritura atómica: escribe a .tmp y luego os.replace."""
    path = cache_path(key)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, path)
