-- 005_grafana_user.sql
-- Usuario solo-lectura para Grafana

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'grafanareader') THEN
        CREATE ROLE grafanareader LOGIN PASSWORD 'grafana_readonly';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE observability TO grafanareader;

-- Esquema meteogalicia
GRANT USAGE ON SCHEMA meteogalicia TO grafanareader;
GRANT SELECT ON ALL TABLES IN SCHEMA meteogalicia TO grafanareader;
ALTER DEFAULT PRIVILEGES IN SCHEMA meteogalicia GRANT SELECT ON TABLES TO grafanareader;

-- Esquema raw_aemet
GRANT USAGE ON SCHEMA raw_aemet TO grafanareader;
GRANT SELECT ON ALL TABLES IN SCHEMA raw_aemet TO grafanareader;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw_aemet GRANT SELECT ON TABLES TO grafanareader;


-- Esquema raw_air
GRANT USAGE ON SCHEMA raw_air TO grafanareader;
GRANT SELECT ON ALL TABLES IN SCHEMA raw_air TO grafanareader;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw_air GRANT SELECT ON TABLES TO grafanareader;

-- Esquema public
GRANT USAGE ON SCHEMA public TO grafanareader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafanareader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO grafanareader;
