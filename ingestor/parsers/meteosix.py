"""Parser para MeteoSIX v5 → filas tidy (weather_hourly)."""
import re
import logging
from datetime import datetime

log = logging.getLogger(__name__)

# Regex para normalizar tz "+01" → "+01:00"
_TZ_RE = re.compile(r'([+-]\d{2})$')

# Variables MeteoSIX → columnas weather_hourly
_VAR_MAP = {
    "temperature":          "temperature",
    "wind_speed":           "wind_speed",
    "wind_direction":       "wind_direction",
    "precipitation_amount": "precipitation",
    "sky_state":            "sky_state",
}


def _normalize_tz(ts: str) -> str:
    """'2026-02-28T13:00:00+01' → '2026-02-28T13:00:00+01:00'"""
    return _TZ_RE.sub(r'\1:00', ts)


def _safe_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_meteosix(payload: dict) -> list[dict]:
    """
    Convierte payload GeoJSON de MeteoSIX a filas tidy.
    Una fila por (coord_index, timeInstant).
    Variables ausentes → None (no rompen el insert).
    """
    rows = []
    features = payload.get("features", [])

    for coord_idx, feature in enumerate(features):
        coords = feature.get("geometry", {}).get("coordinates", [None, None])
        lon, lat = coords[0], coords[1]

        for day in feature.get("properties", {}).get("days", []):
            by_time: dict[str, dict] = {}

            for var in day.get("variables", []):
                var_name = var.get("name", "")
                col_name = _VAR_MAP.get(var_name)
                if col_name is None:
                    continue

                for val_obj in var.get("values", []):
                    raw_ts = val_obj.get("timeInstant", "")
                    if not raw_ts:
                        continue
                    try:
                        dt = datetime.fromisoformat(_normalize_tz(raw_ts))
                    except ValueError:
                        log.warning("timeInstant malformado: %s", raw_ts)
                        continue

                    ts_key = dt.isoformat()
                    if ts_key not in by_time:
                        by_time[ts_key] = {
                            "time": dt,
                            "coord_index": coord_idx,
                            "lon": lon,
                            "lat": lat,
                            "temperature": None,
                            "wind_speed": None,
                            "wind_direction": None,
                            "precipitation": None,
                            "sky_state": None,
                            "raw": {},
                        }

                    raw_val = val_obj.get("value")
                    if col_name == "sky_state":
                        by_time[ts_key][col_name] = str(raw_val) if raw_val is not None else None
                    else:
                        by_time[ts_key][col_name] = _safe_float(raw_val)

                    by_time[ts_key]["raw"][var_name] = raw_val

            rows.extend(by_time.values())

    log.info("[parser] MeteoSIX → %d filas tidy", len(rows))
    return rows
