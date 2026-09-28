"""Инициализация схемы базы данных: создание таблиц."""

import psycopg2
from psycopg2 import OperationalError
from typing import Dict, Any


class DBInitializer:
    """Создаёт таблицы в PostgreSQL, полностью пересоздавая их для гарантии ограничений."""

    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config

    def _get_connection(self):
        try:
            conn = psycopg2.connect(
                host=self.db_config["host"],
                port=int(self.db_config["port"]),
                dbname=self.db_config["dbname"],
                user=self.db_config["user"],
                password=self.db_config["password"],
            )
            return conn
        except OperationalError as e:
            print(f"Ошибка подключения к БД: {e}")
            raise

    def create_tables(self) -> None:
        """Удаляет старые таблицы и создаёт новые с UNIQUE ограничениями."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # 1. Удаляем старые таблицы (гарантируем чистый старт)
                cur.execute("DROP TABLE IF EXISTS aircrafts CASCADE;")
                cur.execute("DROP TABLE IF EXISTS countries CASCADE;")

                # 2. Создаём countries (с UNIQUE на name)
                cur.execute("""
                    CREATE TABLE countries (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        code CHAR(2) NOT NULL,
                        lamin DOUBLE PRECISION NOT NULL,
                        lamax DOUBLE PRECISION NOT NULL,
                        lomin DOUBLE PRECISION NOT NULL,
                        lomax DOUBLE PRECISION NOT NULL
                    );
                """)

                # 3. Создаём aircrafts (с UNIQUE на icao24)
                cur.execute("""
                    CREATE TABLE aircrafts (
                        id SERIAL PRIMARY KEY,
                        icao24 VARCHAR(8) NOT NULL UNIQUE,
                        callsign VARCHAR(20),
                        origin_country VARCHAR(100),
                        latitude DOUBLE PRECISION,
                        longitude DOUBLE PRECISION,
                        velocity DOUBLE PRECISION,
                        baro_altitude DOUBLE PRECISION,
                        on_ground BOOLEAN NOT NULL DEFAULT FALSE,
                        true_track DOUBLE PRECISION,
                        vertical_rate DOUBLE PRECISION
                    );
                """)

            conn.commit()
            print("✅ Таблицы успешно пересозданы с уникальными ограничениями.")

        except Exception as e:
            conn.rollback()
            print(f"❌ Ошибка при создании таблиц: {e}")
            raise
        finally:
            conn.close()
