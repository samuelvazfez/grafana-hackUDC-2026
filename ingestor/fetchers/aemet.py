"""Fetcher para AEMET OpenData — observaciones convencionales."""
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import AEMET_API_KEY, AEMET_BASE_URL
from cache import cache_key, read_cache, write_cache

log = logging.getLogger(__name__)

_session = requests.Session()
_retry = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
_session.mount("https://", HTTPAdapter(max_retries=_retry))

# Caché de 20 min para AEMET (datos cada ~10-30 min)
AEMET_CACHE_TTL = 20 * 60


def fetch_aemet_observaciones() -> list:
    """
    Llama a /api/observacion/convencional/todas.
    AEMET devuelve un JSON con un campo 'datos' que es una URL temporal
    al JSON real. Hacemos 2 peticiones.
    """
    if not AEMET_API_KEY:
        log.warning("[AEMET] Sin API key, saltando fetch")
        return []

    url = f"{AEMET_BASE_URL}/api/observacion/convencional/todas"
    headers = {"api_key": AEMET_API_KEY}

    key = cache_key(url, {"source": "aemet_obs"})
    cached = read_cache(key, ttl=AEMET_CACHE_TTL)
    if cached is not None:
        log.info("[AEMET] CACHE HIT observaciones")
        return cached

    log.info("[AEMET] FETCH %s", url)
    r = _session.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    meta = r.json()

    datos_url = meta.get("datos")
    if not datos_url:
        log.error("[AEMET] No se recibió URL de datos: %s", meta)
        return []

    log.info("[AEMET] FETCH datos URL")
    r2 = _session.get(datos_url, timeout=30)
    r2.raise_for_status()
    data = r2.json()
    write_cache(key, data)
    return data


def fetch_aemet_avisos(area: str = "61") -> list:
    """
    Llama a /api/avisos_cap/ultimoelaborado/area/{area}.
    area=61 → Galicia (A Coruña). Devuelve lista de avisos CAP.
    """
    if not AEMET_API_KEY:
        log.warning("[AEMET] Sin API key, saltando avisos")
        return []

    url = f"{AEMET_BASE_URL}/api/avisos_cap/ultimoelaborado/area/{area}"
    headers = {"api_key": AEMET_API_KEY}

    key = cache_key(url, {"source": f"aemet_avisos_{area}"})
    cached = read_cache(key, ttl=3600)  # 1h
    if cached is not None:
        log.info("[AEMET] CACHE HIT avisos")
        return cached

    log.info("[AEMET] FETCH avisos %s", url)
    r = _session.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    meta = r.json()

    datos_url = meta.get("datos")
    if not datos_url:
        log.warning("[AEMET] No hay avisos activos o falta URL datos")
        return []

    r2 = _session.get(datos_url, timeout=30)
    r2.raise_for_status()
    try:
        data = r2.json()
    except Exception:
        # avisos CAP a veces viene como XML, manejar gracefully
        log.warning("[AEMET] Avisos no son JSON, raw len=%d", len(r2.text))
        data = []

    write_cache(key, data)
    return data
