"""Motor de cálculo del IAD (Índice de Aptitud Deportiva) para running."""
import logging

log = logging.getLogger(__name__)

# ── Sub-scores normalizados 0-10 ─────────────────────────────────────────────

def _temp_score(t) -> float:
    """Ideal: 10-20°C → 10. Fuera de rango cae linealmente."""
    if t is None:
        return 5.0  # sin dato → neutro
    if 10 <= t <= 20:
        return 10.0
    elif t < 0 or t > 40:
        return 0.0
    elif t < 10:
        return max(0, 10 - (10 - t) * 1.0)   # 0°C→0, 10°C→10
    else:  # t > 20
        return max(0, 10 - (t - 20) * 0.5)    # 20°C→10, 40°C→0


def _wind_score(w) -> float:
    """Ideal: <15 km/h → 10. >40 → 0."""
    if w is None:
        return 5.0
    if w <= 15:
        return 10.0
    elif w >= 40:
        return 0.0
    else:
        return max(0, 10 - (w - 15) * 0.4)


def _precip_score(p) -> float:
    """Ideal: 0mm → 10. >10mm → 0."""
    if p is None:
        return 5.0
    if p <= 0.5:
        return 10.0
    elif p >= 10:
        return 0.0
    else:
        return max(0, 10 - p * 1.05)


def _sky_score(sky) -> float:
    """CLEAR/PARTLY_CLOUDY → 10. Otros → baja."""
    if sky is None:
        return 5.0
    sky = sky.upper()
    scores = {
        "CLEAR": 10.0,
        "SUNNY": 10.0,
        "HIGH_CLOUDS": 9.0,
        "PARTLY_CLOUDY": 8.0,
        "CLOUDY": 5.0,
        "OVERCAST": 4.0,
        "FOG": 2.0,
        "DRIZZLE": 2.0,
        "RAIN": 1.0,
        "SHOWER": 1.0,
        "STORM": 0.0,
        "SNOW": 0.0,
    }
    # Buscar coincidencia parcial
    for key, val in scores.items():
        if key in sky:
            return val
    return 5.0


# ── Cálculo IAD ──────────────────────────────────────────────────────────────

# Pesos para running
WEIGHTS = {
    "temperature": 0.30,
    "wind": 0.25,
    "precipitation": 0.30,
    "sky": 0.15,
}

LABELS = [
    (8.0, "Perfecto"),
    (6.0, "Bueno"),
    (4.0, "Aceptable"),
    (2.0, "Malo"),
    (0.0, "No recomendado"),
]


def compute_iad_running(weather_rows: list[dict]) -> list[dict]:
    """
    Calcula IAD running para cada fila de weather_hourly.
    Devuelve lista de dicts con: time, coord_index, lon, lat, score, label, details.
    """
    iad_rows = []
    for r in weather_rows:
        ts = _temp_score(r.get("temperature"))
        ws = _wind_score(r.get("wind_speed"))
        ps = _precip_score(r.get("precipitation"))
        ss = _sky_score(r.get("sky_state"))

        score = round(
            ts * WEIGHTS["temperature"]
            + ws * WEIGHTS["wind"]
            + ps * WEIGHTS["precipitation"]
            + ss * WEIGHTS["sky"],
            2,
        )
        score = max(0.0, min(10.0, score))

        label = "No recomendado"
        for threshold, lbl in LABELS:
            if score >= threshold:
                label = lbl
                break

        iad_rows.append({
            "time": r["time"],
            "coord_index": r["coord_index"],
            "lon": r.get("lon"),
            "lat": r.get("lat"),
            "score": score,
            "label": label,
            "details": {
                "temp_score": ts,
                "wind_score": ws,
                "precip_score": ps,
                "sky_score": ss,
                "temp": r.get("temperature"),
                "wind": r.get("wind_speed"),
                "precip": r.get("precipitation"),
                "sky": r.get("sky_state"),
            },
        })

    log.info("[IAD] Calculados %d scores running", len(iad_rows))
    return iad_rows
