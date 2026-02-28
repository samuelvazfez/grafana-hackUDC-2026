"""
Ingestor principal — Orquesta fetchers, parsers, IAD y escritura a BD.
MeteoSIX (cada POLL_METEOSIX_SECONDS) + AEMET (cada POLL_AEMET_SECONDS).
"""
import time
import logging

from psycopg2.extras import Json, execute_values

from config import (
    METEOSIX_COORDS, POLL_METEOSIX_SECONDS, POLL_AEMET_SECONDS,
    AEMET_API_KEY,
)
from cache import ensure_cache_dir
from db import get_conn
from fetchers.meteosix import fetch_meteosix
from fetchers.aemet import fetch_aemet_observaciones, fetch_aemet_avisos
from parsers.meteosix import parse_meteosix
from parsers.aemet import parse_aemet_observaciones
from iad import compute_iad_running

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

# ── DB helpers ────────────────────────────────────────────────────────────────

def insert_raw_weather(conn, endpoint, coords_batch, payload):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO meteogalicia.raw_weather
               (ts_ingested, endpoint, coords_batch, payload)
               VALUES (NOW(), %s, %s, %s)""",
            (endpoint, coords_batch, Json(payload)),
        )
    conn.commit()


_INSERT_WEATHER = """
INSERT INTO meteogalicia.weather_hourly
    (time, coord_index, lon, lat, temperature, wind_speed,
     wind_direction, precipitation, sky_state, raw)
VALUES %s
"""

def insert_weather(conn, rows):
    if not rows:
        return 0
    vals = [
        (r["time"], r["coord_index"], r["lon"], r["lat"],
         r["temperature"], r["wind_speed"], r["wind_direction"],
         r["precipitation"], r["sky_state"],
         Json(r["raw"]) if r.get("raw") else None)
        for r in rows
    ]
    with conn.cursor() as cur:
        execute_values(cur, _INSERT_WEATHER, vals)
    conn.commit()
    return len(vals)


_INSERT_IAD = """
INSERT INTO meteogalicia.iad_running
    (time, coord_index, lon, lat, score, label, details)
VALUES %s
"""

def insert_iad(conn, rows):
    if not rows:
        return 0
    vals = [
        (r["time"], r["coord_index"], r["lon"], r["lat"],
         r["score"], r["label"],
         Json(r["details"]) if r.get("details") else None)
        for r in rows
    ]
    with conn.cursor() as cur:
        execute_values(cur, _INSERT_IAD, vals)
    conn.commit()
    return len(vals)


_UPSERT_AEMET_OBS = """
INSERT INTO raw_aemet.observaciones
    (ts_ingested, time, estacion_id, ubicacion,
     temperatura, humedad, precipitacion, viento_vel, viento_dir, raw_data)
VALUES %s
ON CONFLICT (time, estacion_id) DO UPDATE SET
    ubicacion=EXCLUDED.ubicacion, temperatura=EXCLUDED.temperatura,
    humedad=EXCLUDED.humedad, precipitacion=EXCLUDED.precipitacion,
    viento_vel=EXCLUDED.viento_vel, viento_dir=EXCLUDED.viento_dir,
    raw_data=EXCLUDED.raw_data
"""

def insert_aemet_obs(conn, rows):
    if not rows:
        return 0
    inserted = 0
    with conn.cursor() as cur:
        for r in rows:
            cur.execute(
                """INSERT INTO raw_aemet.observaciones
                   (time, estacion_id, ubicacion, temperatura, humedad,
                    precipitacion, viento_vel, viento_dir, raw_data)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (r["time"], r["estacion_id"], r["ubicacion"],
                 r["temperatura"], r["humedad"], r["precipitacion"],
                 r["viento_vel"], r["viento_dir"],
                 Json(r["raw_data"]) if r.get("raw_data") else None),
            )
            inserted += 1
    conn.commit()
    return inserted


# ── Ciclos de ingesta ─────────────────────────────────────────────────────────

def ingest_meteosix():
    """Fetch → parse → upsert weather + IAD."""
    payload = fetch_meteosix(METEOSIX_COORDS)
    rows = parse_meteosix(payload)
    iad_rows = compute_iad_running(rows)

    with get_conn() as conn:
        insert_raw_weather(conn, "getNumericForecastInfo", METEOSIX_COORDS, payload)
        n_w = insert_weather(conn, rows)
        n_i = insert_iad(conn, iad_rows)

    log.info("[MeteoSIX] raw + %d weather + %d IAD insertados", n_w, n_i)


def ingest_aemet():
    """Fetch observaciones + avisos → parse → upsert."""
    if not AEMET_API_KEY:
        log.info("[AEMET] Sin API key, saltando")
        return

    obs_data = fetch_aemet_observaciones()
    obs_rows = parse_aemet_observaciones(obs_data)

    with get_conn() as conn:
        n = insert_aemet_obs(conn, obs_rows)
    log.info("[AEMET] %d observaciones insertadas", n)

    # Avisos (por ahora solo log)
    avisos = fetch_aemet_avisos()
    log.info("[AEMET] %d avisos recibidos", len(avisos) if avisos else 0)


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    ensure_cache_dir()

    coords_list = [c for c in METEOSIX_COORDS.split(";") if c.strip()]
    if not coords_list:
        raise RuntimeError("METEOSIX_COORDS vacío")
    if len(coords_list) > 20:
        raise RuntimeError(f"Demasiados puntos ({len(coords_list)}). Máx 20.")

    log.info("=== INGESTOR INICIADO ===")
    log.info("MeteoSIX: %d coords, poll %ds", len(coords_list), POLL_METEOSIX_SECONDS)
    log.info("AEMET: %s, poll %ds", "activo" if AEMET_API_KEY else "SIN API KEY", POLL_AEMET_SECONDS)

    last_meteosix = 0
    last_aemet = 0

    while True:
        now = time.time()

        # MeteoSIX
        if now - last_meteosix >= POLL_METEOSIX_SECONDS:
            try:
                ingest_meteosix()
            except Exception:
                log.exception("Error en ingesta MeteoSIX")
            last_meteosix = time.time()

        # AEMET
        if now - last_aemet >= POLL_AEMET_SECONDS:
            try:
                ingest_aemet()
            except Exception:
                log.exception("Error en ingesta AEMET")
            last_aemet = time.time()

        # Dormir 60s entre comprobaciones
        time.sleep(60)


if __name__ == "__main__":
    main()