"""Motor de cálculo del IAD (Índice de Aptitud Deportiva) multi-deporte."""
import logging

log = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# Sub-scores parametrizables (0-10)
# ══════════════════════════════════════════════════════════════════════════════

def _score_range(val, ideal_min, ideal_max, abs_min, abs_max, default=5.0):
    """Score genérico: 10 si val está en [ideal_min, ideal_max], 0 en abs_min/abs_max."""
    if val is None:
        return default
    if ideal_min <= val <= ideal_max:
        return 10.0
    if val < abs_min or val > abs_max:
        return 0.0
    if val < ideal_min:
        span = ideal_min - abs_min
        return max(0, 10.0 * (val - abs_min) / span) if span > 0 else 0.0
    else:  # val > ideal_max
        span = abs_max - ideal_max
        return max(0, 10.0 * (abs_max - val) / span) if span > 0 else 0.0


def _precip_score(p, threshold_good, threshold_bad):
    """0mm = 10. > threshold_bad = 0."""
    if p is None:
        return 5.0
    if p <= threshold_good:
        return 10.0
    if p >= threshold_bad:
        return 0.0
    return max(0, 10.0 * (threshold_bad - p) / (threshold_bad - threshold_good))


def _sky_score(sky):
    """Cielo: despejado=10, tormenta=0."""
    if sky is None:
        return 5.0
    s = sky.upper()
    MAP = {
        "CLEAR": 10, "SUNNY": 10, "HIGH_CLOUDS": 9, "PARTLY_CLOUDY": 8,
        "CLOUDY": 5, "OVERCAST": 4, "FOG": 2, "DRIZZLE": 2, "WEAK_SHOWERS": 3,
        "SHOWERS": 1, "OVERCAST_AND_SHOWERS": 1, "RAIN": 1, "STORM": 0, "SNOW": 0,
    }
    for key, val in MAP.items():
        if key in s:
            return float(val)
    return 5.0


# ══════════════════════════════════════════════════════════════════════════════
# Perfiles por deporte
# ══════════════════════════════════════════════════════════════════════════════

SPORTS = {
    "running": {
        "label": "🏃 Running",
        "weights": {"temp": 0.30, "wind": 0.25, "precip": 0.30, "sky": 0.15},
        "temp":   {"ideal_min": 10, "ideal_max": 20, "abs_min": -2, "abs_max": 40},
        "wind":   {"ideal_min": 0,  "ideal_max": 15, "abs_min": 0,  "abs_max": 45},
        "precip": {"good": 0.5, "bad": 10},
    },
    "cycling": {
        "label": "🚴 Ciclismo ruta",
        "weights": {"temp": 0.25, "wind": 0.30, "precip": 0.30, "sky": 0.15},
        "temp":   {"ideal_min": 15, "ideal_max": 25, "abs_min": 2,  "abs_max": 40},
        "wind":   {"ideal_min": 0,  "ideal_max": 20, "abs_min": 0,  "abs_max": 55},
        "precip": {"good": 0.2, "bad": 5},
    },
    "mtb": {
        "label": "🚵 MTB",
        "weights": {"temp": 0.25, "wind": 0.20, "precip": 0.35, "sky": 0.20},
        "temp":   {"ideal_min": 10, "ideal_max": 22, "abs_min": 0,  "abs_max": 38},
        "wind":   {"ideal_min": 0,  "ideal_max": 25, "abs_min": 0,  "abs_max": 60},
        "precip": {"good": 1.0, "bad": 15},
    },
}

LABELS = [
    (8.0, "Perfecto"),
    (6.0, "Bueno"),
    (4.0, "Aceptable"),
    (2.0, "Malo"),
    (0.0, "No recomendado"),
]


def _get_label(score):
    for threshold, lbl in LABELS:
        if score >= threshold:
            return lbl
    return "No recomendado"


# ══════════════════════════════════════════════════════════════════════════════
# Cálculo principal
# ══════════════════════════════════════════════════════════════════════════════

def compute_iad(weather_rows: list[dict], sport: str) -> list[dict]:
    """
    Calcula IAD para un deporte dado.
    Devuelve lista con: time, coord_index, lon, lat, sport, score, label, details.
    """
    cfg = SPORTS.get(sport)
    if not cfg:
        raise ValueError(f"Deporte desconocido: {sport}")

    w = cfg["weights"]
    iad_rows = []

    for r in weather_rows:
        ts = _score_range(r.get("temperature"), **cfg["temp"])
        ws = _score_range(r.get("wind_speed"),  **cfg["wind"])
        ps = _precip_score(r.get("precipitation"), cfg["precip"]["good"], cfg["precip"]["bad"])
        ss = _sky_score(r.get("sky_state"))

        score = round(
            ts * w["temp"] + ws * w["wind"] + ps * w["precip"] + ss * w["sky"], 2
        )
        score = max(0.0, min(10.0, score))

        iad_rows.append({
            "time": r["time"],
            "coord_index": r["coord_index"],
            "lon": r.get("lon"),
            "lat": r.get("lat"),
            "sport": sport,
            "score": score,
            "label": _get_label(score),
            "details": {
                "temp_score": round(ts, 2), "wind_score": round(ws, 2),
                "precip_score": round(ps, 2), "sky_score": round(ss, 2),
                "temp": r.get("temperature"), "wind": r.get("wind_speed"),
                "precip": r.get("precipitation"), "sky": r.get("sky_state"),
            },
        })

    log.info("[IAD] %s → %d scores", sport, len(iad_rows))
    return iad_rows


def compute_all_sports(weather_rows: list[dict]) -> list[dict]:
    """Calcula IAD para todos los deportes. Devuelve lista combinada."""
    all_rows = []
    for sport in SPORTS:
        all_rows.extend(compute_iad(weather_rows, sport))
    log.info("[IAD] Total %d scores (%d deportes)", len(all_rows), len(SPORTS))
    return all_rows
