"""Fetcher para MeteoSIX v5 — getNumericForecastInfo."""
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    METEOSIX_BASE_URL, METEOSIX_API_KEY,
    METEOSIX_OPERATION, METEOSIX_FORMAT, METEOSIX_LANG,
)
from cache import cache_key, read_cache, write_cache

log = logging.getLogger(__name__)

# Sesión HTTP con reintentos automáticos
_session = requests.Session()
_retry = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
_session.mount("https://", HTTPAdapter(max_retries=_retry))


def fetch_meteosix(coords_batch: str) -> dict:
    """
    Llama a MeteoSIX getNumericForecastInfo con coords batch.
    Devuelve JSON completo. Usa caché local.
    """
    coords_batch = coords_batch.replace(" ", "")
    if not METEOSIX_API_KEY:
        raise RuntimeError("Falta METEOSIX_API_KEY en el entorno")

    url = f"{METEOSIX_BASE_URL}/{METEOSIX_OPERATION}"
    params = {
        "coords": coords_batch,
        "format": METEOSIX_FORMAT,
        "API_KEY": METEOSIX_API_KEY,
        "lang": METEOSIX_LANG,
    }

    key = cache_key(url, params)
    cached = read_cache(key)
    if cached is not None:
        log.info("[MeteoSIX] CACHE HIT")
        return cached

    log.info("[MeteoSIX] FETCH %s", url)
    r = _session.get(url, params=params, timeout=45)
    r.raise_for_status()
    data = r.json()
    write_cache(key, data)
    return data
