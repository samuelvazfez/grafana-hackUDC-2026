-- OBSERVACIONES METEOROLÓGICAS (AEMET)
-- Endpoint: /api/observacion/convencional/todas
CREATE TABLE IF NOT EXISTS raw_aemet.observaciones (
    ts_ingested TIMESTAMPTZ NOT NULL DEFAULT NOW(),
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
SELECT create_hypertable('raw_aemet.observaciones', 'ts_ingested', if_not_exists => TRUE);

-- AVISOS METEOROLÓGICOS CAP (AEMET)
-- Endpoint: /api/avisos_cap/ultimoelaborado/area/{area}
CREATE TABLE IF NOT EXISTS raw_aemet.avisos (
    ts_ingested TIMESTAMPTZ NOT NULL DEFAULT NOW(),
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
SELECT create_hypertable('raw_aemet.avisos', 'ts_ingested', if_not_exists => TRUE);
