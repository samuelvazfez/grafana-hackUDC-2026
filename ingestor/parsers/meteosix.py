"""Parser para MeteoSIX v5 → filas tidy (weather_hourly)."""
import re
import logging
from datetime import datetime

log = logging.getLogger(__name__)

# Regex para normalizar tz "+01" → "+01:00"
_TZ_RE = re.compile(r'([+-]\d{2})$')

# Variables escalares MeteoSIX → columna weather_hourly
_SCALAR_MAP = {
    "temperature":          "temperature",
    "precipitation_amount": "precipitation",
    "sky_state":            "sky_state",
}
# Variable compuesta "wind" → moduleValue / directionValue
_WIND_VAR = "wind"


def _normalize_tz(ts: str) -> str:
    """'2026-02-28T13:00:00+01' → '2026-02-28T13:00:00+01:00'"""
    return _TZ_RE.sub(r'\1:00', ts)


def _safe_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _get_dt(raw_ts: str):
    """Parse timeInstant con tz normalization."""
    if not raw_ts:
        return None
    try:
        return datetime.fromisoformat(_normalize_tz(raw_ts))
    except ValueError:
        log.warning("timeInstant malformado: %s", raw_ts)
        return None


def _ensure_row(by_time, ts_key, dt, coord_idx, lon, lat):
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
    return by_time[ts_key]


def parse_meteosix(payload: dict) -> list[dict]:
    """
    Convierte payload GeoJSON de MeteoSIX a filas tidy.
    Una fila por (coord_index, timeInstant).
    Maneja variables escalares (temperature, precipitation, sky_state)
    y la variable compuesta 'wind' (moduleValue + directionValue).
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

                # ── Variable compuesta "wind" ─────────────────────────
                if var_name == _WIND_VAR:
                    for val_obj in var.get("values", []):
                        dt = _get_dt(val_obj.get("timeInstant", ""))
                        if dt is None:
                            continue
                        ts_key = dt.isoformat()
                        row = _ensure_row(by_time, ts_key, dt, coord_idx, lon, lat)
                        row["wind_speed"] = _safe_float(val_obj.get("moduleValue"))
                        row["wind_direction"] = _safe_float(val_obj.get("directionValue"))
                        row["raw"]["wind_module"] = val_obj.get("moduleValue")
                        row["raw"]["wind_direction"] = val_obj.get("directionValue")
                    continue

                # ── Variables escalares ────────────────────────────────
                col_name = _SCALAR_MAP.get(var_name)
                if col_name is None:
                    continue

                for val_obj in var.get("values", []):
                    dt = _get_dt(val_obj.get("timeInstant", ""))
                    if dt is None:
                        continue
                    ts_key = dt.isoformat()
                    row = _ensure_row(by_time, ts_key, dt, coord_idx, lon, lat)

                    raw_val = val_obj.get("value")
                    if col_name == "sky_state":
                        row[col_name] = str(raw_val) if raw_val is not None else None
                    else:
                        row[col_name] = _safe_float(raw_val)
                    row["raw"][var_name] = raw_val

            rows.extend(by_time.values())

    log.info("[parser] MeteoSIX → %d filas tidy", len(rows))
    return rows
