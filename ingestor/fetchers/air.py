"""Fetchers para Open-Meteo: Air Quality, Forecast horario y Polen."""
import requests
import logging
from config import METEOSIX_COORDS

log = logging.getLogger(__name__)

_GALICIA_COORDS = None

def _get_coords():
    global _GALICIA_COORDS
    if _GALICIA_COORDS is None:
        _GALICIA_COORDS = []
        for c in METEOSIX_COORDS.split(";"):
            c = c.strip()
            if not c:
                continue
            parts = c.split(",")
            if len(parts) == 2:
                _GALICIA_COORDS.append((parts[0].strip(), parts[1].strip()))  # lon, lat
    return _GALICIA_COORDS


def fetch_air_quality():
    """AQI actual + UV por coordenada."""
    results = []
    for idx, (lon, lat) in enumerate(_get_coords()):
        try:
            resp = requests.get(
                "https://air-quality-api.open-meteo.com/v1/air-quality",
                params={
                    "latitude": lat, "longitude": lon,
                    "current": "european_aqi,pm10,pm2_5,uv_index",
                    "timezone": "auto"
                }, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            data["_lat"], data["_lon"], data["_idx"] = lat, lon, idx
            results.append(data)
        except Exception as e:
            log.error("AQI error lat=%s lon=%s: %s", lat, lon, e)
    return results


def fetch_forecast():
    """Previsión horaria Open-Meteo (próximas 48h) por coordenada."""
    results = []
    for idx, (lon, lat) in enumerate(_get_coords()):
        try:
            resp = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat, "longitude": lon,
                    "hourly": "temperature_2m,apparent_temperature,precipitation_probability,precipitation,wind_speed_10m,wind_gusts_10m,visibility,cloud_cover,is_day",
                    "forecast_days": 2,
                    "timezone": "auto"
                }, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            data["_lat"], data["_lon"], data["_idx"] = lat, lon, idx
            results.append(data)
        except Exception as e:
            log.error("Forecast error lat=%s lon=%s: %s", lat, lon, e)
    return results


def fetch_pollen():
    """Polen horario Open-Meteo por coordenada."""
    results = []
    for idx, (lon, lat) in enumerate(_get_coords()):
        try:
            resp = requests.get(
                "https://air-quality-api.open-meteo.com/v1/air-quality",
                params={
                    "latitude": lat, "longitude": lon,
                    "hourly": "grass_pollen,birch_pollen,olive_pollen,alder_pollen,ragweed_pollen",
                    "forecast_days": 2,
                    "timezone": "auto"
                }, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            data["_lat"], data["_lon"], data["_idx"] = lat, lon, idx
            results.append(data)
        except Exception as e:
            log.error("Pollen error lat=%s lon=%s: %s", lat, lon, e)
    return results
