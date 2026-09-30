-- db/schema.sql
-- Инициализация схемы БД для авиатрекера

-- Таблица стран с границами координат (bounding box)
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(10),
    lamin DOUBLE PRECISION NOT NULL,
    lamax DOUBLE PRECISION NOT NULL,
    lomin DOUBLE PRECISION NOT NULL,
    lomax DOUBLE PRECISION NOT NULL
);

-- Таблица текущих данных о воздушных судах
CREATE TABLE IF NOT EXISTS aircrafts (
    id SERIAL PRIMARY KEY,
    icao24 VARCHAR(24) NOT NULL,
    callsign VARCHAR(64),
    origin_country VARCHAR(255),
    current_country_code VARCHAR(10),
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

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_aircrafts_callsign ON aircrafts(callsign);
CREATE INDEX IF NOT EXISTS idx_aircrafts_velocity ON aircrafts(velocity);
CREATE INDEX IF NOT EXISTS idx_aircrafts_current_country ON aircrafts(current_country_code);
