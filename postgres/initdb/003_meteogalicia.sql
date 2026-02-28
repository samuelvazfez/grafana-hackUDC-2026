-- 003_meteogalicia.sql
-- Esquema y tablas para MeteoGalicia (MeteoSIX v5)

CREATE SCHEMA IF NOT EXISTS meteogalicia;

-- ─── Tabla RAW ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS meteogalicia.raw_weather (
    ts_ingested  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    endpoint     TEXT        NOT NULL,
    coords_batch TEXT        NOT NULL,
    payload      JSONB       NOT NULL
);
SELECT create_hypertable(
    'meteogalicia.raw_weather', 'ts_ingested',
    if_not_exists => TRUE
);

-- ─── Tabla DERIVADA: previsión tidy por coordenada × hora ─────────────────────
-- Particionada por 'time' (hora de previsión):
--   UNIQUE(time, coord_index) incluye la columna de partición → OK TimescaleDB
CREATE TABLE IF NOT EXISTS meteogalicia.weather_hourly (
    ts_ingested       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    time              TIMESTAMPTZ NOT NULL,
    coord_index       SMALLINT    NOT NULL,
    lon               NUMERIC(9,6),
    lat               NUMERIC(9,6),
    temperature       NUMERIC(5,2),
    wind_speed        NUMERIC(6,2),
    wind_direction    NUMERIC(5,1),
    precipitation     NUMERIC(7,2),
    sky_state         TEXT,
    raw               JSONB
);
SELECT create_hypertable(
    'meteogalicia.weather_hourly', 'ts_ingested',
    if_not_exists => TRUE
);

-- ─── Tabla IAD Multi-deporte: score por coordenada × hora × deporte ──────────
CREATE TABLE IF NOT EXISTS meteogalicia.iad_scores (
    ts_ingested  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    time         TIMESTAMPTZ NOT NULL,
    coord_index  SMALLINT    NOT NULL,
    sport        TEXT        NOT NULL,
    lon          NUMERIC(9,6),
    lat          NUMERIC(9,6),
    score        NUMERIC(4,2),
    label        TEXT,
    details      JSONB
);
SELECT create_hypertable(
    'meteogalicia.iad_scores', 'ts_ingested',
    if_not_exists => TRUE
);
