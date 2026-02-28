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