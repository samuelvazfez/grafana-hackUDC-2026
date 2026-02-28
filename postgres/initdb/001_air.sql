CREATE TABLE IF NOT EXISTS raw_air.test (
  ts_ingested TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  test TEXT NOT NULL,
);
SELECT create_hypertable('raw_air.test', 'ts_ingested', if_not_exists => TRUE);
