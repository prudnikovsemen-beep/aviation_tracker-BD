-- db/schema.sql
-- Инициализация схемы БД для авиатрекера

CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(10),
    lat_min DOUBLE PRECISION NOT NULL,
    lat_max DOUBLE PRECISION NOT NULL,
    lon_min DOUBLE PRECISION NOT NULL,
    lon_max DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS aircrafts (
    id SERIAL PRIMARY KEY,
    icao24 VARCHAR(24) NOT NULL,
    callsign VARCHAR(64),
    origin_country VARCHAR(255),
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    baro_altitude DOUBLE PRECISION,
    on_ground BOOLEAN NOT NULL DEFAULT FALSE,
    velocity DOUBLE PRECISION,
    true_track DOUBLE PRECISION,
    vertical_rate DOUBLE PRECISION,
    last_seen TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_aircrafts_callsign ON aircrafts(callsign);
CREATE INDEX IF NOT EXISTS idx_aircrafts_velocity ON aircrafts(velocity);
CREATE INDEX IF NOT EXISTS idx_aircrafts_icao24 ON aircrafts(icao24);
