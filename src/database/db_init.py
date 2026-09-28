"""Модуль для инициализации схемы БД (создание таблиц)."""

from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor


def init_database(conn_params: dict) -> None:
    """
    Создаёт таблицы countries и aircrafts, если их ещё нет.

    Выполняет DDL-запросы для создания структуры БД согласно требованиям курсовой.
    Также создаёт индексы для ускорения поиска по callsign и скорости.

    Args:
        conn_params (dict): Параметры подключения к БД: host, port, dbname, user, password.
    """
    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        with conn.cursor() as cur:
            # Таблица countries
            cur.execute("""
                CREATE TABLE IF NOT EXISTS countries (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    code VARCHAR(10),
                    lamin DOUBLE PRECISION NOT NULL,
                    lamax DOUBLE PRECISION NOT NULL,
                    lomin DOUBLE PRECISION NOT NULL,
                    lomax DOUBLE PRECISION NOT NULL
                );
            """)

            # Таблица aircrafts
            cur.execute("""
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
            """)

            # Индексы
            cur.execute("CREATE INDEX IF NOT EXISTS idx_aircrafts_callsign ON aircrafts(callsign);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_aircrafts_velocity ON aircrafts(velocity);")

        conn.commit()
    finally:
        if conn is not None:
            conn.close()
