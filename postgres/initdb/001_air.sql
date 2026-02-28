-- 001_air.sql
-- Datos de Calidad del Aire, Previsión Horaria y Polen (Open-Meteo)

-- ─── Calidad del Aire ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS raw_air.quality (
    time TIMESTAMPTZ NOT NULL,
    lat NUMERIC NOT NULL,
    lon NUMERIC NOT NULL,
    coord_index SMALLINT,
    european_aqi NUMERIC,
    pm10 NUMERIC,
    pm2_5 NUMERIC,
    uv_index NUMERIC,
    ts_ingested TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SELECT create_hypertable('raw_air.quality', 'time', if_not_exists => TRUE);

-- ─── Previsión Horaria (Open-Meteo Forecast) ────────────────────────────────
CREATE TABLE IF NOT EXISTS raw_air.forecast (
    time TIMESTAMPTZ NOT NULL,
    lat NUMERIC NOT NULL,
    lon NUMERIC NOT NULL,
    coord_index SMALLINT,
    temperature NUMERIC,
    apparent_temperature NUMERIC,
    precipitation_probability NUMERIC,
    precipitation NUMERIC,
    wind_speed NUMERIC,
    wind_gusts NUMERIC,
    visibility NUMERIC,
    cloud_cover NUMERIC,
    is_day SMALLINT,
    ts_ingested TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SELECT create_hypertable('raw_air.forecast', 'time', if_not_exists => TRUE);

-- ─── Polen (Open-Meteo Air Quality) ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS raw_air.pollen (
    time TIMESTAMPTZ NOT NULL,
    lat NUMERIC NOT NULL,
    lon NUMERIC NOT NULL,
    coord_index SMALLINT,
    grass_pollen NUMERIC,
    birch_pollen NUMERIC,
    olive_pollen NUMERIC,
    alder_pollen NUMERIC,
    ragweed_pollen NUMERIC,
    ts_ingested TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SELECT create_hypertable('raw_air.pollen', 'time', if_not_exists => TRUE);
