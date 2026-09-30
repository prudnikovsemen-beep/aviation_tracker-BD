"""Менеджер базы данных для работы с PostgreSQL."""

import psycopg2
from psycopg2 import OperationalError
from typing import List, Dict, Optional, Any
from psycopg2.extensions import connection

from src.models.country import Country
from src.models.aircraft import Aircraft


class DBManager:
    """Подключается к PostgreSQL и выполняет CRUD-операции."""

    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config

    def _get_connection(self) -> connection:
        """Возвращает активное соединение с БД."""
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

    # --- Сохранение данных ---
    def save_country(self, country: Country) -> None:
        """Сохраняет страну в таблицу countries. Если страна уже есть — обновляет координаты."""
        query = """
            INSERT INTO countries (name, code, lamin, lamax, lomin, lomax)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET
                lamin = EXCLUDED.lamin,
                lamax = EXCLUDED.lamax,
                lomin = EXCLUDED.lomin,
                lomax = EXCLUDED.lomax;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (country.name, country.code, country.lamin, country.lamax, country.lomin, country.lomax),
                )
            conn.commit()

    def save_aircraft(self, aircraft: Aircraft) -> None:
        """Сохраняет самолёт в таблицу aircrafts. Обновляет, если icao24 уже есть."""
        query = """
            INSERT INTO aircrafts (icao24, callsign, origin_country, current_country_code,
                                   latitude, longitude, velocity, baro_altitude,
                                   on_ground, true_track, vertical_rate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (icao24) DO UPDATE SET
                callsign = EXCLUDED.callsign,
                origin_country = EXCLUDED.origin_country,
                current_country_code = EXCLUDED.current_country_code,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                velocity = EXCLUDED.velocity,
                baro_altitude = EXCLUDED.baro_altitude,
                on_ground = EXCLUDED.on_ground,
                true_track = EXCLUDED.true_track,
                vertical_rate = EXCLUDED.vertical_rate;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        aircraft.icao24,
                        aircraft.callsign,
                        aircraft.origin_country,
                        aircraft.current_country_code,
                        aircraft.latitude,
                        aircraft.longitude,
                        aircraft.velocity,
                        aircraft.baro_altitude,
                        aircraft.on_ground,
                        aircraft.true_track,
                        aircraft.vertical_rate,
                    ),
                )
            conn.commit()

    # --- Определение страны по координатам ---
    def get_country_code_by_coords(self, latitude: Optional[float], longitude: Optional[float]) -> Optional[str]:
        """
        Определяет код страны по координатам самолёта.
        Проверяет, в какой bounding box страны попадают координаты.

        Args:
            latitude (Optional[float]): Широта самолёта.
            longitude (Optional[float]): Долгота самолёта.

        Returns:
            Optional[str]: Код страны (например, 'RU') или None, если координаты
                           не попадают ни в одну страну из справочника.
        """
        if latitude is None or longitude is None:
            return None

        query = """
            SELECT code FROM countries
            WHERE lamin <= %s AND lamax >= %s
              AND lomin <= %s AND lomax >= %s
            LIMIT 1;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (latitude, latitude, longitude, longitude))
                row = cur.fetchone()
                return row[0] if row else None

    # --- Получение данных (по заданию) ---
    def get_countries_and_aeroplanes_count(self) -> List[Dict[str, Any]]:
        """
        Получает список всех стран и количество самолётов в их воздушных пространствах.
        Связь выполняется по полю current_country_code (страна, в границах которой
        находится самолёт), а не по origin_country (страна регистрации).

        Returns:
            List[Dict[str, Any]]: Список словарей вида
            [{"country_name": "Россия", "aircraft_count": 12}, ...],
            отсортированный по убыванию количества самолётов.
        """
        query = """
            SELECT c.name AS country_name, COUNT(a.id) AS aircraft_count
            FROM countries c
            LEFT JOIN aircrafts a ON c.code = a.current_country_code
            GROUP BY c.id, c.name
            ORDER BY aircraft_count DESC;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                assert cur.description is not None
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]

    def get_all_aeroplanes(self) -> List[Dict[str, Any]]:
        """Получает список всех воздушных судов."""
        query = "SELECT * FROM aircrafts;"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                assert cur.description is not None
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]

    def get_avg_speed(self) -> Optional[float]:
        """Получает среднюю скорость по самолётам."""
        query = "SELECT AVG(velocity) FROM aircrafts WHERE velocity IS NOT NULL;"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchone()
                return result[0] if result and result[0] is not None else None

    def get_aeroplanes_with_higher_speed(self) -> List[Dict[str, Any]]:
        """Получает список самолётов, у которых скорость выше средней."""
        avg = self.get_avg_speed()
        if avg is None:
            return []

        query = "SELECT * FROM aircrafts WHERE velocity > %s;"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (avg,))
                assert cur.description is not None
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]

    def get_aeroplanes_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Получает самолёты, в позывном которых есть заданные символы."""
        search_pattern = f"%{keyword}%"
        query = "SELECT * FROM aircrafts WHERE callsign ILIKE %s LIMIT 20;"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (search_pattern,))
                assert cur.description is not None
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]

    def get_connection(self) -> connection:
        """Публичный метод для получения соединения (удобно для тестов)."""
        return self._get_connection()

    def get_country_by_name(self, name: str) -> Optional[Country]:
        """Возвращает страну по имени или None, если не найдена."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name, code, lamin, lamax, lomin, lomax FROM countries WHERE name = %s", (name,))
                row = cur.fetchone()
                if row:
                    return Country(name=row[0], code=row[1], lamin=row[2], lamax=row[3], lomin=row[4], lomax=row[5])
                return None
