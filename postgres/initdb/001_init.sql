-- 001_init.sql

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS raw_weather (
  ts_ingested TIMESTAMPTZ NOT NULL,
  endpoint TEXT NOT NULL,
  coords_batch TEXT NOT NULL,
  payload JSONB NOT NULL
);

SELECT create_hypertable('raw_weather', 'ts_ingested', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_raw_weather_ts
  ON raw_weather (ts_ingested DESC);

-- Tabla de ejemplo (opcional)
CREATE TABLE IF NOT EXISTS sensor_example (
  time TIMESTAMPTZ NOT NULL,
  metric TEXT NOT NULL,
  value DOUBLE PRECISION NOT NULL
);

SELECT create_hypertable('sensor_example', 'time', if_not_exists => TRUE);

-- ==========================================
-- TABLA 1: OBSERVACIONES METEOROLÓGICAS (AEMET)
-- Endpoint: /api/observacion/convencional/todas
-- ==========================================CREATE TABLE IF NOT EXISTS sensor_example (
CREATE TABLE IF NOT EXISTS aemet_observaciones (
    id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL,           -- Fecha y hora del dato (fint)
    estacion_id VARCHAR(50) NOT NULL,    -- ID de la estación (idema)
    ubicacion VARCHAR(255),              -- Nombre de la ubicación (ubi)
    temperatura NUMERIC,                 -- Temperatura actual (ta)
    humedad NUMERIC,                     -- Humedad relativa (hr)
    precipitacion NUMERIC,               -- Precipitación (prec)
    viento_vel NUMERIC,                  -- Velocidad del viento (vv)
    viento_dir NUMERIC,                  -- Dirección del viento (dv)
    raw_data JSONB                       -- Guardamos el JSON completo por si acaso
);


-- Índices para que Grafana cargue rápido
CREATE INDEX IF NOT EXISTS ix_aemet_obs_time ON aemet_observaciones (time DESC);
CREATE INDEX IF NOT EXISTS ix_aemet_obs_estacion ON aemet_observaciones (estacion_id, time DESC);


-- ==========================================
-- TABLA 2: AVISOS METEOROLÓGICOS CAP (AEMET)
-- Endpoint: /api/avisos_cap/ultimoelaborado/area/{area}
-- ==========================================
CREATE TABLE IF NOT EXISTS aemet_avisos (
    id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL,           -- Cuándo se registró en tu BD
    area VARCHAR(100) NOT NULL,          -- Área consultada
    tipo_aviso VARCHAR(100),             -- Ej: 'Lluvias', 'Viento'
    severidad VARCHAR(50),               -- Ej: 'Amarillo', 'Naranja'
    inicio_aviso TIMESTAMPTZ,            -- Inicio del peligro
    fin_aviso TIMESTAMPTZ,               -- Fin del peligro
    descripcion TEXT,                    -- Descripción del aviso
    instrucciones TEXT                   -- Recomendaciones a la población
);


-- Índices para búsqueda de avisos
CREATE INDEX IF NOT EXISTS ix_aemet_avisos_time ON aemet_avisos (time DESC);
CREATE INDEX IF NOT EXISTS ix_aemet_avisos_rango ON aemet_avisos (inicio_aviso, fin_aviso);
CREATE INDEX IF NOT EXISTS ix_aemet_avisos_area ON aemet_avisos (area);
