-- 000_setup.sql
-- Archivo de configuración inicial de la base de datos y extensiones

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Crear esquemas lógicos para separar los datos por API / origen
CREATE SCHEMA IF NOT EXISTS raw_air;
CREATE SCHEMA IF NOT EXISTS raw_aemet;
