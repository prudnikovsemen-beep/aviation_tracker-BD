"""Инициализация схемы базы данных: создание таблиц."""

import psycopg2
from psycopg2 import OperationalError
from typing import Dict, Any


class DBInitializer:
    """Создаёт таблицы в PostgreSQL, если их нет."""

    def __init__(self, db_config: Dict[str, Any]):
        """
        Args:
            db_config: Словарь с параметрами подключения.
        """
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
        """Создаёт таблицы countries и aircrafts, если они не существуют."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # Таблица стран
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS countries (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        code CHAR(2) NOT NULL,
                        lamin DOUBLE PRECISION NOT NULL,
                        lamax DOUBLE PRECISION NOT NULL,
                        lomin DOUBLE PRECISION NOT NULL,
                        lomax DOUBLE PRECISION NOT NULL
                    );
                """)

                # Таблица самолётов
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS aircrafts (
                        id SERIAL PRIMARY KEY,
                        icao24 VARCHAR(8) NOT NULL,
                        callsign VARCHAR(20),
                        origin_country VARCHAR(100),
                        latitude DOUBLE PRECISION,
                        longitude DOUBLE PRECISION,
                        velocity DOUBLE PRECISION,
                        baro_altitude DOUBLE PRECISION,
                        on_ground BOOLEAN NOT NULL,
                        true_track DOUBLE PRECISION,
                        vertical_rate DOUBLE PRECISION
                    );
                """)
            conn.commit()
            print("✅ Таблицы успешно созданы или уже существуют.")
        except Exception as e:
            conn.rollback()
            print(f"❌ Ошибка при создании таблиц: {e}")
            raise
        finally:
            conn.close()
