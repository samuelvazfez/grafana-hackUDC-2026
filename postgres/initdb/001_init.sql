-- 001_init.sql

-- Extensión de Time Series
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Esquema lógico (opcional)
CREATE SCHEMA IF NOT EXISTS public;

-- Usuario de solo lectura para Grafana
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT FROM pg_catalog.pg_roles WHERE rolname = '${GRAFANA_DB_USER}'
  ) THEN
    CREATE ROLE ${GRAFANA_DB_USER} LOGIN PASSWORD '${GRAFANA_DB_PASSWORD}';
  END IF;
END$$;

-- Permisos mínimos recomendados para Grafana (solo SELECT)
GRANT USAGE ON SCHEMA public TO ${GRAFANA_DB_USER};
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ${GRAFANA_DB_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ${GRAFANA_DB_USER};

-- (Opcional) Tabla de ejemplo con hypertable
CREATE TABLE IF NOT EXISTS sensor_example (
  time TIMESTAMPTZ NOT NULL,
  metric TEXT NOT NULL,
  value DOUBLE PRECISION NOT NULL
);

SELECT create_hypertable('sensor_example', by_range('time'), if_not_exists => TRUE);

-- (Opcional) Política de retención sobre la tabla de ejemplo
-- SELECT add_retention_policy('sensor_example', INTERVAL '30 days', if_not_exists => TRUE);
``